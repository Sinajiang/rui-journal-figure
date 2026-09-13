from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path

def n(x):
    try:return float(x)
    except:return None

def weight(r):
    vals=[n(r.get(k)) for k in ["scientific_similarity","method_similarity","modality_similarity","figure_role_relevance","journal_fit"]]
    vals=[max(0,min(5,v))/5 for v in vals if v is not None]
    base=sum(vals)/len(vals) if vals else .5
    mult={"VERIFIED":1,"PARTIAL":.85,"FIGURE_DETAIL_UNVERIFIED":.55,"UNVERIFIED":.4}.get(r.get("verification_status"),.4)
    return max(.05,base*mult)

def wq(vals,ws,q):
    p=sorted((v,w) for v,w in zip(vals,ws) if v is not None and w>0)
    if not p:return None
    cutoff=q*sum(w for _,w in p); c=0
    for v,w in p:
        c+=w
        if c>=cutoff:return float(v)
    return float(p[-1][0])

def summary(rows,field,ws):
    vals=[n(r.get(field)) for r in rows]
    vv=[(v,w) for v,w in zip(vals,ws) if v is not None]
    if not vv:return {"median":None,"q1":None,"q3":None}
    v=[x for x,_ in vv]; w=[y for _,y in vv]
    return {"median":round(wq(v,w,.5),4),"q1":round(wq(v,w,.25),4),"q3":round(wq(v,w,.75),4)}

def freq(rows,field,ws):
    d=defaultdict(float)
    for r,w in zip(rows,ws): d[r.get(field,"unknown")]+=w
    tot=sum(d.values()) or 1
    return {k:round(v/tot,4) for k,v in sorted(d.items(),key=lambda z:z[1],reverse=True)}

def aggregate(path:Path):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t")); ws=[weight(r) for r in rows]
    topo=freq(rows,"topology",ws); leg=freq(rows,"legend_strategy",ws); td=freq(rows,"text_density",ws); sig=freq(rows,"significance_style",ws) if any(r.get("significance_style") for r in rows) else {}
    rv=defaultdict(list); rw=defaultdict(list)
    for r,w in zip(rows,ws):
        try: rects=json.loads(r["panel_rects_json"]); roles=json.loads(r["panel_roles_json"])
        except: continue
        for rect,role in zip(rects,roles):
            if isinstance(rect,list) and len(rect)==4:
                rv[str(role)].append(float(rect[2])*float(rect[3])); rw[str(role)].append(w)
    priors={role:{"median":round(wq(vals,rw[role],.5),4),"q1":round(wq(vals,rw[role],.25),4),"q3":round(wq(vals,rw[role],.75),4),"n":len(vals)} for role,vals in rv.items()}
    return {
      "corpus":{"n_figures":len(rows),"benchmark_ids":sorted(set(r["benchmark_id"] for r in rows))},
      "topology":{"dominant":next(iter(topo),None),"frequencies":topo},
      "panel_count":summary(rows,"panel_count",ws),
      "anchor_area_share":summary(rows,"anchor_area_share",ws),
      "workflow_area_share":summary(rows,"workflow_area_share",ws),
      "white_space_fraction":summary(rows,"white_space_fraction",ws),
      "direct_label_fraction":summary(rows,"direct_label_fraction",ws),
      "legend_strategy":{"dominant":next(iter(leg),None),"frequencies":leg},
      "text_density":{"dominant":next(iter(td),None),"frequencies":td},
      "role_area_priors":priors,
      "annotation_statistics":{
        "effect_size":{"direct_rate":summary(rows,"effect_size_direct_fraction",ws)["median"],"legend_rate":summary(rows,"effect_size_legend_fraction",ws)["median"]},
        "ci":{"direct_rate":summary(rows,"ci_numeric_direct_fraction",ws)["median"],"legend_rate":summary(rows,"ci_legend_fraction",ws)["median"]},
        "p_value":{"direct_rate":summary(rows,"pvalue_direct_fraction",ws)["median"],"legend_rate":summary(rows,"pvalue_legend_fraction",ws)["median"]},
        "adjusted_p":{"direct_rate":summary(rows,"adjusted_significance_direct_fraction",ws)["median"],"legend_rate":summary(rows,"adjusted_significance_legend_fraction",ws)["median"]},
        "fdr":{"direct_rate":summary(rows,"adjusted_significance_direct_fraction",ws)["median"],"legend_rate":summary(rows,"adjusted_significance_legend_fraction",ws)["median"]},
        "q_value":{"direct_rate":summary(rows,"adjusted_significance_direct_fraction",ws)["median"],"legend_rate":summary(rows,"adjusted_significance_legend_fraction",ws)["median"]},
        "n":{"direct_rate":summary(rows,"n_direct_fraction",ws)["median"],"legend_rate":summary(rows,"n_legend_fraction",ws)["median"]},
        "direction":{"direct_rate":summary(rows,"direction_direct_fraction",ws)["median"],"legend_rate":summary(rows,"direction_legend_fraction",ws)["median"]}
      },
      "significance_style":{"dominant":next(iter(sig),None),"frequencies":sig},
      "legend_statistical_density":summary(rows,"legend_statistical_density",ws)
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("annotations"); ap.add_argument("--out")
    a=ap.parse_args(); res=aggregate(Path(a.annotations))
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
