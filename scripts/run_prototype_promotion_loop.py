from __future__ import annotations
import argparse, json, tempfile
from pathlib import Path

from score_structural_prototype import score as visual_score
from promotion_controller import decide

def run(candidate_json: Path, panel_inventory: Path, architecture_score: float,
        baseline_visual=None, baseline_arch=None, hard_gates_pass=True,
        manual_visual_status="PENDING", blocking_visual_issues=0):
    v=visual_score(candidate_json,panel_inventory)
    vs=v["metrics"]["overall_visual_score"]
    d=decide(
        architecture_score=architecture_score,
        visual_score=vs,
        hard_gates_pass=hard_gates_pass,
        manual_visual_status=manual_visual_status,
        baseline_visual_score=baseline_visual,
        baseline_architecture_score=baseline_arch,
        blocking_visual_issues=blocking_visual_issues
    )
    return {
        "architecture_score":architecture_score,
        "prototype_visual":v,
        "decision":d,
        "manual_visual_review_required":True
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("panel_inventory")
    ap.add_argument("--architecture-score",type=float,required=True)
    ap.add_argument("--baseline-visual-score",type=float)
    ap.add_argument("--baseline-architecture-score",type=float)
    ap.add_argument("--hard-gates-pass",choices=["true","false"],default="true")
    ap.add_argument("--manual-visual-status",default="PENDING")
    ap.add_argument("--blocking-visual-issues",type=int,default=0)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=run(
        Path(args.candidate_json),Path(args.panel_inventory),
        args.architecture_score,args.baseline_visual_score,args.baseline_architecture_score,
        args.hard_gates_pass=="true",args.manual_visual_status,args.blocking_visual_issues
    )
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
