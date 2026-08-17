
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

V1_DIR = "data/hackathons/tata-steel-2026/round_1/build_v1"
V2_DIR = "data/hackathons/tata-steel-2026/round_1/build_v2"

print("=" * 60)
print("STEP 5: V1 vs V2 Comparison Report")
print("=" * 60)

v1_oof_auc = 0.827
v1_recall_at_02 = 0.924
v1_prec_at_r1 = 0.059
v1_test_pos_rate = 46.3
v1_min_fold_iters = 1

cv2  = json.load(open(f"{V2_DIR}/cv_summary_v2.json"))
thr2 = json.load(open(f"{V2_DIR}/chosen_threshold_v2.json"))
sub2 = pd.read_csv(f"{V2_DIR}/expected_submission.csv")
oof2 = pd.read_parquet(f"{V2_DIR}/oof_v2.parquet")

y2     = oof2["Y"].values.astype(int)
prob2  = oof2["oof_proba"].values
v2_oof_auc = float(roc_auc_score(y2, prob2))
v2_chosen_thr    = thr2["chosen_threshold"]
v2_chosen_recall = thr2["chosen_recall"]
v2_chosen_prec   = thr2["chosen_precision"]
v2_criteria_met  = thr2["criteria_met"]
v2_test_pos_rate = 100.0 * sub2["Y"].sum() / len(sub2)
v2_min_fold_iters = cv2["min_fold_iters"]
v2_prec_at_r1 = thr2["T_b_recall1"]["precision"] if thr2.get("T_b_recall1") else None
v2_recall_at_p90 = thr2["T_a_prec90"]["recall"] if (thr2.get("T_a_prec90") and thr2["T_a_prec90"]) else 0.0

print(f"OOF AUC: v1={v1_oof_auc:.4f}  v2={v2_oof_auc:.4f}  delta={v2_oof_auc-v1_oof_auc:+.4f}")
print(f"Prec @ R=1.0: v1={v1_prec_at_r1:.4f}  v2={v2_prec_at_r1:.4f}  delta={v2_prec_at_r1-v1_prec_at_r1:+.4f}")
print(f"Recall @ P>=0.90: v1=0.0  v2={v2_recall_at_p90:.4f}")
print(f"Test pos rate: v1={v1_test_pos_rate:.1f}%  v2={v2_test_pos_rate:.1f}%  delta={v2_test_pos_rate-v1_test_pos_rate:+.1f}%")
print(f"Min fold iters: v1={v1_min_fold_iters}  v2={v2_min_fold_iters}  delta={v2_min_fold_iters-v1_min_fold_iters:+d}")
print(f"Criteria met: v1=NO  v2={"YES" if v2_criteria_met else "NO"}")

print("
Per-fold metrics:")
for fm in cv2["fold_metrics"]:
    print(f"  Fold {fm["fold"]}: AUC={fm["auc"]:.4f}  iter={fm["best_round"]}  pos_smote={fm["pos_before_smote"]}->{fm["pos_after_smote"]}")

print(f"
V2 criteria met: {v2_criteria_met}")
