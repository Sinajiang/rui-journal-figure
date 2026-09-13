from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml

def apply(spec_path:Path,plan_path:Path,out:Path):
    spec=yaml.safe_load(spec_path.read_text(encoding="utf-8")); plan=json.loads(plan_path.read_text(encoding="utf-8"))
    fid=(spec.get("figure") or {}).get("id")
    pmap={(f.get("figure_id"),p.get("panel_id")):p for f in plan.get("figures",[]) for p in f.get("panels",[])}
    fmap={f.get("figure_id"):f for f in plan.get("figures",[])}
    fplan=fmap.get(fid,{})
    spec.setdefault("annotation_intelligence",{}).update({
        "plan_version":plan.get("version"),
        "decision_binding":True,
        "shared_legend_clauses":fplan.get("shared_legend_clauses",[]),
        "author_guidance":fplan.get("shared_legend_guidance",[]),
    })
    for p in spec.get("panels",[]) or []:
        ap=pmap.get((fid,p.get("panel_id")))
        if not ap: continue
        p["annotation_intelligence"]={
          "direct_annotations":[{"annotation_id":x.get("annotation_id"),"type":x.get("statistic_type"),"text":x.get("text"),"priority_score":x.get("direct_score"),"claim_id":x.get("claim_id")} for x in ap.get("direct_annotations",[])],
          "legend_annotations":[{"annotation_id":x.get("annotation_id"),"type":x.get("statistic_type"),"text":x.get("text"),"claim_id":x.get("claim_id")} for x in ap.get("legend_annotations",[])],
          "suppressed_annotation_ids":[x.get("annotation_id") for x in ap.get("suppressed_annotations",[])],
          "density":ap.get("density",{})
        }
    out.write_text(yaml.safe_dump(spec,sort_keys=False,allow_unicode=True),encoding="utf-8")
    return spec

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("render_spec"); ap.add_argument("plan"); ap.add_argument("--out",required=True)
    a=ap.parse_args(); apply(Path(a.render_spec),Path(a.plan),Path(a.out))
