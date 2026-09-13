from __future__ import annotations
import argparse, json
from pathlib import Path

def plan(qa_json: Path):
    q=json.loads(qa_json.read_text(encoding="utf-8"))
    issues=[]
    # Accept several QA shapes.
    blocking=[]
    if "blocking" in q:
        blocking += q.get("blocking",[])
    if "rendered_geometry" in q:
        for p in q["rendered_geometry"].get("pages",[]):
            blocking += p.get("blocking",[])
    if "layout_contract" in q and q["layout_contract"]:
        blocking += q["layout_contract"].get("blocking",[])

    for x in blocking:
        typ=x.get("type","unknown")
        if typ in {"text_text_overlap","card_text_boundary_violation"}:
            fix="move annotation/text into dedicated whitespace; enlarge local container before reducing font size"
        elif typ in {"text_in_forbidden_region","panel_overlap"}:
            fix="restore protected gutter or redistribute panel rectangles"
        elif typ in {"missing_panel","missing_source","missing_legend_clause"}:
            fix="repair evidence/manuscript mapping before visual work"
        else:
            fix="localize object and apply the smallest layout repair"
        issues.append({
            "defect_type":typ,
            "severity":"BLOCKING",
            "recommended_local_fix":fix,
            "protected_elements":[
                "scientific values",
                "accepted panel roles",
                "accepted group color semantics",
                "current scientific authority"
            ]
        })

    return {
        "blocking_issue_count":len(issues),
        "repairs":issues,
        "strategy":"surgical_repair" if issues else "no_blocking_repair_needed"
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("qa_json")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=plan(Path(args.qa_json))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
