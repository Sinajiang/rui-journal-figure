from __future__ import annotations
import csv, math
from pathlib import Path

def parse_list(x):
    if x is None:
        return []
    s=str(x).strip()
    if not s:
        return []
    return [z.strip() for z in s.replace("|",";").split(";") if z.strip()]

def parse_bool(x):
    return str(x).strip().lower() in {"1","true","yes","y"}

def parse_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def load_panels(path: Path):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    out=[]
    for r in rows:
        r=dict(r)
        r["claim_ids"]=parse_list(r.get("claim_ids"))
        r["source_ids"]=parse_list(r.get("source_ids"))
        r["main_eligible"]=parse_bool(r.get("main_eligible"))
        r["must_main"]=parse_bool(r.get("must_main"))
        for k in [
            "priority","contribution_score","benchmark_support_score",
            "source_traceability_score","visual_density","narrative_order"
        ]:
            r[k]=parse_float(r.get(k))
        out.append(r)
    return out

def jaccard(a,b):
    a=set(a); b=set(b)
    if not a and not b:
        return 0.0
    return len(a & b)/max(1,len(a | b))

def redundancy_score(a,b):
    score=0.0
    score += 0.45*jaccard(a.get("claim_ids",[]),b.get("claim_ids",[]))
    score += 0.25*jaccard(a.get("source_ids",[]),b.get("source_ids",[]))
    score += 0.15*(1.0 if a.get("evidence_family") and a.get("evidence_family")==b.get("evidence_family") else 0.0)
    score += 0.10*(1.0 if a.get("chart_type") and a.get("chart_type")==b.get("chart_type") else 0.0)
    rg_a=(a.get("redundancy_group") or "").strip()
    rg_b=(b.get("redundancy_group") or "").strip()
    score += 0.05*(1.0 if rg_a and rg_a==rg_b else 0.0)
    return round(score,4)

def panel_utility(p):
    # 0–10 weighted utility.
    return (
        0.30*p.get("priority",0)
        +0.30*p.get("contribution_score",0)
        +0.15*p.get("benchmark_support_score",0)
        +0.15*p.get("source_traceability_score",0)
        +0.10*max(0.0,10.0-p.get("visual_density",0))
    )

ROLE_ORDER={
    "workflow":0,"provenance":0,"design":0,
    "anchor":1,"primary":1,
    "participant":2,"donor_level":2,
    "orthogonal":3,"replication":3,
    "robustness":4,"sensitivity":4,
    "external_context":5,"context":5,
    "mechanism":6,
    "boundary":7,
}

def role_rank(role):
    return ROLE_ORDER.get((role or "").lower(),4)
