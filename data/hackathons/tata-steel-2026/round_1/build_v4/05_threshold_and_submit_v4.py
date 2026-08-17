"""
V4 finalisation — score-aware threshold sweep + submission generation.

Inputs:
  - oof_v4.parquet         (cols: oof_lgb, oof_xgb, oof_cat, oof_meta, Y)
  - test_meta_v4.parquet   (cols: test_lgb, test_xgb, test_cat, test_meta)
  - test_v4.parquet        (cols: CoilID, X1..X49, ... feature cols)

Outputs:
  - chosen_threshold_v4.json
  - expected_submission.csv       (CoilID, Y)
  - submission_T_balanced.csv     (alt: precision-leaning)
  - submission_T_v2_style.csv     (alt: super-low T, max recall)
  - submission_v4.zip
"""

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4 = BASE / "build_v4"


def main() -> None:
    oof = pd.read_parquet(V4 / "oof_v4.parquet")
    test_meta = pd.read_parquet(V4 / "test_meta_v4.parquet")
    test_feat = pd.read_parquet(V4 / "test_v4.parquet")

    assert len(test_meta) == 339, f"test_meta rows={len(test_meta)}, expected 339"
    assert len(test_feat) == 339, f"test_v4 rows={len(test_feat)}, expected 339"

    p_oof = oof["oof_meta"].values
    y_oof = oof["Y"].values
    p_test = test_meta["test_meta"].values

    # Score-aware sweep: exact unique-threshold sweep (same strategy as V3).
    uniq = np.sort(np.unique(np.concatenate([p_oof, [0.0, 1.0]])))
    # Use mid-points between adjacent unique probas so every (recall, precision)
    # transition is exercised; keeps the sweep stable on ties.
    cuts = np.r_[uniq[0] - 1e-6, 0.5 * (uniq[:-1] + uniq[1:]), uniq[-1] + 1e-6]

    rows = []
    for t in cuts:
        pred = (p_oof >= t).astype(int)
        tp = int(((pred == 1) & (y_oof == 1)).sum())
        fp = int(((pred == 1) & (y_oof == 0)).sum())
        fn = int(((pred == 0) & (y_oof == 1)).sum())
        n_pos = int(pred.sum())
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        score = (recall + precision) / 2.0 * 100.0
        rows.append({
            "threshold": float(t),
            "score": score,
            "recall": recall,
            "precision": precision,
            "n_pos": n_pos,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        })

    sweep = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    sweep.to_csv(V4 / "threshold_sweep_v4_final.csv", index=False)

    best = sweep.iloc[0]
    T_max = float(best["threshold"])
    best_score = float(best["score"])
    print(f"Best OOF score: {best_score:.4f} at T={T_max:.6f}")
    print(f"  recall={best['recall']:.4f}  precision={best['precision']:.4f}  n_pos={int(best['n_pos'])}")

    # Alternate thresholds for safety variants.
    # T_balanced: maximise harmonic mean of (R, P) -> precision-leaning
    sweep["hmean"] = 2 * sweep["recall"] * sweep["precision"] / (sweep["recall"] + sweep["precision"]).replace(0, np.nan)
    balanced_row = sweep.loc[sweep["hmean"].idxmax()]
    T_balanced = float(balanced_row["threshold"])
    # T_v2_style: ultra-low threshold (~v2 maximum-recall posture)
    T_v2_style = 0.001

    # Build submissions
    coilid = test_feat["CoilID"].values
    proba = p_test

    out_main = pd.DataFrame({"CoilID": coilid, "Y": (proba >= T_max).astype(int)})
    out_balanced = pd.DataFrame({"CoilID": coilid, "Y": (proba >= T_balanced).astype(int)})
    out_v2style = pd.DataFrame({"CoilID": coilid, "Y": (proba >= T_v2_style).astype(int)})

    for df, name in [(out_main, "expected_submission.csv"),
                     (out_balanced, "submission_T_balanced.csv"),
                     (out_v2style, "submission_T_v2_style.csv")]:
        assert df.shape == (339, 2)
        assert set(df.columns) == {"CoilID", "Y"}
        assert df["Y"].isin([0, 1]).all()
        df.to_csv(V4 / name, index=False)
        n_pos = int(df["Y"].sum())
        print(f"  wrote {name}: n_pos={n_pos} ({n_pos / 339 * 100:.1f}%)")

    chosen = {
        "chosen_threshold": T_max,
        "strategy": "maximize_(recall+precision)/2_exact_unique_thresholds",
        "predicted_lb_score": best_score,
        "oof_recall": float(best["recall"]),
        "oof_precision": float(best["precision"]),
        "oof_n_positives": int(best["n_pos"]),
        "oof_total": int(len(y_oof)),
        "oof_positive_rate": float(best["n_pos"] / len(y_oof)),
        "comparison": {
            "T_max_score": {
                "threshold": T_max,
                "score": best_score,
                "recall": float(best["recall"]),
                "precision": float(best["precision"]),
                "n_pos": int(best["n_pos"]),
                "test_n_pos": int(out_main["Y"].sum()),
            },
            "T_balanced": {
                "threshold": T_balanced,
                "score": float(balanced_row["score"]),
                "recall": float(balanced_row["recall"]),
                "precision": float(balanced_row["precision"]),
                "n_pos": int(balanced_row["n_pos"]),
                "test_n_pos": int(out_balanced["Y"].sum()),
            },
            "T_v2_style": {
                "threshold": T_v2_style,
                "test_n_pos": int(out_v2style["Y"].sum()),
            },
        },
        "v2_lb_score_for_reference": 50.19,
        "v3_predicted_lb": 53.35,
        "delta_vs_v2": best_score - 50.19,
        "delta_vs_v3": best_score - 53.35,
        "top10_target": 70.0,
        "on_track_for_top10": best_score >= 70.0,
    }
    (V4 / "chosen_threshold_v4.json").write_text(json.dumps(chosen, indent=2))
    print("\nWrote chosen_threshold_v4.json")

    # Zip
    zip_path = V4 / "submission_v4.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(V4 / "expected_submission.csv", "expected_submission.csv")
        zf.write(V4 / "chosen_threshold_v4.json", "chosen_threshold_v4.json")
        zf.write(V4 / "v4_final_features.json", "v4_final_features.json")
        zf.write(V4 / "v4_stacking_summary.json", "v4_stacking_summary.json")
        zf.write(V4 / "coilid_signal_analysis.md", "coilid_signal_analysis.md")
    print(f"Wrote {zip_path}")
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            print(f"  - {info.filename} ({info.file_size / 1024:.1f} KB)")

    print("\n" + "=" * 60)
    print("V4 SUBMISSION SUMMARY")
    print("=" * 60)
    print(f"  Predicted LB score:  {best_score:.2f}")
    print(f"  Delta vs V2 (50.19): {best_score - 50.19:+.2f}")
    print(f"  Delta vs V3 (53.35): {best_score - 53.35:+.2f}")
    print(f"  Top 10 target (70):  {'LIKELY' if best_score >= 70 else 'NO — needs V5 (physics features)'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
