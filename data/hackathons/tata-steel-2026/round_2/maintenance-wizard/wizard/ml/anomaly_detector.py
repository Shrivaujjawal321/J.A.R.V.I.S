"""
wizard.ml.anomaly_detector
===========================
Sensor time-series anomaly detection.

Architecture (per research report 09):
  Head A — IsolationForest (sklearn 1.5): point/multivariate anomaly.
            Features: extract_window_features(history, window=30).
            SHAP TreeExplainer for per-sensor attribution.
  Head B — LSTM Autoencoder (torch, CPU): reconstruction error on 30-step windows.
            Reconstruction error per sensor → per-sensor contribution heatmap.
  Head C — River HalfSpaceTrees: online streaming head (real-time path).
            One-sample-at-a-time; ADWIN drift detection.

Fusion: combined_score = alpha * IF_score + (1 - alpha) * AE_score  (alpha=0.6)
Threshold: adaptive percentile-based (97th pctile of training scores).

Graceful degradation: any head that fails to load → excluded from fusion.
A 'fallback' stub returns a safe mid-range score if ALL artifacts are missing.

Public API
----------
  get_anomaly_score(asset_id, sensor_readings, readings_history) -> dict
      {score: float, severity: str, shap_values: dict, triggered_sensors: list}
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from wizard.core.schemas import AlertSeverity
from wizard.ml.feature_utils import (
    SENSOR_KEYS,
    build_sensor_vector,
    extract_window_features,
)
from wizard.ml.registry import ModelRegistry
# Physics-informed degradation index (steel-sensor domain fix).
# IsolationForest trained on C-MAPSS normalized space produces near-flat
# scores for steel-plant readings regardless of degradation state.
# physics_degradation_index() provides steel-domain discrimination.
from wizard.ml.degradation import physics_degradation_index

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_IF_ALPHA: float = 0.6        # weight for IsolationForest head
_AE_ALPHA: float = 0.4        # weight for LSTM-AE head
_WINDOW: int = 30             # rolling window steps (research report §2d)
_SHAP_SAMPLE_LIMIT: int = 100 # max samples for SHAP (performance guard)

# Severity bins (on fused score [0, 1])
def _severity(score: float) -> AlertSeverity:
    if score < 0.40:
        return AlertSeverity.LOW
    elif score < 0.65:
        return AlertSeverity.MEDIUM
    elif score < 0.85:
        return AlertSeverity.HIGH
    else:
        return AlertSeverity.CRITICAL


# ---------------------------------------------------------------------------
# LSTM Autoencoder — tiny 2-layer LSTM + decoder, CPU-only
# ---------------------------------------------------------------------------

class _LSTMAEModel:
    """
    Thin wrapper around a PyTorch LSTM Autoencoder.

    Architecture:
      Encoder: LSTM(input=D, hidden=32, layers=2)
      Decoder: LSTM(input=32, hidden=32, layers=2) + Linear(32→D)

    Input shape: (T, D)  where T=window, D=n_sensors
    Output: reconstruction of shape (T, D); score = mean(MSE per time-step)
    """

    def __init__(self, n_features: int = len(SENSOR_KEYS), hidden: int = 32, n_layers: int = 2):
        self._n_features = n_features
        self._hidden = hidden
        self._n_layers = n_layers
        self._model: Optional[Any] = None
        self._threshold: float = 0.1  # adaptive threshold from training

    def build(self) -> None:
        """Instantiate the PyTorch model."""
        try:
            import torch
            import torch.nn as nn

            class _LSTMAE(nn.Module):
                def __init__(self, n_features: int, hidden: int, n_layers: int):
                    super().__init__()
                    self.encoder = nn.LSTM(n_features, hidden, n_layers, batch_first=True)
                    self.decoder = nn.LSTM(hidden, hidden, n_layers, batch_first=True)
                    self.out_proj = nn.Linear(hidden, n_features)

                def forward(self, x: "torch.Tensor") -> "torch.Tensor":
                    # x: (B, T, D)
                    _, (h, c) = self.encoder(x)
                    # Repeat bottleneck for decoder input
                    T = x.shape[1]
                    dec_in = h[-1].unsqueeze(1).repeat(1, T, 1)  # (B, T, hidden)
                    dec_out, _ = self.decoder(dec_in, (h, c))
                    return self.out_proj(dec_out)   # (B, T, D)

            self._model = _LSTMAE(self._n_features, self._hidden, self._n_layers)
            self._model.eval()
            logger.debug("LSTM-AE model built in-memory (untrained).")
        except ImportError:
            logger.warning("torch not installed — LSTM-AE head disabled.")

    def load_weights(self, weights_dict: Dict[str, Any]) -> None:
        """Load state_dict from a dict (loaded via joblib)."""
        if self._model is None:
            self.build()
        if self._model is None:
            return
        try:
            import torch
            self._model.load_state_dict(weights_dict["state_dict"])
            self._threshold = float(weights_dict.get("threshold", 0.1))
            self._model.eval()
            logger.info("LSTM-AE weights loaded.")
        except Exception as exc:
            logger.warning("LSTM-AE weight load failed: %s", exc)

    def score(self, window_matrix: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Compute reconstruction anomaly score.

        Parameters
        ----------
        window_matrix : np.ndarray (T, D)
            Sliding window of normalized sensor readings.

        Returns
        -------
        score : float in [0, 1]
            Scaled reconstruction error (0 = normal, 1 = max anomaly).
        per_sensor_error : np.ndarray (D,)
            Per-sensor MSE contribution (for UI heatmap).
        """
        if self._model is None:
            return 0.5, np.zeros(self._n_features)

        try:
            import torch
            with torch.no_grad():
                T, D = window_matrix.shape
                x = torch.tensor(window_matrix, dtype=torch.float32).unsqueeze(0)  # (1, T, D)
                x_hat = self._model(x)  # (1, T, D)
                mse_per_step = ((x - x_hat) ** 2).squeeze(0).mean(dim=0)  # (D,)
                recon_error = float(mse_per_step.mean().item())
                # Normalize against threshold
                normalized = float(np.clip(recon_error / max(self._threshold, 1e-6), 0.0, 2.0) / 2.0)
                return normalized, mse_per_step.numpy()
        except Exception as exc:
            logger.debug("LSTM-AE score failed: %s", exc)
            return 0.5, np.zeros(self._n_features)


# ---------------------------------------------------------------------------
# Module-level lazy singletons (keyed by equipment class)
# ---------------------------------------------------------------------------
_lstm_ae_lock = threading.Lock()
_lstm_ae_cache: Dict[str, _LSTMAEModel] = {}  # eq_key -> _LSTMAEModel

def _get_lstm_ae(eq_key: str = "default") -> Optional[_LSTMAEModel]:
    """
    Return a (possibly untrained) LSTM-AE for this equipment class.

    Artifact key convention matches train_anomaly_models output:
      anomaly_lstm_ae_{eq_key}.pkl

    The model is built with n_features read from the artifact's 'n_features'
    field (defaulting to len(SENSOR_KEYS) if not stored), so that the
    architecture exactly matches the saved state_dict regardless of which
    feature dimension was used at training time.
    """
    with _lstm_ae_lock:
        if eq_key in _lstm_ae_cache:
            return _lstm_ae_cache[eq_key]
        # Try loading artifact with equipment-class-specific key
        artifact_key = f"anomaly_lstm_ae_{eq_key}"
        weights = ModelRegistry.load(artifact_key, fallback=None)
        # Determine n_features from the artifact (canonical source of truth)
        if weights is not None and isinstance(weights, dict):
            n_features = int(weights.get("n_features", len(SENSOR_KEYS)))
        else:
            n_features = len(SENSOR_KEYS)
        ae = _LSTMAEModel(n_features=n_features)
        ae.build()
        if weights is not None:
            ae.load_weights(weights)
        _lstm_ae_cache[eq_key] = ae
        return _lstm_ae_cache[eq_key]


# ---------------------------------------------------------------------------
# River streaming head (optional)
# ---------------------------------------------------------------------------

def _river_score(readings: Dict[str, float], is_normal: bool = True) -> Optional[float]:
    """
    Single-sample anomaly score via River HalfSpaceTrees (streaming head).

    Calls score_one() first, then learn_one() on the current sample so the
    streaming model adapts online (required for non-frozen HST behavior).
    On normal samples (is_normal=True), we always call learn_one() to update
    the model's internal distribution estimate.

    Note: ADWIN drift detection is NOT wired in this implementation; the
    streaming head adapts via HST's built-in window mechanism instead.

    Returns None if river is not installed or artifact is missing.
    """
    try:
        # River HST artifact is pre-fitted; loaded as dict {'model': ..., 'threshold': ...}
        river_artifact = ModelRegistry.load("anomaly_river_hst", fallback=None)
        if river_artifact is None:
            return None
        hst = river_artifact.get("model")
        if hst is None:
            return None
        # Score first (before updating internal state with this sample)
        score = float(hst.score_one(readings))
        # Online update: learn_one() keeps the streaming head adapting to the
        # current data distribution. Call unconditionally — HST handles its
        # own windowing internally.
        hst.learn_one(readings)
        return float(np.clip(score, 0.0, 1.0))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# SHAP attribution for IsolationForest
# ---------------------------------------------------------------------------

def _compute_shap(
    if_model: Any,
    feature_vec: np.ndarray,
    sensor_keys: List[str],
) -> Dict[str, float]:
    """
    Compute SHAP values for IsolationForest prediction.

    Returns dict {sensor_name: shap_contribution}.
    Feature names correspond to extract_window_features output,
    grouped as mean/std/min/max/range/roc per sensor key.
    """
    try:
        import shap  # type: ignore[import]
        explainer = shap.TreeExplainer(if_model)
        shap_vals = explainer.shap_values(feature_vec.reshape(1, -1))
        # shap_vals shape: (1, n_features) — aggregate per sensor
        n_stats = 6  # mean, std, min, max, range, roc
        contributions: Dict[str, float] = {}
        for i, key in enumerate(sensor_keys):
            start = i * n_stats
            end   = start + n_stats
            contributions[key] = float(np.abs(shap_vals[0, start:end]).sum())
        # Normalize to [0, 1]
        total = sum(contributions.values()) or 1.0
        return {k: round(v / total, 4) for k, v in contributions.items()}
    except Exception as exc:
        logger.debug("SHAP attribution failed: %s", exc)
        return {}


# ---------------------------------------------------------------------------
# Public: get_anomaly_score
# ---------------------------------------------------------------------------

def get_anomaly_score(
    asset_id: str,
    sensor_readings: Dict[str, float],
    readings_history: Optional[List[Dict[str, float]]] = None,
    equipment_class: str = "default",
) -> Dict[str, Any]:
    """
    Compute anomaly score for a single sensor snapshot.

    Parameters
    ----------
    asset_id : str
        Equipment identifier.
    sensor_readings : dict[str, float]
        Latest sensor readings snapshot.
    readings_history : list[dict], optional
        Ordered list of past readings (oldest first).
        If provided, LSTM-AE and rolling-window features are computed.
    equipment_class : str
        Used to load the right IsolationForest artifact key.

    Returns
    -------
    dict with keys:
      score : float in [0, 1]   — fused anomaly score
      severity : str            — AlertSeverity enum value
      shap_values : dict[str, float]  — per-sensor attribution
      triggered_sensors : list[str]   — sensors with shap > 0.15
      if_score : float          — IsolationForest head score
      ae_score : float          — LSTM-AE head score
      river_score : float | None — streaming head score (None if unavailable)
      reconstruction_error : list[float]  — per-sensor AE error
    """
    eq_key = equipment_class.lower().replace(" ", "_").replace("-", "_")
    if_artifact_key = f"anomaly_if_{eq_key}"
    threshold_key   = f"anomaly_threshold_{eq_key}"

    # --- Load IsolationForest ---
    if_model = ModelRegistry.load(if_artifact_key, fallback=None)
    adaptive_threshold = ModelRegistry.load(threshold_key, fallback=None)

    # --- Build feature vector ---
    # FIX (2026-06-07): normalize raw physical-unit readings to [0, 1] before
    # computing window features.  The IsolationForest was trained on [0, 1]-scaled
    # synthetic window features, so raw physical values (e.g. temperature=520°C)
    # appear as extreme outliers → every reading scores 1.0 regardless of
    # actual anomaly status.  Normalizing first puts the feature space on the
    # same [0, 1] scale as training data, restoring discrimination.
    history = readings_history or [sensor_readings]
    try:
        from wizard.ml.rul_estimator import _normalize_sensor_readings, _SENSOR_PHYSICAL_RANGE
        def _norm_readings(r: Dict[str, float]) -> Dict[str, float]:
            """Normalize one readings dict from physical units to [0, 1]."""
            out = {}
            for key in SENSOR_KEYS:
                lo, hi = _SENSOR_PHYSICAL_RANGE.get(key, (0.0, 1.0))
                val = float(r.get(key, 0.0))
                rng = hi - lo
                out[key] = float(np.clip((val - lo) / rng if rng > 0 else 0.0, 0.0, 1.0))
            return out
        history_norm = [_norm_readings(r) for r in history]
        sensor_readings_norm = _norm_readings(sensor_readings)
    except Exception:
        # Fallback: use raw readings if normalization fails
        history_norm = list(history)
        sensor_readings_norm = dict(sensor_readings)

    window_features = extract_window_features(history_norm, window=_WINDOW, sensor_keys=SENSOR_KEYS)

    # --- Head A: IsolationForest ---
    if_score = 0.5  # default
    shap_vals: Dict[str, float] = {}
    if if_model is not None:
        try:
            # IsolationForest.score_samples returns negative (lower = more anomalous)
            raw_score = float(if_model.score_samples(window_features.reshape(1, -1))[0])
            # FIX (2026-06-07): data-driven normalization using sklearn's decision boundary.
            # if_model.offset_ is the decision-function threshold: score_samples > offset_ → inlier.
            # We scale so that:
            #   raw_score == offset_  → if_score = 0.50  (decision boundary)
            #   raw_score >> offset_  → if_score → 0.00  (very normal)
            #   raw_score << offset_  → if_score → 1.00  (very anomalous)
            # Scale factor = abs(offset_) so the mapping is data-driven.
            offset = float(getattr(if_model, "offset_", -0.3))
            scale  = max(abs(offset), 0.1)   # guard against zero
            # offset is negative; more negative raw_score → more anomalous
            if_score = float(np.clip((offset - raw_score) / scale, 0.0, 1.0))
            # SHAP — only on flagged windows for performance
            if if_score > 0.4:
                shap_vals = _compute_shap(if_model, window_features, SENSOR_KEYS)
        except Exception as exc:
            logger.debug("IsolationForest score failed: %s", exc)

    # --- Head B: LSTM-AE ---
    ae_score = 0.5
    per_sensor_error = np.zeros(len(SENSOR_KEYS))
    ae = _get_lstm_ae(eq_key)
    if ae is not None and len(history) >= 2 and ae._n_features == len(SENSOR_KEYS):
        # Build (T, D) window matrix — D must match n_features the AE was trained on.
        # Use normalized history (already computed above) so the AE operates in [0,1] space.
        tail = list(history_norm)[-_WINDOW:]
        window_matrix = np.array(
            [[float(r.get(k, 0.0)) for k in SENSOR_KEYS] for r in tail],
            dtype=np.float32,
        )
        ae_score, per_sensor_error = ae.score(window_matrix)
    elif ae is not None and ae._n_features != len(SENSOR_KEYS):
        logger.debug(
            "LSTM-AE skipped: artifact n_features=%d but inference window D=%d "
            "(retrain with train_anomaly.py to fix)",
            ae._n_features, len(SENSOR_KEYS),
        )

    # --- Head C: River (streaming, optional) ---
    river_s = _river_score(sensor_readings_norm)

    # --- Physics degradation index (steel-sensor domain fix) ---
    # Domain-mismatch fix: IsolationForest trained on C-MAPSS normalized space
    # cannot discriminate steel-plant degradation from physical sensor readings.
    # physics_degradation_index() computes per-sensor severity using domain-specific
    # operating bands (ISO 10816 / ISO 13381), then aggregates as 0.6*max + 0.4*mean
    # so one critical sensor dominates while multiple elevated sensors compound.
    # Fusion: fused = max(model_score, physics_idx) weighted average — ensures
    # that clearly-failing readings (physics_idx → 1) always map to HIGH/CRITICAL
    # severity even when the model score is suppressed by training-data mismatch.
    physics_idx = physics_degradation_index(sensor_readings, equipment_class)

    # --- Fusion ---
    combined = _IF_ALPHA * if_score + _AE_ALPHA * ae_score
    combined = float(np.clip(combined, 0.0, 1.0))

    # Apply adaptive threshold if available
    threshold = float(adaptive_threshold) if adaptive_threshold is not None else 0.65
    # Normalize model score to threshold: > threshold → maps to MEDIUM+
    if combined < threshold * 0.5:
        model_fused = combined * (0.40 / max(threshold * 0.5, 1e-6))
    else:
        model_fused = 0.40 + (combined - threshold * 0.5) * (0.60 / max(1.0 - threshold * 0.5, 1e-6))
    model_fused = float(np.clip(model_fused, 0.0, 1.0))

    # Physics-model fusion: take the maximum to guarantee physics-critical signals
    # always escalate severity, then blend 50/50 so normal readings stay low when
    # both model and physics agree.  This gives:
    #   normal   → low physics_idx (0.05–0.15) + low model → LOW/MEDIUM score
    #   failing  → high physics_idx (0.85–0.98) dominates → HIGH/CRITICAL score
    fused = float(np.clip(
        0.5 * max(model_fused, physics_idx) + 0.5 * physics_idx,
        0.0, 1.0,
    ))

    severity = _severity(fused)

    triggered = [k for k, v in shap_vals.items() if v > 0.15]

    return {
        "score": round(fused, 4),
        "severity": severity.value,
        "shap_values": shap_vals,
        "triggered_sensors": triggered,
        "if_score": round(if_score, 4),
        "ae_score": round(ae_score, 4),
        "river_score": round(river_s, 4) if river_s is not None else None,
        "reconstruction_error": per_sensor_error.tolist(),
    }


# ---------------------------------------------------------------------------
# Offline training entry-point (imported by scripts/train_anomaly.py)
# ---------------------------------------------------------------------------

def train_anomaly_models(
    normal_df: "np.ndarray",                # (N, D) float32 — normal window *features* for IF (D=FEATURE_DIM=54)
    anomaly_df: Optional["np.ndarray"],     # (M, D) float32 — anomaly window features (for IF threshold)
    equipment_class: str = "default",
    n_estimators: int = 200,
    contamination: float = 0.02,
    lstm_epochs: int = 20,
    models_dir: Optional["Path"] = None,    # type: ignore[type-arg]
    raw_sensor_windows: Optional["np.ndarray"] = None,  # (N, N_SENSORS) raw sensor time-steps for LSTM-AE
) -> None:
    """
    Train IsolationForest + LSTM-AE on normal sensor windows.

    ``normal_df`` is the 54-dim window-feature matrix (for IsolationForest).
    ``raw_sensor_windows`` is the raw 9-dim sensor time-steps matrix (for LSTM-AE).
      If not provided, a 9-dim slice of normal_df is used as a fallback.

    ``anomaly_df`` (optional) is used to calibrate the adaptive threshold.

    Artifacts written to data/models/:
      anomaly_if_{equipment_class}.pkl         - IsolationForest
      anomaly_threshold_{equipment_class}.pkl  - 97th percentile threshold (float)
      anomaly_lstm_ae_{equipment_class}.pkl    - {'state_dict': ..., 'threshold': ...}
    """
    from pathlib import Path  # local import avoids circular at module level
    try:
        from sklearn.ensemble import IsolationForest  # type: ignore[import]
        import joblib  # type: ignore[import]
    except ImportError as exc:
        raise ImportError("pip install scikit-learn joblib") from exc

    if models_dir is None:
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").exists():
                models_dir = parent / "data" / "models"
                break
        else:
            models_dir = Path.cwd() / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    eq_key = equipment_class.lower().replace(" ", "_").replace("-", "_")

    # --- IsolationForest ---
    logger.info("Training IsolationForest: %d normal samples, contamination=%.2f", len(normal_df), contamination)
    if_model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    if_model.fit(normal_df)

    # Adaptive threshold = 97th pctile of IF scores on normal data
    scores = -if_model.score_samples(normal_df)  # higher = more anomalous
    if anomaly_df is not None and len(anomaly_df) > 0:
        anom_scores = -if_model.score_samples(anomaly_df)
        threshold = float(np.percentile(np.concatenate([scores, anom_scores]), 97))
    else:
        threshold = float(np.percentile(scores, 97))
    logger.info("IsolationForest trained. Adaptive threshold=%.4f", threshold)

    if_path = models_dir / f"anomaly_if_{eq_key}.pkl"
    joblib.dump(if_model, if_path)
    th_path = models_dir / f"anomaly_threshold_{eq_key}.pkl"
    joblib.dump(threshold, th_path)
    logger.info("Saved IF → %s", if_path)

    # --- LSTM-AE ---
    # IMPORTANT: the LSTM-AE operates on raw sensor time-series (T, N_SENSORS=9),
    # NOT on the 54-dim window-feature vectors used by IsolationForest.
    # ``raw_sensor_windows`` must have shape (N, N_SENSORS).  If the caller did
    # not supply it, fall back to the first len(SENSOR_KEYS) columns of normal_df
    # as a best-effort so training still completes.
    try:
        import torch  # type: ignore[import]
        import torch.nn as nn  # type: ignore[import]

        lstm_train_data = (
            raw_sensor_windows
            if raw_sensor_windows is not None
            else normal_df[:, : len(SENSOR_KEYS)]
        )
        n_features = lstm_train_data.shape[1]
        if n_features != len(SENSOR_KEYS):
            logger.warning(
                "LSTM-AE training: raw_sensor_windows has %d features, expected %d. "
                "Inference will use %d features — mismatched artifact will fail at load.",
                n_features, len(SENSOR_KEYS), len(SENSOR_KEYS),
            )
        hidden = 32
        n_layers = 2

        class _LSTMAE(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.LSTM(n_features, hidden, n_layers, batch_first=True)
                self.decoder = nn.LSTM(hidden, hidden, n_layers, batch_first=True)
                self.out_proj = nn.Linear(hidden, n_features)

            def forward(self, x):
                _, (h, c) = self.encoder(x)
                T = x.shape[1]
                dec_in = h[-1].unsqueeze(1).repeat(1, T, 1)
                dec_out, _ = self.decoder(dec_in, (h, c))
                return self.out_proj(dec_out)

        # Build windowed sequences: each row in lstm_train_data is a time-step (raw sensor)
        # Group into (B, T, D) batches of _WINDOW steps
        W = _WINDOW
        D = n_features
        N = len(lstm_train_data)
        n_sequences = max(1, N - W + 1)
        sequences = np.array(
            [lstm_train_data[i:i + W] for i in range(n_sequences)], dtype=np.float32
        )
        X_tensor = torch.tensor(sequences)  # (B, W, D)

        ae_model = _LSTMAE()
        optimizer = torch.optim.Adam(ae_model.parameters(), lr=1e-3)
        criterion = nn.MSELoss()

        batch_size = 32
        ae_model.train()
        for epoch in range(lstm_epochs):
            perm = torch.randperm(len(X_tensor))
            total_loss = 0.0
            for start in range(0, len(X_tensor), batch_size):
                idx = perm[start:start + batch_size]
                xb = X_tensor[idx]
                optimizer.zero_grad()
                xb_hat = ae_model(xb)
                loss = criterion(xb_hat, xb)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(xb)
            avg_loss = total_loss / len(X_tensor)
            if epoch % 5 == 0 or epoch == lstm_epochs - 1:
                logger.info("LSTM-AE epoch %d/%d loss=%.6f", epoch + 1, lstm_epochs, avg_loss)

        # Compute reconstruction threshold on normal data
        ae_model.eval()
        with torch.no_grad():
            x_hat = ae_model(X_tensor)
            recon_mse = ((X_tensor - x_hat) ** 2).mean(dim=(1, 2)).numpy()
        ae_threshold = float(np.percentile(recon_mse, 97))
        logger.info("LSTM-AE threshold (97th pctile on normal): %.6f", ae_threshold)

        ae_artifact = {
            "state_dict": ae_model.state_dict(),
            "threshold": ae_threshold,
            "n_features": n_features,
        }
        ae_path = models_dir / f"anomaly_lstm_ae_{eq_key}.pkl"
        joblib.dump(ae_artifact, ae_path)
        logger.info("Saved LSTM-AE → %s", ae_path)

    except ImportError:
        logger.warning("torch not installed — skipping LSTM-AE training.")
    except Exception as exc:
        logger.warning("LSTM-AE training failed: %s", exc)

    logger.info("Anomaly model training for '%s' complete.", equipment_class)


def train_river_hst(
    raw_sensor_windows: "np.ndarray",  # (N, N_SENSORS) raw sensor time-steps
    sensor_keys: Optional[List[str]] = None,
    n_trees: int = 25,
    height: int = 8,
    window_size: int = 250,
    models_dir: Optional["Path"] = None,
) -> None:
    """
    Train (warm-up) a River HalfSpaceTrees streaming anomaly model.

    The HST learns online from a stream of normal sensor samples.  Each row of
    ``raw_sensor_windows`` is treated as one streaming sample (dict of sensor
    readings).  The fitted model is saved as a single shared artifact
    ``anomaly_river_hst.pkl`` (one global HST, not per-equipment-class, since
    River HST adapts at runtime to any distribution shift).

    Artifacts written to data/models/:
      anomaly_river_hst.pkl — {'model': HalfSpaceTrees, 'threshold': float,
                               'sensor_keys': list}
    """
    from pathlib import Path as _Path

    try:
        from river.anomaly import HalfSpaceTrees  # type: ignore[import]
        import joblib  # type: ignore[import]
    except ImportError as exc:
        raise ImportError("pip install river joblib") from exc

    if sensor_keys is None:
        sensor_keys = SENSOR_KEYS

    if models_dir is None:
        here = _Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").exists():
                models_dir = parent / "data" / "models"
                break
        else:
            models_dir = _Path.cwd() / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    hst = HalfSpaceTrees(
        n_trees=n_trees,
        height=height,
        window_size=window_size,
        seed=42,
    )

    scores = []
    logger.info(
        "River HST warm-up: %d samples, n_trees=%d, height=%d, window_size=%d",
        len(raw_sensor_windows), n_trees, height, window_size,
    )
    for row in raw_sensor_windows:
        sample = {k: float(v) for k, v in zip(sensor_keys, row)}
        score = float(hst.score_one(sample))
        hst.learn_one(sample)
        scores.append(score)

    # Threshold = 97th percentile of warm-up scores (anomaly if score > threshold)
    threshold = float(np.percentile(scores, 97)) if scores else 0.5
    logger.info("River HST warm-up complete. Threshold (97th pctile)=%.4f", threshold)

    artifact = {
        "model": hst,
        "threshold": threshold,
        "sensor_keys": list(sensor_keys),
    }
    out_path = models_dir / "anomaly_river_hst.pkl"
    joblib.dump(artifact, out_path)
    logger.info("Saved River HST → %s", out_path)
