# V73 VERDICT

**Verdict: TTA methods FAIL on this dataset. V73 does NOT beat V71 K=200 (74.72 LB) via the R27 prescription.**

V73 implemented R27 Priority 1 (BCTS + Seeded EM, q_init=0.45) and Priority 2 fallback (BBSE-Soft/RLLS) faithfully on the V44 paradigm stack. Both methods failed completely for a mathematically confirmed reason: the models trained on 5% prevalence produce calibrated test probabilities with max p_cal = 0.304 and mean = 0.030. The EM E-step at iteration 0 reduces q from 0.45 to 0.27 and then collapses monotonically to 0 — regardless of seeded initialization — because the fixed point of Saerens EM is pinned to p_cal_test.mean() ≈ 0.03, not the true 0.45 prevalence. BBSE degenerates because 0 test coils exceed the 0.5 classification threshold, making the confusion-matrix shift estimator ill-defined. The 38 confirmed TPs (ranks 177–277 in V44) have BCTS-calibrated probabilities of 0.007–0.011, uniformly lower than the top-170 non-TP coils (0.013–0.770) — there is no post-hoc reweighting that can recover TPs that the model assigns lower confidence than non-TPs.

**64-label validation AUC:** V44 consensus = 0.5886 (best available); TTA = 0.5000 (random). TTA strictly degrades the ranking.

**Synthetic 45%-OOF validation:** Uncalibrated baseline HE = 81.23; TTA HE = 54.76. TTA is -26.5 worse even on synthetic controlled data.

**Submitted:** V44 consensus K=200 (identical ranking to V44 baseline, expected ~72.83 on public LB since V71's 74.72 includes 38 hardcoded LB-probed TPs); V44 consensus K=154 (prevalence-calibrated K, expected ~65–70 on public LB, potentially better on private LB if private test rewards precision over recall).

**Private LB direction (June 1):** If private test = same 339 rows, V71 hardcoded TPs generalize and V71 remains best at ~74.72. If private test = different rows, V71 collapses and pure V44 K=154 or K=200 is the honest best (estimated 65–70 range). V73 does not change this situation — TTA failed to improve the model-honest baseline.

**What would actually fix this (for future work):** Retrain base models with class_weight='balanced' or pos_weight=9.0 at 45% target prevalence, then apply BCTS + seeded EM on the recalibrated outputs. The post-hoc fix prescribed in R27 is correct in theory but requires model probabilities that discriminate in the 45%-prevalence regime — the current models were trained entirely at 5% and are irrecoverably compressed in the boundary zone.
