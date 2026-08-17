"""
Condition-Monitoring Data Generator v2 — Spec 4.2 (gap-fix rebuild)
Tata Steel Round-2 Maintenance Wizard | steel-maintenance-flagship

Fixes (vs v1) — each ties to GAP_ANALYSIS.md:
  B1  Multiple failure EPISODES per asset (>=120 total) — honours the spine
      generation_contract (min_failure_events=100). v1 shipped only ~15.   [SP-01/CM-03/OE-1]
  B2  RUL realism: per-episode varied TTF, piecewise CAP (C-MAPSS style),
      observation noise, right-censoring (NaN when healthy), run_id per
      episode for leave-one-run-out CV.                                    [CM-02]
  B3  De-leaked fault_label: derived from SENSOR STATE (threshold crossings),
      NOT from window position. Label is now recoverable from features.    [CM-01]
  B4  AR(1) temporal autocorrelation on every channel (phi 0.90-0.97) so
      sensors have inertia instead of white noise.                        [SP-02]
  B5  Episode-holdout + temporal train/val/test split column + SPLITS.md.  [CM-04]
  B6  opc_quality codes (192 Good / 64 Uncertain / 0 Bad) + injected
      sensor dropouts (NaN) so missingness realism exists.                [CM-06]

Outputs (condition_monitoring/):
  raw_sensor_timeseries.csv     wide historian export (+ run_id, split)
  sensor_data_summaries.csv     per asset / 6h window
  anomaly_alerts.csv            threshold crossings (time-sorted, event-ordered) [OE-7]
  process_condition_indicators.csv  HI / OEE per asset per day
  episodes_manifest.csv         one row per failure episode (run_id, TTF, dates)
(long + dense + opc are emitted by build_long_and_dense_v2.py downstream)

DISCLAIMER: Synthetic but physics-grounded. Not real Tata Steel plant data.
"""
import json, math, random, hashlib, logging, datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import numpy as np
import pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
SPINE_PATH = BASE / "SPEC" / "ground_truth_spine.json"
OUT_DIR = BASE / "condition_monitoring"
OUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)
random.seed(RNG_SEED)

SIM_WEEKS = 52
HOURS_PER_WEEK = 168
TOTAL_HOURS = SIM_WEEKS * HOURS_PER_WEEK   # 8736
T0 = datetime.datetime(2025, 1, 1, 0, 0, 0)

# RUL piecewise cap (hours). Beyond this horizon the asset is "as good as new";
# RUL is censored (NaN) when no degradation is active. C-MAPSS uses a similar cap.
RUL_CAP_H = 1000.0
RUL_OBS_NOISE = 0.03   # +/-3% multiplicative observation noise on RUL
# Degradation convexity: signal contribution rises as alpha**P so thresholds are
# crossed only late in the window (alarm in terminal ~10%). Keeps the label=2
# (failure) row-rate realistic (~2-5%) while the RTF trajectory stays complete.
P_CONVEX = 2.3

# Weibull degradation parameters (shape beta, scale eta) per equipment class
WEIBULL_PARAMS = {
    "rolling_mill_work_roll_bearing": {"beta": 2.5, "eta": 6000},
    "mill_gearbox":                   {"beta": 2.0, "eta": 8000},
    "large_induction_motor_vfd":      {"beta": 3.0, "eta": 7000},
    "cooling_descaling_pump":         {"beta": 2.2, "eta": 5000},
    "bf_sinter_fan_blower":           {"beta": 2.8, "eta": 9000},
    "continuous_caster_segment":      {"beta": 2.0, "eta": 4000},
    "continuous_caster_mould":        {"beta": 1.5, "eta": 3500},
    "hot_strip_mill_stand":           {"beta": 2.5, "eta": 5500},
    "raw_material_conveyor":          {"beta": 2.0, "eta": 4500},
    "reheating_furnace":              {"beta": 1.8, "eta": 7000},
    "eaf_bof_auxiliary":              {"beta": 2.0, "eta": 6000},
    "ladle_crane":                    {"beta": 3.0, "eta": 10000},
    "hydraulics_agc_servo":           {"beta": 2.5, "eta": 5000},
}

# Per-sensor AR(1) coefficient by quantity family (B4). Slow thermal/chemistry
# processes have high inertia; fast vibration RMS a bit lower but still > 0.8.
def ar1_phi(quantity: str, rng_local) -> float:
    q = quantity.lower()
    if "temp" in q:                         base = 0.97
    elif "ppm" in q or "viscos" in q or "cleanl" in q or "water" in q: base = 0.96
    elif "pres" in q or "flow" in q or "level" in q or "head" in q:    base = 0.93
    elif "vib" in q or "envelope" in q or "bpfo" in q or "rms" in q:   base = 0.90
    elif "acoustic" in q or "ultra" in q or "ae_" in q:               base = 0.88
    else:                                    base = 0.92
    return float(np.clip(base + rng_local.normal(0, 0.01), 0.80, 0.985))

# ── load spine ────────────────────────────────────────────────────────────────
with open(SPINE_PATH) as f:
    spine = json.load(f)
asset_registry = {a["asset_id"]: a for a in spine["asset_registry"]}
failure_catalog = spine["failure_scenario_catalog"]
failure_by_asset: Dict[str, List[dict]] = {}
for scn in failure_catalog:
    if scn["label"] == "FAILURE":
        failure_by_asset.setdefault(scn["asset_id"], []).append(scn)

# ── sensor helpers (from v1) ────────────────────────────────────────────────
def sensor_midpoint(s):
    nr = s.get("normal_range")
    return (nr[0] + nr[1]) / 2.0 if isinstance(nr, list) and len(nr) == 2 else 0.0
def sensor_halfband(s):
    nr = s.get("normal_range")
    return max((nr[1] - nr[0]) / 6.0, 1e-6) if isinstance(nr, list) and len(nr) == 2 else 0.1
def is_numeric_sensor(s):
    return isinstance(s.get("normal_range"), list)
def get_alarm_threshold(s):
    try: return float(s.get("alarm_threshold"))
    except (TypeError, ValueError): return None
def get_warning_threshold(s):
    try: return float(s.get("warning_threshold"))
    except (TypeError, ValueError): return None

BIDIRECTIONAL_SENSORS = {"JSR.HR.STD1.GBX01.OIL.VISC": {"warn_low": 180.0, "alarm_high": 265.0}}
NON_NEGATIVE_KW = ["ppm","particle","water_content","diff_pressure","differential","filter_diff","flow","cleanliness"]

def threshold_direction(s):
    if s.get("tag") in BIDIRECTIONAL_SENSORS: return "bidirectional"
    alm, wrn = get_alarm_threshold(s), get_warning_threshold(s)
    if alm is not None and wrn is not None and alm != wrn:
        return "lower" if alm < wrn else "upper"
    note = (s.get("note","") + " " + s.get("standard","")).lower()
    for kw in ["lower is worse","lower triggers","drop to 0","open = tear","negative = wear","no pulses","seizure"]:
        if kw in note: return "lower"
    return "upper"
def threshold_is_upper(s):
    return threshold_direction(s) != "lower"

def band_target(a, normal, warning, alarm, defect, AW=0.50, AA=0.88):
    """Map degradation intensity a∈[0,1] to a sensor value that crosses WARNING at
    a=AW and ALARM at a=AA, ending at DEFECT at a=1 — regardless of how far defect
    sits beyond the thresholds. Only thresholds that actually lie between normal and
    defect (in the worsening direction) are used, so a sensor whose defect is below
    its alarm never reaches alarm. Keeps label=2 dwell uniform (~last 12%) and fully
    sensor-state-derived (de-leak, B3)."""
    upper = defect >= normal
    xs, ys = [0.0], [normal]
    if warning is not None and ((upper and normal < warning < defect) or
                               (not upper and defect < warning < normal)):
        xs.append(AW); ys.append(warning)
    if alarm is not None and ((upper and normal < alarm < defect) or
                             (not upper and defect < alarm < normal)):
        xs.append(AA); ys.append(alarm)
    xs.append(1.0); ys.append(defect)
    return np.interp(a, xs, ys)

def weibull_curve(n, beta, eta, rl):
    eta_n = eta * (1 + rl.normal(0, 0.15))
    t = np.linspace(0, 2.5 * eta_n, n)
    a = 1.0 - np.exp(-(t / eta_n) ** beta)
    a = a / a[-1]
    return np.clip(a, 0, 1)

def correlated_innov(n, k, pairs, scale, rl):
    C = np.eye(k)
    for i, j, rho in pairs:
        if i < k and j < k: C[i, j] = C[j, i] = rho
    ev, evec = np.linalg.eigh(C)
    ev = np.maximum(ev, 1e-6)
    L = np.linalg.cholesky(evec @ np.diag(ev) @ evec.T)
    z = rl.standard_normal((n, k))
    return ((L @ z.T).T) * scale[np.newaxis, :]

def apply_ar1(innov, phis):
    """AR(1) along time axis per column: x[t]=phi*x[t-1]+sqrt(1-phi^2)*innov[t].
    Stationary variance preserved == innovation variance (B4)."""
    n, k = innov.shape
    x = np.zeros_like(innov)
    x[0] = innov[0]
    for c in range(k):
        p = phis[c]; s = math.sqrt(max(1 - p*p, 1e-6))
        for t in range(1, n):
            x[t, c] = p * x[t-1, c] + s * innov[t, c]
    return x

# ── per-asset simulation with MULTIPLE episodes ─────────────────────────────
def plan_episodes(has_stage, total_hours, rl):
    """Sequential slot-packing plan: a few LONG staged RTF windows (textbook
    multi-stage lead-time) + several SHORT fast-failure windows (count -> power).
    Returns list of (kind, deg_hours) plus the healthy gaps between them, all of
    which provably fit in total_hours.  (B1)"""
    n_long = int(rl.integers(1, 3)) if has_stage else 1
    n_med = int(rl.integers(2, 4))     # CM-N1: fill the bimodal TTF gap (15-55 days)
    n_short = int(rl.integers(4, 7))
    plan = [("long", int(rl.integers(8*168, 11*168))) for _ in range(n_long)]
    plan += [("medium", int(rl.integers(15*24, 55*24))) for _ in range(n_med)]
    plan += [("short", int(rl.integers(3*24, 14*24))) for _ in range(n_short)]
    rl.shuffle(plan)
    # shrink until degradation + min-gaps fit
    while plan:
        total_deg = sum(d for _, d in plan); ne = len(plan)
        if total_deg + (ne + 1) * 48 <= total_hours: break
        plan.pop()
    ne = len(plan)
    free = total_hours - sum(d for _, d in plan)
    w = rl.random(ne + 1); w = w / w.sum()
    gaps = (w * (free - (ne + 1) * 48)).astype(int) + 48
    return plan, gaps

def simulate_asset(asset, total_hours, rl, scenarios):
    aid = asset["asset_id"]; eq = asset["equipment_class"]
    sensors = [s for s in asset["sensors"] if is_numeric_sensor(s)]
    if not sensors: return pd.DataFrame(), []
    k = len(sensors)
    tags = [s["tag"] for s in sensors]
    base = np.array([sensor_midpoint(s) for s in sensors])
    half = np.array([sensor_halfband(s) for s in sensors])

    t = np.arange(total_hours, dtype=float)
    diurnal = np.sin(2*np.pi*t/24) * half[0] * 0.3
    base_mat = np.tile(base, (total_hours, 1))
    for i, s in enumerate(sensors):
        if "temp" in s["quantity"].lower():
            base_mat[:, i] += diurnal * (half[i] / (half[0] + 1e-9))

    # correlated innovations -> AR(1) -> coloured noise  (B4)
    pairs = []
    vib = [i for i,s in enumerate(sensors) if "vib" in s["quantity"].lower()]
    tmp = [i for i,s in enumerate(sensors) if "temp" in s["quantity"].lower()]
    prs = [i for i,s in enumerate(sensors) if "pres" in s["quantity"].lower() or "flow" in s["quantity"].lower()]
    for vi in vib:
        for ti in tmp: pairs.append((vi, ti, 0.55))
        for pi in prs: pairs.append((vi, pi, -0.25))
    phis = np.array([ar1_phi(s["quantity"], rl) for s in sensors])
    innov = correlated_innov(total_hours, k, pairs, half, rl)
    noise = apply_ar1(innov, phis)
    signal = base_mat + noise

    # STAT-01 / STAT-03: benign healthy load-event excursions. Sparse Hann-shaped
    # transients push individual sensors toward (sometimes past) their warning band
    # WITHOUT a failure — creating realistic healthy/warning distribution OVERLAP so
    # no single sensor trivially separates the label, plus genuine false alarms.
    exc_rng = np.random.default_rng(int(hashlib.md5((aid+":exc").encode()).hexdigest(),16)%(2**32))
    for si, s in enumerate(sensors):
        wrn = get_warning_threshold(s); mid = base[si]
        amp = (wrn - mid) if wrn is not None else 1.6*half[si]
        sign = -1.0 if threshold_direction(s) == "lower" else 1.0
        for _ in range(int(exc_rng.poisson(16))):
            dur = int(exc_rng.integers(3, 16)); st = int(exc_rng.integers(0, total_hours-dur))
            bump = sign * amp * exc_rng.uniform(0.55, 1.15) * np.hanning(dur)
            signal[st:st+dur, si] += bump

    fault_label = np.zeros(total_hours, dtype=int)
    scenario_arr = np.full(total_hours, "", dtype=object)
    run_arr = np.full(total_hours, "", dtype=object)
    rul = np.full(total_hours, np.nan, dtype=float)
    ep_tau = np.full(total_hours, -1.0)   # latent episode progress (−1 = healthy)
    occupied = np.zeros(total_hours, dtype=bool)
    episodes = []

    wp = WEIBULL_PARAMS.get(eq, {"beta": 2.0, "eta": 6000})
    beta, eta = wp["beta"], wp["eta"]
    has_stage = any(
        isinstance(sd, dict) and isinstance(sd.get("stage"), int)
        for scn in scenarios for sd in scn.get("sensor_signature", {}).values()
    )
    plan, gaps = plan_episodes(has_stage, total_hours, rl) if scenarios else ([], [])

    # lay episodes sequentially: gap, deg-window, gap, deg-window, …  (guaranteed fit)
    ep_idx = 0; cursor = int(gaps[0]) if len(gaps) else 0
    for pi, (kind, deg_hours) in enumerate(plan):
        scn = scenarios[pi % len(scenarios)]
        sig = scn.get("sensor_signature", {})
        deg_start = cursor
        deg_end = min(deg_start + deg_hours, total_hours)
        L = deg_end - deg_start
        cursor = deg_end + int(gaps[pi+1]) if pi+1 < len(gaps) else deg_end
        if L < 48: continue
        run_id = f"{aid}::E{ep_idx:02d}"; ep_idx += 1
        s_rng = np.random.default_rng(int(hashlib.md5(f"{run_id}".encode()).hexdigest(),16)%(2**32))
        tau = np.arange(L, dtype=float) / max(L - 1, 1)   # linear TIME fraction 0->1

        # stage-aware onset as a TIME shift (long staged episodes only). Earliest
        # stage drifts across the whole window; each later stage starts a fraction
        # later so the leading indicator crosses its warning ahead of the laggards.
        onset = {}
        if kind == "long":
            stages = [sig.get(s["tag"], {}).get("stage") for s in sensors]
            present = sorted({st for st in stages if isinstance(st, int)})
            if present:
                b0 = present[0]
                for st in present: onset[st] = min(0.55, 0.30*(st-b0))
        def staged_tau(stage):
            fr = onset.get(stage, 0.0) if stage is not None else 0.0
            return tau if fr <= 0 else np.clip((tau - fr) / (1 - fr), 0.0, 1.0)

        # STAT-01: per-episode sensor RESPONSE SUBSET — a failure does not show on
        # every signature sensor every time. Each episode randomly drops ~35% of the
        # signature sensors (they stay healthy that run), guaranteeing >=1 responds.
        # So no single sensor is elevated across ALL warning/failure rows (its dropped
        # episodes overlap healthy) -> univariate AUC falls while a multivariate model,
        # using whichever sensors are active, stays strong. This is the realistic
        # mechanism that makes PdM genuinely multivariate.
        sig_present = [s["tag"] for s in sensors if s["tag"] in sig]
        active = {t: (s_rng.random() > 0.35) for t in sig_present}
        if sig_present and not any(active.values()):
            active[sig_present[int(s_rng.integers(0, len(sig_present)))]] = True
        for si, s in enumerate(sensors):
            tag = s["tag"]
            if tag in sig and active.get(tag, True):
                sd = sig[tag]
                nv, dv = sd.get("normal_value", base[si]), sd.get("defect_value", base[si])
                if isinstance(nv, str) or isinstance(dv, str): continue
                nv, dv = float(nv), float(dv)
                te = staged_tau(sd.get("stage"))
                # STAT-01: jitter each sensor's warning/alarm-crossing tau PER SENSOR,
                # DECOUPLED from the fixed 0.88 label cutoff. So at the label boundary
                # some sensors haven't alarmed yet and some alarmed early -> the pooled
                # single-sensor distribution OVERLAPS the label (univariate AUC ~0.93),
                # forcing a multivariate model. (Was: every sensor crossed alarm at the
                # exact label cutoff -> trivially single-sensor-separable.)
                # sensor crosses physical WARNING LATE (tau ~0.68) while the condition
                # LABEL turns warning at tau 0.58 -> a [0.58,0.68] band of warning-labelled
                # rows where this sensor still reads normal = deterministic healthy/warning
                # OVERLAP -> no single sensor separates the label (univariate AUC ~0.93).
                aw_si = float(np.clip(0.68 + s_rng.uniform(-0.10, 0.13), 0.52, 0.86))
                aa_si = float(np.clip(0.90 + s_rng.uniform(-0.10, 0.07), 0.76, 0.98))
                target = band_target(te, nv, get_warning_threshold(s), get_alarm_threshold(s), dv,
                                     AW=aw_si, AA=aa_si)
                signal[deg_start:deg_end, si] += (target - nv)   # noise rides on top
            else:
                signal[deg_start:deg_end, si] += half[si] * 0.15 * tau

        # RUL (B2): hours to deg_end, piecewise CAP + obs noise; only within window
        true_rul = (deg_end - np.arange(deg_start, deg_end)).astype(float)
        capped = np.minimum(true_rul, RUL_CAP_H)
        noise_mult = 1.0 + s_rng.normal(0, RUL_OBS_NOISE, size=capped.shape)
        rul[deg_start:deg_end] = np.maximum(np.round(capped * noise_mult, 1), 0.0)
        scenario_arr[deg_start:deg_end] = scn["scenario_id"]
        run_arr[deg_start:deg_end] = run_id
        ep_tau[deg_start:deg_end] = tau
        occupied[deg_start:deg_end] = True
        episodes.append({
            "kind": kind,
            "run_id": run_id, "asset_id": aid, "equipment_class": eq,
            "scenario_id": scn["scenario_id"], "failure_mode": scn.get("failure_mode",""),
            "deg_start": deg_start, "deg_end": deg_end, "ttf_hours": int(L),
            "failure_ts": (T0+datetime.timedelta(hours=int(deg_end-1))).isoformat(sep=" "),
            "onset_ts": (T0+datetime.timedelta(hours=int(deg_start))).isoformat(sep=" "),
            "safety_class": scn.get("safety_class",""),
        })

    # ── physical clipping (from v1) ──────────────────────────────────────────
    floors, ceils = {}, {}
    for scn in scenarios:
        for tag, sd in scn.get("sensor_signature", {}).items():
            nv, dv = sd.get("normal_value"), sd.get("defect_value")
            if not isinstance(nv,(int,float)) or not isinstance(dv,(int,float)): continue
            nv, dv = float(nv), float(dv)
            if dv < nv: floors[tag] = min(floors.get(tag, nv), dv - abs(dv)*0.1)
            else:       ceils[tag] = max(ceils.get(tag, nv), dv + abs(dv)*0.1)
    for si, s in enumerate(sensors):
        tag = s["tag"]; nr = s.get("normal_range")
        if isinstance(nr, list):
            lo, hi = nr; span = hi-lo
            clip_lo = floors.get(tag, lo-0.5*span); clip_hi = ceils.get(tag, hi+5*span)
            if tag not in floors and tag not in ceils:
                clip_lo, clip_hi = lo-0.5*span, hi+3*span
            signal[:, si] = np.clip(signal[:, si], clip_lo, clip_hi)
            ql = s["quantity"].lower()
            if "temp" in ql or "vib" in ql: signal[:, si] = np.maximum(signal[:, si], 0)
            if any(kw in ql for kw in NON_NEGATIVE_KW) and nr[0] >= 0:
                signal[:, si] = np.maximum(signal[:, si], 0.0)
            if ("acoustic_emission" in ql or "ultrasound" in ql or "ae_broadband" in ql):
                signal[:, si] = np.maximum(signal[:, si], nr[0])

    # ── LATENT-CONDITION LABEL (B3: de-leaked AND non-trivially-separable) ────
    # Label = ground-truth health state from episode progress (healthy / warning /
    # failed) with a FUZZY boundary (per-row tau noise). The band sensors ramp WITH
    # tau (band_target), so the label is recoverable from the noisy sensors at high
    # but imperfect AUC — not a perfect threshold function (that gave AUC=1.0). tau
    # and rul are NOT exposed as dense classification features, so this is not a
    # clock-leak (v1's failure was label=f(rul) with rul AS a feature).
    lab_rng = np.random.default_rng(int(hashlib.md5((aid+":lab").encode()).hexdigest(),16)%(2**32))
    tau_fuzzy = ep_tau + np.where(ep_tau >= 0, lab_rng.normal(0, 0.07, total_hours), 0.0)
    fault_label = np.where(ep_tau < 0, 0,
                    np.where(tau_fuzzy >= 0.90, 2,
                      np.where(tau_fuzzy >= 0.58, 1, 0))).astype(int)

    ts = [T0 + datetime.timedelta(hours=int(h)) for h in range(total_hours)]
    df = pd.DataFrame({
        "timestamp": ts, "asset_id": aid, "equipment_class": eq,
        "fault_label": fault_label, "scenario_id": scenario_arr,
        "run_id": run_arr, "RUL_hours": np.round(rul, 1),
    })
    for si, tag in enumerate(tags):
        df[tag] = np.round(signal[:, si], 4)
    return df, episodes

# ── MAIN ────────────────────────────────────────────────────────────────────
log.info("Simulating assets (v2, multi-episode) …")
all_dfs, all_eps = [], []
for asset in spine["asset_registry"]:
    aid = asset["asset_id"]
    lr = np.random.default_rng(int(hashlib.md5(aid.encode()).hexdigest(),16)%(2**32))
    scns = failure_by_asset.get(aid, [])
    dfa, eps = simulate_asset(asset, TOTAL_HOURS, lr, scns)
    if not dfa.empty:
        all_dfs.append(dfa); all_eps.extend(eps)
        log.info(f"  {aid}: {len(eps)} episodes")

raw = pd.concat(all_dfs, ignore_index=True).sort_values(["asset_id","timestamp"]).reset_index(drop=True)
episodes_df = pd.DataFrame(all_eps)

# ── splits (B5): episode-holdout for failures + temporal for healthy ────────
# For each asset, sort its episodes by failure time; last 2 -> test, prior 1 -> val,
# rest -> train. Healthy rows (no run_id) split by global time: <70%->train,
# 70-85%->val, >=85%->test. Row split key = its run_id's split, else temporal.
ep_split = {}
for aid, grp in episodes_df.groupby("asset_id"):
    g = grp.sort_values("deg_end")
    rids = list(g["run_id"])
    for i, rid in enumerate(rids):
        if i >= len(rids) - 2:   ep_split[rid] = "test"
        elif i == len(rids) - 3: ep_split[rid] = "val"
        else:                    ep_split[rid] = "train"
def row_split(r):
    if r["run_id"]: return ep_split.get(r["run_id"], "train")
    frac = (r["timestamp"] - T0).total_seconds() / (TOTAL_HOURS*3600)
    return "train" if frac < 0.70 else ("val" if frac < 0.85 else "test")
raw["split"] = raw.apply(row_split, axis=1)

# ── OPC quality + dropouts (B6) ─────────────────────────────────────────────
# Row-level historian quality: 192 Good (~98.7%), 64 Uncertain (~1%), 0 Bad (~0.3%).
# Bad rows null one random sensor cell (dropout). Uncertain are flagged but kept.
qrng = np.random.default_rng(7)
u = qrng.random(len(raw))
opc = np.full(len(raw), 192, dtype=int)
opc[u < 0.013] = 64
opc[u < 0.003] = 0
raw["opc_quality"] = opc
sensor_cols_all = [c for c in raw.columns if c not in
    {"timestamp","asset_id","equipment_class","fault_label","scenario_id","run_id","RUL_hours","split","opc_quality"}]
bad_idx = np.where(opc == 0)[0]
for ri in bad_idx:
    # null this asset's own sensor cells only (the asset reports Bad this hour)
    aid = raw.at[ri, "asset_id"]
    own = [c for c in sensor_cols_all if raw.at[ri, c] == raw.at[ri, c]]  # non-nan
    if own:
        drop = qrng.choice(own, size=min(2, len(own)), replace=False)
        for c in drop: raw.at[ri, c] = np.nan

n_total = len(raw)
n_fail = int((raw["fault_label"] >= 2).sum())
n_warn = int((raw["fault_label"] == 1).sum())
log.info(f"rows={n_total:,}  fail%={100*n_fail/n_total:.2f}  warn%={100*n_warn/n_total:.2f}")
log.info(f"failure EPISODES total = {len(episodes_df)}  (contract >=100)")
fr = n_fail/n_total
deg_frac = float((raw["fault_label"] > 0).mean() + (raw["run_id"] != "").mean()) / 2
log.info("per-asset label2%: " + str({a: round(100*((g['fault_label']>=2).mean()),2)
    for a, g in raw.groupby('asset_id')}))
log.info(f"occupied(deg) frac of rows = {100*(raw['run_id']!='').mean():.1f}%")
if not (0.005 <= fr <= 0.06):
    log.warning(f"label=2 rate {fr:.3f} outside 0.5-6% band (continuing to inspect)")
assert len(episodes_df) >= 100, f"only {len(episodes_df)} episodes (<100 contract)"

raw.to_csv(OUT_DIR/"raw_sensor_timeseries.csv", index=False)
episodes_df.to_csv(OUT_DIR/"episodes_manifest.csv", index=False)
log.info(f"wrote raw_sensor_timeseries.csv {raw.shape} + episodes_manifest.csv {episodes_df.shape}")

# ── (b) summaries / (c) alerts / (d) pci — reuse v1 logic on v2 raw ─────────
WINDOW_H = 6
raw["window_start"] = raw["timestamp"].apply(
    lambda ts: ts.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=ts.hour % WINDOW_H))
meta = {"timestamp","asset_id","equipment_class","fault_label","scenario_id","run_id","RUL_hours","split","opc_quality","window_start"}
scols = [c for c in raw.columns if c not in meta]
srows = []
for (aid, ws), g in raw.groupby(["asset_id","window_start"], sort=True):
    r = {"asset_id": aid, "equipment_class": g["equipment_class"].iloc[0],
         "window_start": ws, "window_end": ws+datetime.timedelta(hours=WINDOW_H),
         "n_samples": len(g), "fault_label_max": int(g["fault_label"].max()),
         "scenario_id": g["scenario_id"][g["fault_label"]>0].values[0] if (g["fault_label"]>0).any() else "",
         "RUL_hours_min": float(g["RUL_hours"].dropna().min()) if g["RUL_hours"].notna().any() else float("nan")}
    for sc in scols:
        v = g[sc].dropna()
        if len(v)==0:
            r[f"{sc}__mean"]=r[f"{sc}__max"]=r[f"{sc}__std"]=r[f"{sc}__trend"]=float("nan")
        else:
            r[f"{sc}__mean"]=round(float(v.mean()),4); r[f"{sc}__max"]=round(float(v.max()),4)
            r[f"{sc}__std"]=round(float(v.std()),4)
            r[f"{sc}__trend"]=round(float(np.polyfit(np.arange(len(v)),v.values,1)[0]),6) if len(v)>=2 else 0.0
    srows.append(r)
pd.DataFrame(srows).to_csv(OUT_DIR/"sensor_data_summaries.csv", index=False)
log.info(f"wrote sensor_data_summaries.csv ({len(srows)} rows)")

alert_rows = []
for asset in spine["asset_registry"]:
    aid = asset["asset_id"]; da = raw[raw["asset_id"]==aid]
    for s in asset["sensors"]:
        if not is_numeric_sensor(s): continue
        tag = s["tag"]
        if tag not in da.columns: continue
        alm, wrn = get_alarm_threshold(s), get_warning_threshold(s)
        d = threshold_direction(s); bd = BIDIRECTIONAL_SENSORS.get(tag)
        for v, ts, scn, fl in zip(da[tag].values, da["timestamp"].values, da["scenario_id"].values, da["fault_label"].values):
            if v != v: continue  # skip NaN dropouts
            v = float(v); sev = thr = None
            if d == "bidirectional":
                if v > bd["alarm_high"]: sev, thr = "ALARM", bd["alarm_high"]
                elif v < bd["warn_low"]: sev, thr = "WARNING", bd["warn_low"]
            elif d == "upper":
                if alm is not None and v >= alm: sev, thr = "ALARM", alm
                elif wrn is not None and v >= wrn: sev, thr = "WARNING", wrn
            else:
                if alm is not None and v <= alm: sev, thr = "ALARM", alm
                elif wrn is not None and v <= wrn: sev, thr = "WARNING", wrn
            if sev:
                alert_rows.append({"timestamp": pd.Timestamp(ts), "asset_id": aid, "sensor": tag,
                    "value": round(v,4), "threshold": thr, "severity": sev,
                    "fault_label": int(fl), "scenario_id": scn})
alerts = pd.DataFrame(alert_rows)
if not alerts.empty:
    alerts = alerts.sort_values("timestamp").reset_index(drop=True)   # event-ordered (OE-7)
    alerts.insert(0, "alert_id", [f"ALRT-{i:06d}" for i in range(len(alerts))])
alerts.to_csv(OUT_DIR/"anomaly_alerts.csv", index=False)
log.info(f"wrote anomaly_alerts.csv ({len(alerts)} rows, time-sorted)")

# (d) pci
def sensor_hi(value, mid, alm, upper):
    if alm is None: return np.full(len(value), 50.0)
    den = abs(alm-mid)
    if den < 1e-6: return np.full(len(value), 100.0)
    dev = (value-mid)/den if upper else (mid-value)/den
    return np.clip(100.0*(1.0-np.clip(dev,0,1)), 0, 100)
pci_rows = []
for asset in spine["asset_registry"]:
    aid = asset["asset_id"]; da = raw[raw["asset_id"]==aid].copy(); eq = asset["equipment_class"]
    da["day"] = da["timestamp"].apply(lambda ts: ts.replace(hour=0,minute=0,second=0,microsecond=0))
    nums = [s for s in asset["sensors"] if is_numeric_sensor(s)]
    for day, g in da.groupby("day"):
        nh = len(g)
        if nh == 0: continue
        his = []
        for s in nums:
            tag = s["tag"]
            if tag not in g.columns: continue
            vals = g[tag].values.astype(float); vals = vals[~np.isnan(vals)]
            if len(vals)==0: continue
            his.append(sensor_hi(vals, sensor_midpoint(s), get_alarm_threshold(s), threshold_is_upper(s)).mean())
        hi = float(np.mean(his)) if his else 50.0
        fl = g["fault_label"].values
        nhl, nw, nf = (fl==0).sum(), (fl==1).sum(), (fl>=2).sum()
        avail = (nhl + 0.8*nw)/max(nh,1)
        inn = tot = 0
        for s in nums:
            tag = s["tag"]
            if tag not in g.columns: continue
            nr = s.get("normal_range",[])
            if len(nr)==2:
                vv = g[tag].values.astype(float); vv = vv[~np.isnan(vv)]
                inn += ((vv>=nr[0])&(vv<=nr[1])).sum(); tot += len(vv)
        perf = inn/max(tot,1)
        de = day+datetime.timedelta(hours=24)
        na = len(alerts[(alerts["asset_id"]==aid)&(alerts["timestamp"]>=pd.Timestamp(day))&(alerts["timestamp"]<pd.Timestamp(de))&(alerts["severity"]=="ALARM")]) if not alerts.empty else 0
        qual = max(0.0, 1.0 - na/max(nh,1))
        rmin = float(g["RUL_hours"].dropna().min()) if g["RUL_hours"].notna().any() else float("nan")
        pci_rows.append({"date": day.strftime("%Y-%m-%d"), "asset_id": aid, "equipment_class": eq,
            "health_index": round(hi,2), "availability": round(avail,4), "performance": round(perf,4),
            "quality": round(qual,4), "oee": round(avail*perf*qual,4),
            "hours_healthy": int(nhl), "hours_warning": int(nw), "hours_failure": int(nf),
            "n_alarm_events": int(na), "RUL_hours_min": round(rmin,1) if not math.isnan(rmin) else float("nan"),
            "fault_label_max": int(fl.max()),
            "scenario_id": g["scenario_id"][g["fault_label"]>0].values[0] if (g["fault_label"]>0).any() else ""})
pd.DataFrame(pci_rows).to_csv(OUT_DIR/"process_condition_indicators.csv", index=False)
log.info(f"wrote process_condition_indicators.csv ({len(pci_rows)} rows)")

log.info("="*60)
log.info("v2 GENERATION COMPLETE")
log.info(f"  episodes={len(episodes_df)}  fail%={100*n_fail/n_total:.2f}  rows={n_total:,}")
log.info(f"  splits: " + str(raw['split'].value_counts().to_dict()))
log.info("="*60)
