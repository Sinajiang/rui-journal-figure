from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

VALID_AVAILABILITY={"DIRECTLY_AVAILABLE","STRUCTURALLY_ADAPTABLE","OPTIONAL_NEW_ANALYSIS","NOT_APPLICABLE"}

def validate(plan_path: Path, allow_new_analysis=False):
    p=yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    blocking=[]
    review=[]
    figures=p.get("figures",[]) or []
    seen_fig=set()
    for f in figures:
        fnum=f["figure"]
        if fnum in seen_fig:
            blocking.append({"type":"duplicate_figure_number","figure":fnum})
        seen_fig.add(fnum)
        seen_panel=set()
        for pan in f.get("panels",[]) or []:
            label=str(pan["panel"])
            if label in seen_panel:
                blocking.append({"type":"duplicate_panel","figure":fnum,"panel":label})
            seen_panel.add(label)
            avail=pan.get("availability")
            if avail not in VALID_AVAILABILITY:
                blocking.append({"type":"invalid_availability","figure":fnum,"panel":label,"availability":avail})
            if avail=="OPTIONAL_NEW_ANALYSIS" and not allow_new_analysis:
                blocking.append({"type":"unavailable_panel_in_promoted_plan","figure":fnum,"panel":label})
            if avail=="NOT_APPLICABLE":
                blocking.append({"type":"not_applicable_panel_in_promoted_plan","figure":fnum,"panel":label})
            if pan.get("role") not in {"workflow","provenance"}:
                if not pan.get("analysis_id") and avail=="DIRECTLY_AVAILABLE":
                    review.append({"type":"available_evidence_panel_missing_analysis_id","figure":fnum,"panel":label})
                if not pan.get("source_id") and avail=="DIRECTLY_AVAILABLE":
                    review.append({"type":"available_evidence_panel_missing_source_id","figure":fnum,"panel":label})

    return {
        "candidate_id":p.get("candidate_id"),
        "blocking":blocking,
        "review":review,
        "pass":len(blocking)==0
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--allow-new-analysis",action="store_true")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=validate(Path(args.plan),args.allow_new_analysis)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
