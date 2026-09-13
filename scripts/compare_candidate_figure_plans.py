from __future__ import annotations
import argparse, json
from pathlib import Path
from score_candidate_figure_plan import score
from validate_candidate_figure_plan import validate

def compare(paths):
    rows=[]
    for p in paths:
        p=Path(p)
        v=validate(p,allow_new_analysis=False)
        s=score(p)
        rows.append({
            "file":str(p),
            "candidate_id":s.get("candidate_id") or v.get("candidate_id"),
            "validation_pass":v["pass"],
            "score_pass":s["pass"],
            "weighted_score_0_to_10":s.get("weighted_score_0_to_10"),
            "blocking":v["blocking"],
            "review":v["review"],
        })

    eligible=[r for r in rows if r["validation_pass"] and r["score_pass"]]
    eligible=sorted(eligible,key=lambda x:x["weighted_score_0_to_10"],reverse=True)
    return {
        "candidates":rows,
        "recommended_candidate":eligible[0]["candidate_id"] if eligible else None,
        "eligible_ranked":[
            {"candidate_id":x["candidate_id"],"score":x["weighted_score_0_to_10"]}
            for x in eligible
        ],
        "manual_scientific_review_required":True
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("plans",nargs="+")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=compare(args.plans)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
