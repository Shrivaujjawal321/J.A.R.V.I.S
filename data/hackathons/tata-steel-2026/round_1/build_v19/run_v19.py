"""
BUILD V19 -- TabNet + Test-Time Augmentation
Tata Steel AI Hackathon 2026, Round 1
"""
import json, warnings, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

BASE    = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V5_DIR  = BASE / "build_v5"
OUT_DIR = BASE / "build_v19"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED=42; N_FOLDS=5; TTA_ROUNDS=20; TTA_NOISE=0.01
TARGET="Y"

print("=== BUILD V19: TabNet + TTA ===\n")
train = pd.read_parquet(V5_DIR/"train_v5.parquet")
test  = pd.read_parquet(V5_DIR/"test_v5.parquet")
with open(V5_DIR/"feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]
y = train[TARGET].values.astype(int)
print(f"train: {train.shape}  test: {test.shape}  features: {len(v5_features)}")
print(f"class balance: {y.mean():.4f} ({y.sum()} pos / {len(y)} total)\n")

def apply_gate(proba, df):
    p = proba.copy()
    p[(df["X42"].values > 0.025067)|(df["X39"].values >= 169)] = 0.0
    return p

def he_score(y_true, y_proba):
    best, best_t = 0.0, 0.5
    for t in np.linspace(0.01, 0.99, 500):
        pred = (y_proba>=t).astype(int)
        tp = ((pred==1)&(y_true==1)).sum()
        fp = ((pred==1)&(y_true==0)).sum()
        fn = ((pred==0)&(y_true==1)).sum()
        r=tp/max(tp+fn,1); p=tp/max(tp+fp,1); s=(r+p)/2
        if s>best: best=s; best_t=t
    return best, best_t

scaler = StandardScaler()
Xtr = scaler.fit_transform(np.nan_to_num(train[v5_features].values, nan=0.0))
Xte = scaler.transform(np.nan_to_num(test[v5_features].values, nan=0.0))

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_arr = np.zeros(len(y))
fold_aucs=[]; test_preds=[]; test_preds_nt=[]

for fold,(tr,va) in enumerate(skf.split(Xtr,y)):
    print(f"  Fold {fold+1}/{N_FOLDS}...")
    Xtr2,Xva2=Xtr[tr],Xtr[va]; ytr,yva=y[tr],y[va]
    pos_w=(ytr==0).sum()/max(ytr.sum(),1)
    W=np.where(ytr==1,pos_w,1.0).astype(float)
    m=TabNetClassifier(n_d=16,n_a=16,n_steps=3,gamma=1.5,n_independent=2,n_shared=2,
        lambda_sparse=1e-4,optimizer_fn=torch.optim.Adam,optimizer_params={"lr":1e-2},
        scheduler_fn=torch.optim.lr_scheduler.StepLR,scheduler_params={"step_size":10,"gamma":0.95},
        mask_type="entmax",verbose=0,seed=SEED+fold,device_name="auto")
    m.fit(Xtr2,ytr,eval_set=[(Xva2,yva)],eval_metric=["auc"],
          max_epochs=200,patience=30,batch_size=256,virtual_batch_size=64,weights=W)
    vp=m.predict_proba(Xva2)[:,1]; oof_arr[va]=vp
    fa=roc_auc_score(yva,vp); fold_aucs.append(fa)
    print(f"    fold {fold+1} AUC: {fa:.4f}")
    test_preds_nt.append(m.predict_proba(Xte)[:,1])
    rng=np.random.default_rng(SEED+fold)
    runs=[m.predict_proba(Xte+rng.normal(0,TTA_NOISE,Xte.shape))[:,1] for _ in range(TTA_ROUNDS)]
    test_preds.append(np.mean(runs,axis=0))

tabnet_auc=roc_auc_score(y,oof_arr)
Tp_TTA=np.mean(test_preds,axis=0); Tp_nTTA=np.mean(test_preds_nt,axis=0)
print(f"\nTabNet OOF AUC: {tabnet_auc:.4f}")
print(f"Per-fold AUCs: {[round(a,4) for a in fold_aucs]}")

v5_oof=pd.read_parquet(V5_DIR/"oof_v5.parquet")
v5_te=pd.read_parquet(V5_DIR/"test_meta_v5.parquet")
# Known cols from inspection: oof_meta, test_meta
v5op=v5_oof["oof_meta"].values; v5tp=v5_te["test_meta"].values
v5auc=roc_auc_score(y,v5op)
print(f"V5 OOF meta AUC: {v5auc:.4f}")

print("\n=== Phase C -- Blends ===\n")
cfgs={
  "TabNet-only (TTA)":      (Tp_TTA, oof_arr),
  "TabNet-only (no-TTA)":   (Tp_nTTA, oof_arr),
  "V5+TabNet 80/20 (TTA)":  (0.8*v5tp+0.2*Tp_TTA, 0.8*v5op+0.2*oof_arr),
  "V5+TabNet 70/30 (TTA)":  (0.7*v5tp+0.3*Tp_TTA, 0.7*v5op+0.3*oof_arr),
  "V5+TabNet 50/50 (TTA)":  (0.5*v5tp+0.5*Tp_TTA, 0.5*v5op+0.5*oof_arr),
  "V5-only (reference)":    (v5tp, v5op),
}
res={}
for name,(tp,op) in cfgs.items():
    auc=roc_auc_score(y,op); sc,th=he_score(y,op)
    res[name]={"oof_auc":auc,"he_score":sc,"thresh":th,"test_proba":tp,"oof_proba":op}
    print(f"  {name:38s} OOF={auc:.4f} HE={sc:.4f} t={th:.4f}")

best=max(res,key=lambda k:res[k]["oof_auc"])
if "+" in best:
    d=res[best]["oof_auc"]-v5auc
    print(f"\nBlend lift: {d:+.4f}")
    if d<0.002:
        print("  WARNING: lift<0.002 -- V10 blend disaster risk. Falling back to V5-only.")
        best="V5-only (reference)"
ch=res[best]
print(f"\nChosen: {best}  OOF={ch['oof_auc']:.4f}  HE={ch['he_score']:.4f}")

print("\n=== Phase D -- Gate + Submission ===\n")
tpg=apply_gate(ch["test_proba"],test); ng=int((tpg<ch["test_proba"]).sum())
opg=apply_gate(ch["oof_proba"],train); scg,thg=he_score(y,opg)
print(f"Gate zeroed: {ng}  HE(gated)={scg:.4f}  t={thg:.4f}")
preds=(tpg>=thg).astype(int); np_=int(preds.sum())
print(f"Positives: {np_}/{len(preds)}")

id_col=test["CoilID"].values if "CoilID" in test.columns else np.arange(len(test))
sub=pd.DataFrame({"id":id_col,"target":preds})
sp=OUT_DIR/"expected_submission.csv"; sub.to_csv(sp,index=False)
zp=OUT_DIR/"submission_v19.zip"
with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as zf: zf.write(sp,"expected_submission.csv")
print(f"Saved: {sp}")

print("\n=== Bootstrap CI ===\n")
rng_b=np.random.default_rng(SEED); bs=[]
for _ in range(1000):
    idx=rng_b.integers(0,len(y),len(y)); s,_=he_score(y[idx],opg[idx]); bs.append(s)
bm=float(np.mean(bs)); bl=float(np.percentile(bs,2.5)); bh=float(np.percentile(bs,97.5))
print(f"Bootstrap: {bm:.4f}  95% CI [{bl:.4f}, {bh:.4f}]")

lb_est=scg*100+2.67
print(f"Calibrated LB est: {lb_est:.2f}  (gap vs V4 56.98: {lb_est-56.98:+.2f})")

td_m=float(np.abs(Tp_TTA-Tp_nTTA).mean()); td_s=float(np.abs(Tp_TTA-Tp_nTTA).std())
print(f"TTA delta on test: mean|delta|={td_m:.5f} std={td_s:.5f}")

out={
    "tabnet_oof_auc":float(tabnet_auc),
    "tabnet_oof_auc_per_fold":[float(a) for a in fold_aucs],
    "v5_meta_oof_auc":float(v5auc),
    "chosen_config":best,
    "chosen_oof_auc":float(ch["oof_auc"]),
    "chosen_he_score_gated":float(scg),
    "chosen_threshold":float(thg),
    "bootstrap_mean":bm,"bootstrap_ci_lo":bl,"bootstrap_ci_hi":bh,
    "calibrated_lb_est":float(lb_est),
    "n_positives_test":np_,"n_gated_test":ng,
    "tta_delta_mean":td_m,"tta_delta_std":td_s,
    "all_configs":{k:{"oof_auc":float(v["oof_auc"]),"he_score":float(v["he_score"]),"thresh":float(v["thresh"])} for k,v in res.items()}
}
with open(OUT_DIR/"v19_results.json","w") as f: json.dump(out,f,indent=2)

print("\n=== V19 COMPLETE ===")
print(f"TabNet OOF AUC:          {tabnet_auc:.4f}")
print(f"V5 meta OOF AUC (ref):   {v5auc:.4f}")
print(f"Chosen config:           {best}")
print(f"Chosen OOF AUC:          {ch['oof_auc']:.4f}")
print(f"HE OOF score (gated):    {scg:.4f}")
print(f"Calibrated LB estimate:  {lb_est:.2f}")
print(f"Test positives:          {np_}")
