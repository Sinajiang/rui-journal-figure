from __future__ import annotations
import argparse,csv,re
from pathlib import Path
import yaml

FIELDS=["figure_id","panel_id","annotation_id","claim_id","statistic_type","label","value","lower","upper","interval_level","effect_metric","null_reference","display_text","inferential_unit","claim_importance","statistical_necessity","panel_tier","primary_test","multiplicity_applies","multiplicity_adjusted","uncertainty_encoded","estimate_encoded","direction_encoded","n_varies","repeated_across_panels","exact_value_required","redundancy_group","benchmark_direct_rate","benchmark_legend_rate","notes"]

def infer_type(s):
    t=(s or "").lower()
    if "fdr" in t:return "fdr"
    if re.search(r"\bq\s*[=<]",t):return "q_value"
    if "adjusted p" in t or "adj p" in t:return "adjusted_p"
    if re.search(r"\bp\s*[=<]",t):return "p_value"
    if "ci" in t or "confidence interval" in t:return "ci"
    if re.search(r"\bn\s*=",t):return "n"
    return "descriptive"

def extract(path:Path,out:Path):
    g=yaml.safe_load(path.read_text(encoding="utf-8")); rows=[]; i=1
    for fk,f in (g.get("figures") or {}).items():
        for pk,p in (f.get("panels") or {}).items():
            stats=p.get("statistics")
            if not stats and p.get("statistic"):
                stats=[{"text":p.get("statistic")}]
            for st in stats or []:
                if isinstance(st,str): st={"text":st}
                txt=st.get("text") or st.get("label") or ""
                rows.append({
                  "figure_id":f"Figure_{fk}","panel_id":str(pk),"annotation_id":st.get("id") or f"AUTO{i:03d}",
                  "claim_id":(p.get("claim_ids") or [""])[0],"statistic_type":st.get("type") or infer_type(txt),
                  "label":txt,"value":st.get("value","") ,"lower":st.get("lower","") ,"upper":st.get("upper","") ,
                  "interval_level":st.get("interval_level","") ,"effect_metric":st.get("effect_metric","") ,"null_reference":st.get("null_reference","") ,"display_text":st.get("display_text","") ,
                  "inferential_unit":st.get("inferential_unit",st.get("redundancy_group",f"AUTO_{i}")),"claim_importance":st.get("claim_importance",3),
                  "statistical_necessity":st.get("necessity","moderate"),"panel_tier":st.get("panel_tier",str(p.get("role","SUPPORT")).upper()),
                  "primary_test":st.get("primary_test",False),"multiplicity_applies":st.get("multiplicity_applies",False),
                  "multiplicity_adjusted":st.get("multiplicity_adjusted",False),"uncertainty_encoded":st.get("uncertainty_encoded",False),
                  "estimate_encoded":st.get("estimate_encoded",False),"direction_encoded":st.get("direction_encoded",False),
                  "n_varies":st.get("n_varies",False),"repeated_across_panels":st.get("repeated_across_panels",False),
                  "exact_value_required":st.get("exact_value_required",False),"redundancy_group":st.get("redundancy_group",f"AUTO_{i}"),
                  "benchmark_direct_rate":"","benchmark_legend_rate":"","notes":"legacy evidence-graph extraction; enrich from source tables when needed"
                }); i+=1
    with out.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS,delimiter="\t"); w.writeheader(); w.writerows(rows)
    return rows

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("evidence_graph"); ap.add_argument("--out",required=True)
    a=ap.parse_args(); extract(Path(a.evidence_graph),Path(a.out))
