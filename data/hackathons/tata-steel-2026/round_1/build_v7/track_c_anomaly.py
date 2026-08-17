"""
Track C: Anomaly Detection as Primary Classifier
Phase A: 6 AD methods
Phase B: 7-way LR ensemble
Phase C: Hard defect recovery
"""
import numpy as np, pandas as pd, json, os, warnings
warnings.filterwarnings("ignore")
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import EmpiricalCovariance
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler as SS2
import torch, torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
OUT  = os.path.join(BASE, "build_v7")
print("Loading...")
train  = pd.read_parquet(os.path.join(BASE,"build_v5/train_v5.parquet"))
test   = pd.read_parquet(os.path.join(BASE,"build_v5/test_v5.parquet"))
oof_v5 = pd.read_parquet(os.path.join(BASE,"build_v5/oof_v5.parquet"))
with open(os.path.join(BASE,"build_v5/feature_list_v5.json")) as f: FEATS=json.load(f)["features"]
FTR=[f for f in FEATS if f in train.columns]; FTE=[f for f in FEATS if f in test.columns]
print(f"Train {train.shape} Test {test.shape} Feats {len(FTR)} Defects {int(train['Y'].sum())}/{len(train)}")
Xtr=train[FTR].fillna(0).values.astype(np.float32); ytr=train["Y"].values
Xte=test[FTE].fillna(0).values.astype(np.float32)
Xnorm=Xtr[ytr==0]
sc=StandardScaler(); Xnsc=sc.fit_transform(Xnorm); Xtrsc=sc.transform(Xtr); Xtesc=sc.transform(Xte)
print(f"Normal rows: {len(Xnorm)}")

def rp2(s,y,n=300):
    best=0.0
    for t in np.percentile(s,np.linspace(0,100,n)):
        p_=(s>=t).astype(int); tp=((p_==1)&(y==1)).sum(); fp=((p_==1)&(y==0)).sum(); fn=((p_==0)&(y==1)).sum()
        v=(tp/(tp+fp+1e-9)+tp/(tp+fn+1e-9))/2
        if v>best: best=v
    return best
def auc(s,y):
    try: return float(roc_auc_score(y,s))
    except: return 0.0

RES={}

# M1
print("\n[M1] IsolationForest...")
IF_=IsolationForest(n_estimators=300,contamination=0.049,max_samples="auto",random_state=42,n_jobs=-1)
IF_.fit(Xnorm); s1tr=-IF_.decision_function(Xtr); s1te=-IF_.decision_function(Xte)
try:
    fi=np.mean([e.feature_importances_ for e in IF_.estimators_],axis=0)
    top1=[(FTR[i],round(float(fi[i]),4)) for i in np.argsort(fi)[::-1][:5]]
except Exception:
    top1=[]
RES["M1_IF"]={"auc":round(auc(s1tr,ytr),4),"rp2":round(rp2(s1tr,ytr)*100,2),"top":top1,"str":s1tr.tolist(),"ste":s1te.tolist()}
print(f"  AUC={RES['M1_IF']['auc']}  RP2={RES['M1_IF']['rp2']}")

# M2
print("[M2] OneClassSVM...")
oc=OneClassSVM(kernel="rbf",gamma="scale",nu=0.05); oc.fit(Xnsc)
s2tr=-oc.decision_function(Xtrsc); s2te=-oc.decision_function(Xtesc)
RES["M2_OCSVM"]={"auc":round(auc(s2tr,ytr),4),"rp2":round(rp2(s2tr,ytr)*100,2),"top":[],"str":s2tr.tolist(),"ste":s2te.tolist()}
print(f"  AUC={RES['M2_OCSVM']['auc']}  RP2={RES['M2_OCSVM']['rp2']}")

# M3
print("[M3] LOF...")
lof=LocalOutlierFactor(n_neighbors=20,contamination=0.049,novelty=True); lof.fit(Xnsc)
s3tr=-lof.decision_function(Xtrsc); s3te=-lof.decision_function(Xtesc)
RES["M3_LOF"]={"auc":round(auc(s3tr,ytr),4),"rp2":round(rp2(s3tr,ytr)*100,2),"top":[],"str":s3tr.tolist(),"ste":s3te.tolist()}
print(f"  AUC={RES['M3_LOF']['auc']}  RP2={RES['M3_LOF']['rp2']}")

# M4
print("[M4] Mahalanobis...")
try:
    ec=EmpiricalCovariance(); ec.fit(Xnsc)
    s4tr=ec.mahalanobis(Xtrsc); s4te=ec.mahalanobis(Xtesc); m4n="full"
except Exception as e:
    print(f"  Singular ({e}), diagonal fallback")
    mu=Xnsc.mean(0); std=Xnsc.std(0)+1e-9
    s4tr=np.sum(((Xtrsc-mu)/std)**2,1); s4te=np.sum(((Xtesc-mu)/std)**2,1); m4n="diagonal"
RES["M4_Mah"]={"auc":round(auc(s4tr,ytr),4),"rp2":round(rp2(s4tr,ytr)*100,2),"top":[],"note":m4n,"str":s4tr.tolist(),"ste":s4te.tolist()}
print(f"  AUC={RES['M4_Mah']['auc']}  RP2={RES['M4_Mah']['rp2']}  ({m4n})")

# M5
print("[M5] Autoencoder (200ep)...")
class AE(nn.Module):
    def __init__(self,d):
        super().__init__()
        self.enc=nn.Sequential(nn.Linear(d,32),nn.Tanh(),nn.Linear(32,8),nn.Tanh())
        self.dec=nn.Sequential(nn.Linear(8,32),nn.Tanh(),nn.Linear(32,d))
    def forward(self,x): return self.dec(self.enc(x))
d=Xnsc.shape[1]; ae=AE(d); opt=torch.optim.Adam(ae.parameters(),lr=1e-3); crit=nn.MSELoss()
Xnt=torch.tensor(Xnsc,dtype=torch.float32)
loader=DataLoader(TensorDataset(Xnt),batch_size=64,shuffle=True)
ae.train()
for ep in range(200):
    for (b,) in loader:
        opt.zero_grad(); loss=crit(ae(b),b); loss.backward(); opt.step()
    if (ep+1)%50==0: print(f"  ep{ep+1}/200 loss={loss.item():.6f}")
ae.eval()
with torch.no_grad():
    Xtrt=torch.tensor(Xtrsc,dtype=torch.float32); Xtet=torch.tensor(Xtesc,dtype=torch.float32)
    s5tr=((Xtrt-ae(Xtrt))**2).mean(1).numpy(); s5te=((Xtet-ae(Xtet))**2).mean(1).numpy()
RES["M5_AE"]={"auc":round(auc(s5tr,ytr),4),"rp2":round(rp2(s5tr,ytr)*100,2),"top":[],"str":s5tr.tolist(),"ste":s5te.tolist()}
print(f"  AUC={RES['M5_AE']['auc']}  RP2={RES['M5_AE']['rp2']}")

# M6
print("[M6] PCA ReconError (10 pc)...")
pca=PCA(n_components=10,random_state=42); pca.fit(Xnsc)
def pe(X): return np.sum((X-pca.inverse_transform(pca.transform(X)))**2,1)
s6tr=pe(Xtrsc); s6te=pe(Xtesc)
wl=np.abs(pca.components_).T@pca.explained_variance_ratio_
top6=[(FTR[i],round(float(wl[i]),4)) for i in np.argsort(wl)[::-1][:5]]
RES["M6_PCA"]={"auc":round(auc(s6tr,ytr),4),"rp2":round(rp2(s6tr,ytr)*100,2),"top":top6,
               "var10pc":round(float(pca.explained_variance_ratio_.sum()),4),"str":s6tr.tolist(),"ste":s6te.tolist()}
print(f"  AUC={RES['M6_PCA']['auc']}  RP2={RES['M6_PCA']['rp2']}  var={RES['M6_PCA']['var10pc']}")

print("\n=== Phase B: 7-way LR Ensemble ===")
v5tr=oof_v5["oof_meta"].values
TMP=os.path.join(BASE,"build_v5/test_meta_v5.parquet")
if os.path.exists(TMP):
    tmv5=pd.read_parquet(TMP); print("test_meta cols:",list(tmv5.columns))
    v5te=tmv5["meta"].values if "meta" in tmv5.columns else tmv5.iloc[:,0].values
else:
    v5te=np.zeros(len(test))
Xmtr=np.column_stack([s1tr,s2tr,s3tr,s4tr,s5tr,s6tr,v5tr])
Xmte=np.column_stack([s1te,s2te,s3te,s4te,s5te,s6te,v5te])
oens=np.zeros(len(ytr))
for fold,(ti,vi) in enumerate(StratifiedKFold(5,shuffle=True,random_state=42).split(Xmtr,ytr)):
    pipe=make_pipeline(SS2(),LogisticRegression(C=1.0,max_iter=2000,random_state=42))
    pipe.fit(Xmtr[ti],ytr[ti]); oens[vi]=pipe.predict_proba(Xmtr[vi])[:,1]
    print(f"  Fold {fold+1}")
ea=auc(oens,ytr); er=rp2(oens,ytr)
v5a=auc(v5tr,ytr); v5r=rp2(v5tr,ytr)
bk=max(RES,key=lambda k:RES[k]["rp2"]); V4D=2.67; plb=round(er*100+V4D,2)
print(f"\n  V5 standalone: AUC={v5a:.4f} RP2={v5r*100:.2f}")
print(f"  Best single AD: RP2={RES[bk]['rp2']:.2f} ({bk})")
print(f"  7-way LR OOF:  AUC={ea:.4f} RP2={er*100:.2f}")
print(f"  Predicted LB:  {plb}")
pfin=make_pipeline(SS2(),LogisticRegression(C=1.0,max_iter=2000,random_state=42)); pfin.fit(Xmtr,ytr)
ENS={"v5_rp2":round(v5r*100,2),"v5_auc":round(v5a,4),"best_ad":bk,"best_ad_rp2":RES[bk]["rp2"],
     "ens_rp2":round(er*100,2),"ens_auc":round(ea,4),"v4_delta":V4D,"pred_lb":plb}

print("\n=== Phase C: Hard Defect Recovery ===")
didx=np.where(ytr==1)[0]; dp=v5tr[didx]; hidx=didx[np.argsort(dp)[:15]]
sm={"IF":s1tr,"OCSVM":s2tr,"LOF":s3tr,"Mah":s4tr,"AE":s5tr,"PCA":s6tr}
htable=[]; anc=0
print(f"{'CoilID':>7}  {'V5_p':>8}  IF%  OCSVM%  LOF%  Mah%  AE%  PCA%  Caught?")
for idx in hidx:
    cid=int(train.iloc[idx]["CoilID"]); vp=float(v5tr[idx])
    pcts={m:round(float(np.mean(s<s[idx])*100),1) for m,s in sm.items()}
    t5=[m for m,p in pcts.items() if p>=95.0]
    htable.append({"id":cid,"v5":round(vp,5),**pcts,"top5":t5})
    if t5: anc+=1
    cs=f"YES({','.join(t5)})" if t5 else "no"
    print(f"  {cid:>6}  {vp:>8.5f}  {pcts['IF']:>4.1f}  {pcts['OCSVM']:>6.1f}  {pcts['LOF']:>4.1f}  {pcts['Mah']:>4.1f}  {pcts['AE']:>4.1f}  {pcts['PCA']:>4.1f}  {cs}")
print(f"\n  Caught: {anc}/{len(hidx)}")
vc="BREAKTHROUGH" if anc>=3 else ("PARTIAL_LIFT" if anc>=1 else "EXHAUSTED")
PC={"n_hard":len(hidx),"n_caught":anc,"table":htable,"verdict":vc}

# Save JSON
def strip(d): return {k:v for k,v in d.items() if k not in ("str","ste")}
jp=os.path.join(OUT,"anomaly_method_scores.json")
with open(jp,"w") as f: json.dump({"phase_a":{k:strip(v) for k,v in RES.items()},"phase_b":ENS,"phase_c":PC},f,indent=2)
print(f"\nSaved: {jp}")

# Report
ep=er*100
if ep>=70: hl=f"Found method that hits OOF {ep:.1f} — BREAKTHROUGH"
elif ep>v5r*100+1.0: hl=f"Anomaly ensemble gives marginal lift ({ep:.1f} vs V5 {v5r*100:.1f})"
else: hl=f"Exhausted — supervised framing was correct (ensemble {ep:.1f} approx V5 {v5r*100:.1f})"
lines=["# Track C — Anomaly Detection Report","","## 1. Headline",f"**{hl}**","",
       "## 2. Per-Method Results","",
       "| Method | AUC | OOF (R+P)/2 | Top Features |",
       "|--------|-----|-------------|--------------|"]
for k,v in RES.items():
    tf=", ".join(x[0] for x in v.get("top",[])[:3]) or "—"
    lines.append(f"| {k} | {v['auc']:.4f} | {v['rp2']:.2f} | {tf} |")
lines.append(f"| 7-way LR Ensemble | {ea:.4f} | {ep:.2f} | — |")
lines.append(f"| V5 Supervised | {v5a:.4f} | {v5r*100:.2f} | — |")
lines+=["","## 3. Ensemble + Predicted LB","",
        f"- V5 standalone OOF: **{v5r*100:.2f}**",
        f"- Best single AD: **{RES[bk]['rp2']:.2f}** ({bk})",
        f"- 7-way LR ensemble OOF: **{ep:.2f}**",
        f"- V4 calibration delta: +{V4D}",
        f"- **Predicted LB: {plb}**","",
        "## 4. Hard-Defect Recovery","",
        f"Hard defects = 15 Y=1 rows with lowest V5 meta proba.",
        f"**Verdict: {vc}**  —  {anc}/{len(hidx)} hard defects caught (>=1 AD in top 5%)","",
        "| CoilID | V5 Proba | IF% | OCSVM% | LOF% | Mah% | AE% | PCA% | Caught? |",
        "|--------|----------|-----|--------|------|------|-----|------|---------|"]
for r in htable:
    c=f"YES({','.join(r['top5'])})" if r["top5"] else "no"
    lines.append(f"| {r['id']} | {r['v5']:.5f} | {r.get('IF',0):.0f} | {r.get('OCSVM',0):.0f} | {r.get('LOF',0):.0f} | {r.get('Mah',0):.0f} | {r.get('AE',0):.0f} | {r.get('PCA',0):.0f} | {c} |")
if vc=="BREAKTHROUGH": rec="Build V8 around anomaly detection. IF+AE as primary, supervised ensemble on top."
elif vc=="PARTIAL_LIFT": rec="Add best AD scores as V8 features for +0.5-1pp lift."
else: rec=("Hard defects lie WITHIN normal parameter space — AD cannot see them. Supervised already captures all signal. Next: physics features, semi-supervised label prop, or threshold calibration.")
lines+=["","## 5. Recommendation","",rec,"","---","_2026-05-23_"]
rp=os.path.join(OUT,"TRACK_C_REPORT.md")
with open(rp,"w") as f: f.write("\n".join(lines))
print(f"Saved: {rp}")
print("====== DONE ======")
