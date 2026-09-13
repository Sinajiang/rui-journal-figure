from __future__ import annotations
import argparse, json
from pathlib import Path

def decide(
    architecture_score: float,
    visual_score: float,
    hard_gates_pass: bool,
    manual_visual_status: str,
    baseline_visual_score: float|None=None,
    baseline_architecture_score: float|None=None,
    blocking_visual_issues: int=0,
):
    m=(manual_visual_status or "pending").upper()

    if not hard_gates_pass:
        return {
            "decision":"ROLLBACK",
            "reason":"Scientific/architecture/journal/source hard gate failed."
        }

    if blocking_visual_issues > 0:
        return {
            "decision":"REPAIR",
            "reason":f"{blocking_visual_issues} blocking visual issue(s) remain."
        }

    if m in {"PENDING","NOT_REVIEWED","HOLD"}:
        return {
            "decision":"HOLD",
            "reason":"Manual final-size visual review is incomplete."
        }

    if m == "FAIL":
        return {
            "decision":"ROLLBACK",
            "reason":"Manual final-size visual review failed."
        }

    if baseline_visual_score is not None and visual_score < baseline_visual_score - 0.6:
        return {
            "decision":"ROLLBACK",
            "reason":"Global visual quality regressed beyond tolerance versus accepted baseline."
        }

    if baseline_architecture_score is not None and architecture_score < baseline_architecture_score - 0.5:
        return {
            "decision":"ROLLBACK",
            "reason":"Architecture score regressed beyond tolerance versus accepted baseline."
        }

    if architecture_score < 7.0 or visual_score < 7.0:
        return {
            "decision":"REPAIR",
            "reason":"Candidate passes hard gates but architecture or visual score remains below promotion threshold."
        }

    return {
        "decision":"PROMOTE",
        "reason":"Hard gates pass; manual visual review passes; candidate does not materially regress from baseline."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--architecture-score",type=float,required=True)
    ap.add_argument("--visual-score",type=float,required=True)
    ap.add_argument("--hard-gates-pass",choices=["true","false"],required=True)
    ap.add_argument("--manual-visual-status",required=True)
    ap.add_argument("--baseline-visual-score",type=float)
    ap.add_argument("--baseline-architecture-score",type=float)
    ap.add_argument("--blocking-visual-issues",type=int,default=0)
    ap.add_argument("--out")
    args=ap.parse_args()

    res=decide(
        args.architecture_score,
        args.visual_score,
        args.hard_gates_pass=="true",
        args.manual_visual_status,
        args.baseline_visual_score,
        args.baseline_architecture_score,
        args.blocking_visual_issues
    )
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
