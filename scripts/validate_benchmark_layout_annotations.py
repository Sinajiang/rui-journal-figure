from __future__ import annotations
import argparse,csv,json
from pathlib import Path
VALID_LEGEND={"none","embedded","shared_top","shared_bottom","shared_right","panel_local","direct_labels_only"}
VALID_DENSITY={"low","moderate","high"}
VALID_VERIFY={"VERIFIED","PARTIAL","FIGURE_DETAIL_UNVERIFIED","UNVERIFIED"}

def validate(path:Path):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    blocking=[]
    for i,r in enumerate(rows,start=2):
        if not r.get("benchmark_id") or not r.get("figure_id"):
            blocking.append({"type":"missing_id","row":i})
        try: pc=float(r["panel_count"])
        except: pc=0
        if pc<1: blocking.append({"type":"invalid_panel_count","row":i})
        for fld in ["anchor_area_share","workflow_area_share","white_space_fraction","direct_label_fraction"]:
            try:v=float(r[fld])
            except: v=None
            if v is not None and not (0<=v<=1):
                blocking.append({"type":"fraction_out_of_range","row":i,"field":fld})
        for fld in ["effect_size_direct_fraction","effect_size_legend_fraction","ci_numeric_direct_fraction","ci_legend_fraction","pvalue_direct_fraction","pvalue_legend_fraction","adjusted_significance_direct_fraction","adjusted_significance_legend_fraction","n_direct_fraction","n_legend_fraction","direction_direct_fraction","direction_legend_fraction"]:
            raw=r.get(fld)
            if raw in (None,""): continue
            try:v=float(raw)
            except:
                blocking.append({"type":"invalid_optional_fraction","row":i,"field":fld}); continue
            if not (0<=v<=1): blocking.append({"type":"fraction_out_of_range","row":i,"field":fld})
        if r.get("legend_statistical_density") not in (None,""):
            try:v=float(r.get("legend_statistical_density"))
            except: blocking.append({"type":"invalid_legend_statistical_density","row":i})
            else:
                if v<0: blocking.append({"type":"invalid_legend_statistical_density","row":i})
        if r.get("legend_strategy") not in VALID_LEGEND:
            blocking.append({"type":"invalid_legend_strategy","row":i})
        if r.get("text_density") not in VALID_DENSITY:
            blocking.append({"type":"invalid_text_density","row":i})
        if r.get("verification_status") not in VALID_VERIFY:
            blocking.append({"type":"invalid_verification_status","row":i})
        for fld in ["panel_rects_json","panel_roles_json","panel_chart_types_json"]:
            try: obj=json.loads(r.get(fld) or "[]")
            except:
                blocking.append({"type":"invalid_json","row":i,"field":fld}); continue
            if fld=="panel_rects_json":
                for rect in obj:
                    if not isinstance(rect,list) or len(rect)!=4:
                        blocking.append({"type":"invalid_panel_rect","row":i}); continue
                    x,y,w,h=map(float,rect)
                    if min(x,y,w,h)<0 or x+w>1.0001 or y+h>1.0001:
                        blocking.append({"type":"panel_rect_out_of_bounds","row":i})
    return {"count":len(rows),"blocking":blocking,"pass":not blocking}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("annotations"); ap.add_argument("--out")
    a=ap.parse_args(); res=validate(Path(a.annotations))
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
