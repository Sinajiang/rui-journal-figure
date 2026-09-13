from __future__ import annotations
import argparse, json, math
from pathlib import Path
import csv

def f(x,default=0.0):
    try:return float(x)
    except:return default

def parse_bool(x):
    return str(x).strip().lower() in {"1","true","yes","y"}

def score(candidate_json: Path, panel_inventory_tsv: Path):
    c=json.loads(candidate_json.read_text(encoding="utf-8"))
    rows=list(csv.DictReader(panel_inventory_tsv.open(encoding="utf-8"),delimiter="\t"))
    pmap={r["panel_id"]:r for r in rows}

    figures=c.get("figures",[])
    panel_balance_scores=[]
    density_scores=[]
    anchor_scores=[]
    whitespace_scores=[]
    schematic_count=0
    panel_count=0

    for fig in figures:
        pids=fig.get("panels",[])
        if not pids:
            continue
        panel_count += len(pids)
        n=len(pids)

        # Balance heuristic: 2-4 panels generally easiest; 1 or >5 less efficient.
        if n==1: pb=7
        elif 2<=n<=4: pb=10
        elif n==5: pb=7.5
        else: pb=max(2,10-1.7*(n-4))
        panel_balance_scores.append(pb)

        density=sum(f(pmap.get(pid,{}).get("visual_density")) for pid in pids)
        density_scores.append(max(0,10-0.35*max(0,density-18)))

        # anchor visibility: high-contribution/anchor panels should exist
        anchors=[
            pmap.get(pid,{}) for pid in pids
            if (pmap.get(pid,{}).get("role") or "").lower() in {"anchor","primary"}
            or f(pmap.get(pid,{}).get("contribution_score"))>=9
        ]
        anchor_scores.append(10 if anchors else 6)

        # Whitespace heuristic: penalize excessive density and too many panels.
        pressure=density + 2.5*n
        whitespace_scores.append(max(0,min(10,12-0.18*pressure)))

        for pid in pids:
            ct=(pmap.get(pid,{}).get("chart_type") or "").lower()
            role=(pmap.get(pid,{}).get("role") or "").lower()
            if "schematic" in ct or role in {"workflow","provenance","design"}:
                schematic_count += 1

    def avg(xs):
        return sum(xs)/len(xs) if xs else 0

    schematic_fraction=schematic_count/panel_count if panel_count else 0
    # broad default; exact benchmark comparison belongs upstream
    schematic_score=10 if 0.08 <= schematic_fraction <= 0.35 else max(4,10-20*min(abs(schematic_fraction-.08),abs(schematic_fraction-.35)))

    metrics={
        "panel_balance":round(avg(panel_balance_scores),3),
        "density_feasibility":round(avg(density_scores),3),
        "whitespace_efficiency":round(avg(whitespace_scores),3),
        "anchor_visibility":round(avg(anchor_scores),3),
        "benchmark_visual_concordance":round(schematic_score,3),
    }
    weights={
        "panel_balance":1.0,
        "density_feasibility":1.3,
        "whitespace_efficiency":1.0,
        "anchor_visibility":1.3,
        "benchmark_visual_concordance":0.7,
    }
    overall=sum(metrics[k]*weights[k] for k in metrics)/sum(weights.values())
    metrics["overall_visual_score"]=round(overall,3)

    return {
        "metrics":metrics,
        "schematic_fraction":round(schematic_fraction,3),
        "panel_count":panel_count,
        "figure_count":len(figures),
        "note":"Structural score is a prototype heuristic; final-size manual visual review remains mandatory."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("panel_inventory_tsv")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=score(Path(args.candidate_json),Path(args.panel_inventory_tsv))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
