from __future__ import annotations
import argparse,json,math
from pathlib import Path

def load_panels(p):
    o=json.loads(Path(p).read_text(encoding="utf-8"))
    return o.get("panels") or o.get("panel_weights") or []

def sc(p):
    for k in ["visual_weight","scientific_contribution_score","contribution_score","weight"]:
        try:
            if p.get(k) is not None:return float(p[k])
        except: pass
    return 5.0

def rects(topology,n):
    if n==1:return [[.08,.12,.84,.76]]
    if topology=="anchor_left_stack_right" and n>=3:
        rr=[[.06,.12,.50,.78]]; m=n-1; gap=.04; h=(.78-gap*(m-1))/m
        for i in range(m): rr.append([.62,.12+(m-1-i)*(h+gap),.32,h])
        return rr
    if topology=="anchor_top_support_bottom" and n>=3:
        rr=[[.07,.53,.86,.37]]; m=n-1; gap=.04; w=(.86-gap*(m-1))/m
        rr += [[.07+i*(w+gap),.12,w,.31] for i in range(m)]; return rr
    cols=2; rows=math.ceil(n/cols); gx=.05; gy=.06; w=(.86-gx)/2; h=(.76-gy*(rows-1))/rows
    return [[.07+(i%2)*(w+gx),.12+(rows-1-i//2)*(h+gy),w,h] for i in range(n)]

def solve(contribution_json:Path,grammar_json:Path,figure_id="Figure_1"):
    panels=[p for p in load_panels(contribution_json) if str(p.get("recommended_location","main")).lower()!="supplement"]
    panels=sorted(panels,key=sc,reverse=True)
    g=json.loads(grammar_json.read_text(encoding="utf-8"))
    topology=(g.get("topology") or {}).get("dominant") or ("anchor_left_stack_right" if len(panels)>=3 else "equal_2x2")
    priors=g.get("role_area_priors",{})
    raw=[]
    for p in panels:
        prior=(priors.get(p.get("role","")) or {}).get("median")
        pf=max(.75,min(1.35,float(prior)/.25)) if prior is not None else 1
        raw.append(sc(p)*pf)
    s=sum(raw) or 1; shares=[x/s for x in raw]
    am=(g.get("anchor_area_share") or {}).get("median")
    if am is not None and len(shares)>1:
        t=max(.22,min(.58,.65*shares[0]+.35*float(am))); rem=sum(shares[1:]) or 1
        shares=[t]+[(1-t)*x/rem for x in shares[1:]]
    rs=rects(topology,len(panels))
    return {"figure_id":figure_id,"topology":topology,
            "legend":{"strategy":(g.get("legend_strategy") or {}).get("dominant") or "none"},
            "white_space_fraction_target":(g.get("white_space_fraction") or {}).get("median"),
            "panels":[{"panel_id":p.get("panel_id"),"role":p.get("role"),"contribution_score":sc(p),
                       "target_area_share":round(sh,4),"rect":[round(float(x),4) for x in r]}
                      for p,sh,r in zip(panels,shares,rs)]}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("contribution_weights"); ap.add_argument("layout_grammar")
    ap.add_argument("--figure-id",default="Figure_1"); ap.add_argument("--out")
    a=ap.parse_args(); res=solve(Path(a.contribution_weights),Path(a.layout_grammar),a.figure_id)
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
