from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def audit(evidence_graph: Path, architecture: Path):
    g=yaml.safe_load(evidence_graph.read_text(encoding="utf-8"))
    a=yaml.safe_load(architecture.read_text(encoding="utf-8"))
    blocking=[]
    review=[]

    figs=g.get("figures",{}) or {}
    arch=a.get("figures",{}) or {}

    for fk,fobj in figs.items():
        fs=str(fk)
        aobj=arch.get(int(fs),arch.get(fs))
        if aobj is None:
            blocking.append({"type":"missing_legend_architecture","figure":fs})
            continue
        promoted=list((fobj.get("panels") or {}).keys())
        declared=[str(x) for x in aobj.get("panels",[])]
        if promoted != declared:
            blocking.append({
                "type":"panel_set_or_order_mismatch",
                "figure":fs,
                "promoted_panels":promoted,
                "legend_architecture_panels":declared
            })
        legend_order=[str(x) for x in aobj.get("legend_order",[])]
        if legend_order and legend_order != promoted:
            review.append({
                "type":"legend_order_differs_from_panel_order",
                "figure":fs,
                "panel_order":promoted,
                "legend_order":legend_order
            })

    for fk in arch:
        fs=str(fk)
        if int(fs) not in figs and fs not in figs:
            review.append({"type":"architecture_for_nonpromoted_figure","figure":fs})

    return {"blocking":blocking,"review":review,"pass":len(blocking)==0}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("evidence_graph")
    ap.add_argument("legend_architecture")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.evidence_graph),Path(args.legend_architecture))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
