from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from pathlib import Path
import yaml

BOOL_TRUE={"1","true","yes","y","t"}
ADJ_TYPES={"adjusted_p","fdr","q_value"}
SIG_TYPES={"p_value","adjusted_p","fdr","q_value"}

def b(x):
    return str(x or "").strip().lower() in BOOL_TRUE

def f(x, default=0.0):
    try: return float(x)
    except: return default

def load_contract(path:Path|None):
    if path:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return yaml.safe_load((Path(__file__).resolve().parents[1]/"templates/annotation_intelligence_contract.yaml").read_text(encoding="utf-8"))

def load_benchmark(path:Path|None):
    if not path or not path.exists(): return {}
    return json.loads(path.read_text(encoding="utf-8"))

def load_hierarchy(path:Path|None):
    if not path or not path.exists(): return {}
    d=json.loads(path.read_text(encoding="utf-8"))
    return {p["panel_id"]:p for fig in d.get("figures",[]) for p in fig.get("panels",[])}

def benchmark_rate(bench, stat_type, where):
    k="annotation_statistics"
    obj=(bench.get(k) or {}).get(stat_type) or {}
    v=obj.get(f"{where}_rate")
    return f(v,0.0)

def _compose(label, core):
    label=(label or "").strip()
    core=(core or "").strip()
    if not label: return core
    if not core: return label
    if core.lower().startswith(label.lower()): return core
    norm=lambda x: "".join(ch.lower() for ch in x if ch.isalnum())
    if norm(label) in {norm(core.split("=")[0]), norm(core.split("<")[0])}:
        return core
    return f"{label}, {core}"

def _fmt_sig(val, sig=2):
    return f"{float(val):.{int(sig)}g}"

def _infer_null_reference(row):
    explicit=(row.get("null_reference") or "").strip()
    if explicit:
        try:return float(explicit)
        except:return None
    metric=(row.get("effect_metric") or "").strip().lower().replace(" ","")
    if metric in {"or","oddsratio","hr","hazardratio","rr","riskratio","irr","incidencerateratio","pr","prevalenceratio"}:
        return 1.0
    return 0.0

def _fmt_preserve_null(val, sig, null_ref):
    v=float(val); core=_fmt_sig(v,sig)
    if null_ref is None or v==null_ref:
        return core
    try: rv=float(core)
    except:return core
    original_side=1 if v>null_ref else -1
    rounded_side=1 if rv>null_ref else (-1 if rv<null_ref else 0)
    if rounded_side==original_side:
        return core
    for dec in range(2,8):
        core=f"{v:.{dec}f}".rstrip("0").rstrip(".")
        if core in {"-0",""}: core="0"
        rv=float(core)
        rounded_side=1 if rv>null_ref else (-1 if rv<null_ref else 0)
        if rounded_side==original_side:
            return core
    return f"{v:.8g}"

def precision_text(row, contract):
    typ=(row.get("statistic_type") or "").strip()
    label=(row.get("label") or "").strip()
    raw=(row.get("value") or "").strip()
    display=(row.get("display_text") or "").strip()
    cfg=(contract.get("precision") or {}).get(typ,{})
    if display:
        return _compose(label,display)
    if typ=="ci":
        lo=(row.get("lower") or "").strip(); hi=(row.get("upper") or "").strip()
        if lo and hi:
            try:
                sig=int(cfg.get("significant_digits",2)); level=(row.get("interval_level") or "95").strip(); null_ref=_infer_null_reference(row)
                core=f"{level}% CI {_fmt_preserve_null(float(lo),sig,null_ref)}–{_fmt_preserve_null(float(hi),sig,null_ref)}"
                return _compose(label,core)
            except Exception:
                return _compose(label,f"{lo}–{hi}")
    if not raw:
        return label
    try: val=float(raw)
    except:
        return _compose(label,raw)
    if typ in SIG_TYPES:
        thr=float(cfg.get("scientific_threshold",0.001))
        exact=b(row.get("exact_value_required"))
        if val < thr and not exact:
            core=cfg.get("small_value_format") or f"{typ}<{thr:g}"
            return _compose(label,core)
        dec=int(cfg.get("min_decimals",3))
        prefixes={"p_value":"P","adjusted_p":"adjusted P","fdr":"FDR","q_value":"q"}
        core=f"{prefixes.get(typ,typ)}={val:.{dec}f}"
        return _compose(label,core)
    if typ=="n":
        return _compose(label,f"n={int(round(val))}")
    sig=int(cfg.get("significant_digits",2))
    if typ=="effect_size":
        metric=(row.get("effect_metric") or "").strip(); null_ref=_infer_null_reference(row)
        vtxt=_fmt_preserve_null(val,sig,null_ref)
        core=f"{metric}={vtxt}" if metric else vtxt
        return _compose(label,core)
    if typ=="ci":
        return _compose(label,_fmt_sig(val,sig))
    return _compose(label,raw)

def necessity_weight(level, c):
    return float((c.get("necessity_weights") or {}).get((level or "moderate").lower(),1.0))

def tier_bonus(tier,c):
    cw=c.get("claim_weights") or {}
    return {
      "ANCHOR":float(cw.get("anchor_bonus",1.8)),
      "MAJOR_SUPPORT":float(cw.get("major_support_bonus",1.0)),
      "SUPPORT":float(cw.get("support_bonus",0.4)),
    }.get((tier or "").upper(),0.0)

def decide_row(row,c,bench,hierarchy,adjusted_keys):
    typ=(row.get("statistic_type") or "descriptive").strip().lower()
    defaults=(c.get("statistic_defaults") or {}).get(typ,(c.get("statistic_defaults") or {}).get("descriptive",{}))
    pid=row.get("panel_id","")
    hp=hierarchy.get(pid,{})
    tier=(row.get("panel_tier") or hp.get("tier") or "SUPPORT").upper()
    importance=f(row.get("claim_importance"),3.0)
    necessity=(row.get("statistical_necessity") or "moderate").lower()
    direct=float(defaults.get("base_direct",0))+necessity_weight(necessity,c)
    legend=float(defaults.get("base_legend",0))+0.65*necessity_weight(necessity,c)
    direct += importance*float((c.get("claim_weights") or {}).get("per_point",0.75)) + tier_bonus(tier,c)
    legend += importance*0.25

    bd=f(row.get("benchmark_direct_rate"),benchmark_rate(bench,typ,"direct"))
    bl=f(row.get("benchmark_legend_rate"),benchmark_rate(bench,typ,"legend"))
    direct += bd*float((c.get("benchmark_weights") or {}).get("direct_scale",1.4))
    legend += bl*float((c.get("benchmark_weights") or {}).get("legend_scale",1.1))

    reasons=[]; forced=None
    group=(row.get("redundancy_group") or "").strip()
    inferential_unit=(row.get("inferential_unit") or group).strip()
    scope_key=(row.get("figure_id") or "Figure_1", pid, inferential_unit)

    if typ=="method":
        forced="LEGEND"; reasons.append("method_prose_belongs_in_legend")
    if typ=="direction" and b(row.get("direction_encoded")):
        forced="SUPPRESS"; reasons.append("direction_already_visually_encoded")
    if typ=="ci" and b(row.get("uncertainty_encoded")) and not b(row.get("exact_value_required")):
        forced="SUPPRESS"; reasons.append("ci_already_graphically_encoded")
    if typ=="n":
        if b(row.get("n_varies")) and importance>=4:
            direct += 3.0; reasons.append("varying_denominator_is_interpretive")
        else:
            direct -= 3.0; legend += 2.0; reasons.append("sample_size_preferred_in_legend")
        if b(row.get("repeated_across_panels")):
            direct -= 2.0; reasons.append("repeated_n_should_collapse")
    if typ=="p_value" and inferential_unit and scope_key in adjusted_keys and b(row.get("multiplicity_applies")):
        forced="SUPPRESS"; reasons.append("adjusted_significance_available_for_same_inferential_unit")
    if typ in ADJ_TYPES and b(row.get("multiplicity_applies")):
        direct += 1.4; legend += 1.0; reasons.append("multiplicity_aware_statistic_prioritized")
    if typ=="effect_size" and tier in {"ANCHOR","MAJOR_SUPPORT"}:
        direct += 1.6; reasons.append("effect_magnitude_supports_high_importance_claim")
    if typ=="effect_size" and b(row.get("estimate_encoded")):
        if b(row.get("exact_value_required")) or necessity in {"required","high"} and importance>=4:
            direct += 0.5; reasons.append("effect_encoded_but_numeric_value_claim_critical")
        else:
            direct -= 1.8; legend += 0.6; reasons.append("effect_magnitude_already_visually_encoded")
    if typ in SIG_TYPES and importance<3 and necessity in {"low","redundant"}:
        direct -= 2.0
    if b(row.get("repeated_across_panels")):
        legend += 0.8
    if necessity=="redundant" and forced is None:
        forced="SUPPRESS"; reasons.append("declared_redundant")

    thr=c.get("thresholds") or {}
    if forced:
        disposition=forced
    elif direct>=float(thr.get("direct_score",7.0)) and direct>=legend+0.7:
        disposition="DIRECT"
    elif max(direct,legend)>=float(thr.get("legend_score",3.5)):
        disposition="LEGEND"
    else:
        disposition="SUPPRESS"
    if disposition=="DIRECT" and typ=="method": disposition="LEGEND"

    return {
      "annotation_id":row.get("annotation_id"),"claim_id":row.get("claim_id"),
      "statistic_type":typ,"text":precision_text(row,c),"raw_label":row.get("label",""),"raw_value":row.get("value",""),
      "disposition":disposition,"direct_score":round(direct,3),"legend_score":round(legend,3),
      "claim_importance":importance,"statistical_necessity":necessity,"panel_tier":tier,
      "benchmark_direct_rate":round(bd,3),"benchmark_legend_rate":round(bl,3),
      "redundancy_group":group,"reasons":reasons or ["score_based_assignment"],
      "primary_test":b(row.get("primary_test")),"multiplicity_applies":b(row.get("multiplicity_applies")),
      "multiplicity_adjusted":b(row.get("multiplicity_adjusted")),"uncertainty_encoded":b(row.get("uncertainty_encoded")),
      "estimate_encoded":b(row.get("estimate_encoded")),"direction_encoded":b(row.get("direction_encoded")),
      "n_varies":b(row.get("n_varies")),"repeated_across_panels":b(row.get("repeated_across_panels")),
      "exact_value_required":b(row.get("exact_value_required")),
      "inferential_unit":inferential_unit,"effect_metric":(row.get("effect_metric") or "").strip(),
      "lower":(row.get("lower") or "").strip(),"upper":(row.get("upper") or "").strip(),
      "interval_level":(row.get("interval_level") or "").strip(),"display_text":(row.get("display_text") or "").strip(),
      "null_reference":(row.get("null_reference") or "").strip()
    }

def derive(inventory:Path, contract_path:Path|None=None, benchmark_path:Path|None=None, hierarchy_path:Path|None=None):
    c=load_contract(contract_path); bench=load_benchmark(benchmark_path); hierarchy=load_hierarchy(hierarchy_path)
    rows=list(csv.DictReader(inventory.open(encoding="utf-8"),delimiter="\t"))
    # Propagate effect-scale metadata to CI rows belonging to the same local claim/inferential unit.
    # This is presentation metadata only; no statistics are recalculated.
    scale_meta={}
    for r in rows:
        if (r.get("statistic_type") or "").strip().lower()!="effect_size": continue
        local_unit=(r.get("inferential_unit") or r.get("redundancy_group") or r.get("claim_id") or "").strip()
        if not local_unit: continue
        key=(r.get("figure_id") or "Figure_1",r.get("panel_id") or "",local_unit)
        scale_meta[key]={"effect_metric":(r.get("effect_metric") or "").strip(),"null_reference":(r.get("null_reference") or "").strip()}
    for r in rows:
        if (r.get("statistic_type") or "").strip().lower()!="ci": continue
        local_unit=(r.get("inferential_unit") or r.get("redundancy_group") or r.get("claim_id") or "").strip()
        key=(r.get("figure_id") or "Figure_1",r.get("panel_id") or "",local_unit)
        meta=scale_meta.get(key) or {}
        if not (r.get("effect_metric") or "").strip() and meta.get("effect_metric"): r["effect_metric"]=meta["effect_metric"]
        if not (r.get("null_reference") or "").strip() and meta.get("null_reference"): r["null_reference"]=meta["null_reference"]
    adjusted_keys=set()
    for r in rows:
        typ=(r.get("statistic_type") or "").strip().lower(); grp=(r.get("redundancy_group") or "").strip()
        unit=(r.get("inferential_unit") or grp).strip(); raw=(r.get("value") or "").strip()
        if unit and typ in ADJ_TYPES and raw:
            adjusted_keys.add((r.get("figure_id") or "Figure_1",r.get("panel_id") or "",unit))
    decisions=[(r,decide_row(r,c,bench,hierarchy,adjusted_keys)) for r in rows]

    figures=defaultdict(lambda:defaultdict(list))
    for r,d in decisions:
        figures[r.get("figure_id") or "Figure_1"][r.get("panel_id") or "P01"].append(d)

    output={"version":"2.5.1","figures":[],"review_flags":[]}
    ld=c.get("legend_density") or {}
    max_shared=int(ld.get("max_shared_statistical_definitions_per_figure",2))

    for fid,pans in figures.items():
        fitem={"figure_id":fid,"panels":[],"shared_legend_clauses":[],"shared_legend_guidance":[]}
        all_items=[d for ds in pans.values() for d in ds]

        # Collapse genuinely repeated legend context into one figure-level clause.
        repeated=defaultdict(list)
        for d in all_items:
            grp=d.get("redundancy_group")
            if grp and d.get("repeated_across_panels"):
                repeated[grp].append(d)
        for grp,xs in repeated.items():
            if len(xs)<2: continue
            texts=[x.get("text") for x in xs if x.get("text")]
            types={x.get("statistic_type") for x in xs}
            if len(types)==1 and texts and len(set(texts))==1:
                shared=texts[0]
                if next(iter(types))=="n": shared=f"{shared} throughout unless otherwise indicated"
                if len(fitem["shared_legend_clauses"])<max_shared:
                    fitem["shared_legend_clauses"].append(shared)
                    for x in xs:
                        if x.get("disposition")=="LEGEND":
                            x["disposition"]="SUPPRESS"
                            x["reasons"].append("collapsed_to_shared_legend_clause")

        # Guidance is machine/author-facing, not submission legend prose.
        if any(d["statistic_type"]=="ci" and d["uncertainty_encoded"] for d in all_items):
            fitem["shared_legend_guidance"].append("Define the graphical uncertainty interval once using the authorized interval level; do not repeat numeric CI bounds in the data viewport unless exact bounds are claim-critical.")
        if any(d["statistic_type"] in SIG_TYPES for d in all_items):
            fitem["shared_legend_guidance"].append("Name the inferential quantity exactly as analyzed; where multiplicity applies, prefer the authorized adjusted quantity over redundant raw P.")

        for pid,ds in pans.items():
            hp=hierarchy.get(pid,{})
            direct_budget=int(hp.get("max_annotation_lines",999))
            legend_budget=int(hp.get("max_legend_items",999))

            semantic_priority={"effect_size":6,"ci":5,"adjusted_p":4,"fdr":4,"q_value":4,"p_value":3,"n":2,"direction":1,"threshold":1,"descriptive":0,"method":-1}
            direct=sorted([d for d in ds if d["disposition"]=="DIRECT"],key=lambda x:(x["statistical_necessity"] not in {"required","high"},-x["claim_importance"],-semantic_priority.get(x["statistic_type"],0),-x["direct_score"]))
            legend=sorted([d for d in ds if d["disposition"]=="LEGEND"],key=lambda x:(x["statistical_necessity"] not in {"required","high"},-x["claim_importance"],-x["legend_score"]))
            supp=[d for d in ds if d["disposition"]=="SUPPRESS"]

            # Rebalance direct annotations into legend before ever shrinking text.
            if len(direct)>direct_budget:
                keep=direct[:direct_budget]; moved=direct[direct_budget:]
                for d in moved:
                    d["disposition"]="LEGEND"; d["reasons"].append("moved_to_legend_due_to_physical_annotation_budget")
                direct=keep; legend=legend+moved
                output["review_flags"].append({"type":"DIRECT_ANNOTATION_BUDGET_EXCEEDED_REBALANCED","figure_id":fid,"panel_id":pid,"budget":direct_budget})

            # Legend budget: automatically drop only low/redundant material; never silently drop required/high items.
            if len(legend)>legend_budget:
                ranked=sorted(legend,key=lambda x:(x["statistical_necessity"] not in {"required","high"},-x["claim_importance"],-x["legend_score"]))
                keep=[]; overflow=[]
                for x in ranked:
                    if len(keep)<legend_budget:
                        keep.append(x)
                    else:
                        overflow.append(x)
                unresolved=[]
                for x in overflow:
                    if x["statistical_necessity"] in {"low","redundant"}:
                        x["disposition"]="SUPPRESS"; x["reasons"].append("suppressed_due_to_legend_density_budget")
                        supp.append(x)
                    else:
                        unresolved.append(x)
                legend=keep+unresolved
                if unresolved:
                    output["review_flags"].append({"type":"LEGEND_BUDGET_REQUIRES_RESTRUCTURE","figure_id":fid,"panel_id":pid,"budget":legend_budget,"unresolved":len(unresolved)})
                else:
                    output["review_flags"].append({"type":"LEGEND_BUDGET_AUTOMATICALLY_REBALANCED","figure_id":fid,"panel_id":pid,"budget":legend_budget})

            stat_leg=[d for d in legend if d["statistic_type"]!="method"]
            method_leg=[d for d in legend if d["statistic_type"]=="method"]
            if len(stat_leg)>int(ld.get("max_statistical_clauses_per_panel",3)):
                output["review_flags"].append({"type":"LEGEND_STATISTICAL_DENSITY_HIGH","figure_id":fid,"panel_id":pid,"count":len(stat_leg)})
            if len(method_leg)>int(ld.get("max_method_clauses_per_panel",2)):
                output["review_flags"].append({"type":"LEGEND_METHOD_DENSITY_HIGH","figure_id":fid,"panel_id":pid,"count":len(method_leg)})

            fitem["panels"].append({
              "panel_id":pid,"tier":(hierarchy.get(pid,{}) or {}).get("tier") or (ds[0].get("panel_tier") if ds else ""),
              "direct_annotations":direct,"legend_annotations":legend,"suppressed_annotations":supp,
              "density":{"direct_count":len(direct),"direct_budget":direct_budget,"legend_count":len(legend),"legend_budget":legend_budget,"legend_statistical_clauses":len(stat_leg),"legend_method_clauses":len(method_leg)}
            })
        output["figures"].append(fitem)

    # Summary must reflect the final post-budget dispositions.
    total={"DIRECT":0,"LEGEND":0,"SUPPRESS":0}
    seen=set()
    for fig in output["figures"]:
        for p in fig["panels"]:
            for key,disp in [("direct_annotations","DIRECT"),("legend_annotations","LEGEND"),("suppressed_annotations","SUPPRESS")]:
                for x in p[key]:
                    aid=(fig["figure_id"],p["panel_id"],x.get("annotation_id"))
                    if aid in seen: continue
                    seen.add(aid); total[disp]+=1
    output["summary"]={"direct_count":total["DIRECT"],"legend_count":total["LEGEND"],"suppress_count":total["SUPPRESS"],"candidate_count":sum(total.values())}
    return output

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("inventory")
    ap.add_argument("--contract")
    ap.add_argument("--benchmark-grammar")
    ap.add_argument("--visual-hierarchy")
    ap.add_argument("--out")
    a=ap.parse_args()
    res=derive(Path(a.inventory),Path(a.contract) if a.contract else None,Path(a.benchmark_grammar) if a.benchmark_grammar else None,Path(a.visual_hierarchy) if a.visual_hierarchy else None)
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
