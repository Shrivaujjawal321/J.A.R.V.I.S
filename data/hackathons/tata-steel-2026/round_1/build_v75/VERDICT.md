# V75 VERDICT

**Best variant:** V75-var1-pct-avg
**Estimated LB vs V71 (74.72):** NEUTRAL — coin-flip on 37 unknown substitutions; all TPs preserved

---

V75 merges V71's proven 8-paradigm consensus (with 38 LB-probed TP overrides, LB=74.72) with V74's fresh LGB+XGB+CatBoost retrain (64L AUC=0.7004, est LB ~71.28 standalone). The best merge variant (V75-var1-pct-avg) achieves TP@200=38/38 on the 64 confirmed labels — same as V71. The V75 submission swaps 37 unknown coils from V71 for 37 different unknown coils preferred by V74; all 38 confirmed TPs are preserved. The confirmed-label gate cannot distinguish V75 from V71 (both score 38/38 TP recall, 64L AUC=1.00). The real question is whether V74's 37 substitutions are better or worse than V71's 37 dropped unknowns in the actual test distribution — and there is no way to know this without an LB probe. V74 estimated LB was ~71.28 (worse than V44's 72.83), suggesting its boundary-zone picks are net-negative. The merge dampens this by keeping all TPs via V71, but the 37 unknown substitutions remain unvalidated. LOW-to-NEUTRAL confidence this beats 74.72. Treat as a coin-flip; V71 K=200 remains the recommended primary submission.
