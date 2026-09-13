from __future__ import annotations
import argparse, json, math
from pathlib import Path

def topology_rects(topology,n):
    if n==1:
        return [[.08,.12,.84,.76]]
    if topology=="anchor_left_stack_right" and n>=3:
        out=[[.06,.12,.50,.78]]
        m=n-1; gap=.04; h=(.78-gap*(m-1))/m
        for i in range(m):
            out.append([.62,.12+(m-1-i)*(h+gap),.32,h])
        return out
    if topology=="anchor_top_support_bottom" and n>=3:
        out=[[.07,.53,.86,.37]]
        m=n-1; gap=.04; w=(.86-gap*(m-1))/m
        out += [[.07+i*(w+gap),.12,w,.31] for i in range(m)]
        return out
    if topology=="horizontal_triptych":
        gap=.04; w=(.86-gap*(n-1))/n
        return [[.07+i*(w+gap),.15,w,.70] for i in range(n)]
    if topology=="vertical_stack":
        gap=.04; h=(.78-gap*(n-1))/n
        return [[.10,.12+(n-1-i)*(h+gap),.80,h] for i in range(n)]
    # equal grid
    cols=2 if n>1 else 1
    rows=math.ceil(n/cols); gx=.05; gy=.06
    w=(.86-gx*(cols-1))/cols
    h=(.76-gy*(rows-1))/rows
    rects=[]
    for i in range(n):
        r=i//cols; c=i%cols
        rects.append([.07+c*(w+gx),.12+(rows-1-r)*(h+gy),w,h])
    return rects

def solve(visual_weight_plan:Path,layout_grammar:Path,figure_width_mm=180,figure_height_mm=120):
    vp=json.loads(visual_weight_plan.read_text(encoding="utf-8"))
    g=json.loads(layout_grammar.read_text(encoding="utf-8"))
    dom=(g.get("topology") or {}).get("dominant")
    out={"figure_width_mm":figure_width_mm,"figure_height_mm":figure_height_mm,"figures":[]}
    for f in vp.get("figures",[]):
        panels=sorted(f.get("panels",[]),key=lambda x:(x.get("layout_priority",999),-float(x.get("contribution_score",0))))
        n=len(panels)
        topology=dom or ("anchor_left_stack_right" if n>=3 and f.get("layout_strategy")=="dominant_anchor" else "equal_2x2")
        rects=topology_rects(topology,n)
        out["figures"].append({
            "figure":f.get("figure"),
            "figure_id":f"Figure_{f.get('figure')}",
            "theme":f.get("theme"),
            "topology":topology,
            "legend_strategy":(g.get("legend_strategy") or {}).get("dominant") or "none",
            "white_space_fraction_target":(g.get("white_space_fraction") or {}).get("median"),
            "panels":[{
                "panel_id":p["panel_id"],
                "role":p.get("role"),
                "contribution_score":float(p.get("contribution_score",0)),
                "visual_weight_class":p.get("visual_weight_class"),
                "normalized_area_share":float(p.get("normalized_area_share",0)),
                "visual_density":float(p.get("visual_density",0)),
                "rect":[round(float(x),4) for x in r],
            } for p,r in zip(panels,rects)]
        })
    return out

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("visual_weight_plan")
    ap.add_argument("layout_grammar")
    ap.add_argument("--figure-width-mm",type=float,default=180)
    ap.add_argument("--figure-height-mm",type=float,default=120)
    ap.add_argument("--out")
    a=ap.parse_args()
    res=solve(Path(a.visual_weight_plan),Path(a.layout_grammar),a.figure_width_mm,a.figure_height_mm)
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
