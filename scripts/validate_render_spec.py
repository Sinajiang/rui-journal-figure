from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

SUPPORTED={
    "dot_box","paired_dot","effect_plot","lollipop","scatter",
    "grouped_bar","heatmap","evidence_matrix","workflow"
}

REQUIRED_MAPPING={
    "dot_box":["group","value"],
    "paired_dot":["id","condition","value"],
    "effect_plot":["label","estimate"],
    "lollipop":["label","value"],
    "scatter":["x","y"],
    "grouped_bar":["category","value"],
    "heatmap":["row","column","value"],
    "evidence_matrix":["row","column","status"],
    "workflow":[],
}

def validate(path: Path):
    s=yaml.safe_load(path.read_text(encoding="utf-8"))
    blocking=[]; review=[]
    fig=s.get("figure") or {}
    if not fig.get("id"):
        blocking.append({"type":"missing_figure_id"})
    for k in ["width_mm","height_mm"]:
        if float(fig.get(k,0))<=0:
            blocking.append({"type":"invalid_dimension","field":k})
    seen=set()
    for p in s.get("panels",[]) or []:
        pid=p.get("panel_id")
        if not pid:
            blocking.append({"type":"missing_panel_id"})
            continue
        if pid in seen:
            blocking.append({"type":"duplicate_panel_id","panel_id":pid})
        seen.add(pid)
        ct=p.get("chart_type")
        if ct not in SUPPORTED:
            blocking.append({"type":"unsupported_chart_type","panel_id":pid,"chart_type":ct})
            continue
        mp=p.get("mapping") or {}
        for req in REQUIRED_MAPPING[ct]:
            if req not in mp:
                blocking.append({"type":"missing_mapping","panel_id":pid,"chart_type":ct,"mapping":req})
        if ct!="workflow":
            src=(p.get("source") or {}).get("path")
            if not src:
                blocking.append({"type":"missing_source_path","panel_id":pid})
    return {"blocking":blocking,"review":review,"pass":len(blocking)==0}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("render_spec")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=validate(Path(args.render_spec))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
