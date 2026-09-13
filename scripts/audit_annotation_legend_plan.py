from __future__ import annotations
import argparse,json,math
from pathlib import Path

SIG_TYPES={"p_value","adjusted_p","fdr","q_value"}
SAFE_REQUIRED_SUPPRESSION={
    "ci_already_graphically_encoded",
    "adjusted_significance_available_for_same_inferential_unit",
    "direction_already_visually_encoded",
    "collapsed_to_shared_legend_clause",
    "effect_magnitude_already_visually_encoded",
}

def _float(x):
    try:return float(x)
    except:return None

def audit(path:Path):
    d=json.loads(path.read_text(encoding="utf-8")); blocking=[]; review=[]
    for flag in d.get("review_flags",[]):
        if flag.get("type")=="LEGEND_BUDGET_REQUIRES_RESTRUCTURE":
            blocking.append({**flag,"type":"UNRESOLVED_LEGEND_RESTRUCTURE_REQUIRED"})
    for fig in d.get("figures",[]):
        for p in fig.get("panels",[]):
            items=p.get("direct_annotations",[])+p.get("legend_annotations",[])+p.get("suppressed_annotations",[])
            groups={}; claims={}
            for x in items:
                if x.get("redundancy_group"):
                    groups.setdefault(x["redundancy_group"],[]).append(x)
                if x.get("claim_id"):
                    claims.setdefault(x["claim_id"],[]).append(x)
                typ=x.get("statistic_type")
                raw=x.get("raw_value")
                val=_float(raw)
                if typ in SIG_TYPES and raw not in {None,""}:
                    if val is None or not (0<=val<=1):
                        blocking.append({"type":"INVALID_SIGNIFICANCE_VALUE","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id"),"value":raw})
                if typ=="n" and raw not in {None,""}:
                    if val is None or val<=0 or abs(val-round(val))>1e-9:
                        blocking.append({"type":"INVALID_SAMPLE_SIZE","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id"),"value":raw})
                nr=x.get("null_reference")
                if nr not in {None,""} and _float(nr) is None:
                    blocking.append({"type":"INVALID_NULL_REFERENCE","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id"),"null_reference":nr})
                if typ=="ci":
                    lo=_float(x.get("lower")); hi=_float(x.get("upper"))
                    if (x.get("lower") or x.get("upper")) and (lo is None or hi is None or lo>hi):
                        blocking.append({"type":"INVALID_CI_BOUNDS","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id"),"lower":x.get("lower"),"upper":x.get("upper")})
                    lvl=_float(x.get("interval_level"))
                    if x.get("interval_level") and (lvl is None or not (0<lvl<100)):
                        blocking.append({"type":"INVALID_INTERVAL_LEVEL","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id"),"interval_level":x.get("interval_level")})
                if x.get("disposition")=="SUPPRESS" and x.get("statistical_necessity")=="required":
                    rs=set(x.get("reasons") or [])
                    if not rs.intersection(SAFE_REQUIRED_SUPPRESSION):
                        blocking.append({"type":"REQUIRED_ITEM_SUPPRESSED_WITHOUT_ALTERNATIVE","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id")})
                if x.get("disposition")=="DIRECT" and typ=="method":
                    blocking.append({"type":"METHOD_PROSE_IN_DATA_VIEWPORT","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id")})
                if x.get("disposition")=="DIRECT" and typ=="direction" and x.get("direction_encoded"):
                    review.append({"type":"REDUNDANT_DIRECTION_DIRECT","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id")})
                if x.get("disposition")=="DIRECT" and typ=="ci" and x.get("uncertainty_encoded") and not x.get("exact_value_required"):
                    review.append({"type":"NUMERIC_CI_DUPLICATES_GRAPHIC_ENCODING","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"annotation_id":x.get("annotation_id")})
            for grp,xs in groups.items():
                direct_types={x.get("statistic_type") for x in xs if x.get("disposition")=="DIRECT"}
                if "p_value" in direct_types and direct_types.intersection({"adjusted_p","fdr","q_value"}):
                    review.append({"type":"RAW_AND_ADJUSTED_SIGNIFICANCE_BOTH_DIRECT","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"redundancy_group":grp})
            for cid,xs in claims.items():
                if not any(x.get("primary_test") for x in xs):
                    continue
                effects=[x for x in xs if x.get("statistic_type")=="effect_size"]
                if effects and all(x.get("disposition")=="SUPPRESS" and not x.get("estimate_encoded") for x in effects):
                    blocking.append({"type":"PRIMARY_CLAIM_EFFECT_MAGNITUDE_LOST","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"claim_id":cid})
                cis=[x for x in xs if x.get("statistic_type")=="ci"]
                if cis and all(x.get("disposition")=="SUPPRESS" and not x.get("uncertainty_encoded") for x in cis):
                    blocking.append({"type":"PRIMARY_CLAIM_UNCERTAINTY_LOST","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id"),"claim_id":cid})
            if p.get("density",{}).get("direct_count",0)>p.get("density",{}).get("direct_budget",999):
                blocking.append({"type":"DIRECT_ANNOTATION_BUDGET_EXCEEDED","figure_id":fig.get("figure_id"),"panel_id":p.get("panel_id")})
    return {"blocking":blocking,"review":review,"pass":not blocking}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("--out")
    a=ap.parse_args(); res=audit(Path(a.plan)); txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
