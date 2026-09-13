from __future__ import annotations
import argparse, json, math
from pathlib import Path
import yaml

from architecture_utils import (
    load_panels, redundancy_score, panel_utility, role_rank
)

ELIGIBLE_BASE={"DIRECTLY_AVAILABLE"}

def eligible(panel, allow_structurally_adaptable):
    allowed=set(ELIGIBLE_BASE)
    if allow_structurally_adaptable:
        allowed.add("STRUCTURALLY_ADAPTABLE")
    return (
        panel.get("main_eligible",False)
        and panel.get("availability") in allowed
    )

def claim_priority_map(inp):
    return {
        cid:float(meta.get("priority",0))
        for cid,meta in (inp.get("claims",{}) or {}).items()
    }

def weighted_claim_coverage(selected, claim_priority):
    covered=set()
    for p in selected:
        covered.update(p.get("claim_ids",[]))
    denom=sum(claim_priority.values())
    num=sum(v for k,v in claim_priority.items() if k in covered)
    return (num/denom if denom else 1.0), covered

def reduce_redundancy(selected, threshold):
    selected=sorted(selected,key=panel_utility,reverse=True)
    kept=[]
    merged=[]
    for p in selected:
        conflicts=[
            (q,redundancy_score(p,q))
            for q in kept
            if redundancy_score(p,q)>=threshold
        ]
        if conflicts and not p.get("must_main"):
            partner,maxs=max(conflicts,key=lambda x:x[1])
            # retain if panel has a different role and meaningful contribution;
            # otherwise demote/merge.
            if (p.get("role") or "").lower() == (partner.get("role") or "").lower():
                merged.append((p,partner,maxs))
                continue
        kept.append(p)
    return kept, merged

def group_by_theme(selected):
    groups={}
    for p in selected:
        groups.setdefault(p.get("theme") or "misc",[]).append(p)
    return groups

def group_claims(group):
    s=set()
    for p in group:
        s.update(p.get("claim_ids",[]))
    return s

def group_density(group):
    return sum(p.get("visual_density",0) for p in group)

def group_utility(group):
    return sum(panel_utility(p) for p in group)

def group_overlap(a,b):
    ca=group_claims(a); cb=group_claims(b)
    if not ca and not cb: return 0.0
    return len(ca&cb)/max(1,len(ca|cb))

def merge_groups(groups, target):
    # groups: dict theme -> list panels
    groups={k:list(v) for k,v in groups.items()}
    while len(groups)>target:
        keys=list(groups)
        best=None
        for i,a in enumerate(keys):
            for b in keys[i+1:]:
                ov=group_overlap(groups[a],groups[b])
                # Prefer claim-related merge; secondarily small total density.
                rank=(ov, -(group_density(groups[a])+group_density(groups[b])))
                if best is None or rank>best[0]:
                    best=(rank,a,b)
        if best is None: break
        _,a,b=best
        newkey=f"{a}+{b}"
        groups[newkey]=groups.pop(a)+groups.pop(b)
    return groups

def split_groups(groups, target):
    groups={k:list(v) for k,v in groups.items()}
    counter=1
    while len(groups)<target:
        # pick largest splittable group
        candidates=[
            (group_density(v),k,v)
            for k,v in groups.items()
            if len(v)>=2
        ]
        if not candidates:
            break
        _,k,v=max(candidates,key=lambda x:x[0])
        # Split by evidence family first.
        fam={}
        for p in v:
            fam.setdefault(p.get("evidence_family") or p.get("role") or "misc",[]).append(p)
        if len(fam)>=2:
            parts=sorted(fam.items(),key=lambda kv:min(p.get("narrative_order",999) for p in kv[1]))
            first_name,first=parts[0]
            rest=[p for _,grp in parts[1:] for p in grp]
        else:
            vv=sorted(v,key=lambda p:(p.get("narrative_order",999),role_rank(p.get("role"))))
            cut=max(1,len(vv)//2)
            first=vv[:cut]; rest=vv[cut:]
            first_name="part"
        if not rest:
            break
        groups.pop(k)
        groups[f"{k}:{first_name}"]=first
        groups[f"{k}:split{counter}"]=rest
        counter+=1
    return groups

def enforce_capacity(groups, max_panels, max_density):
    supplement=[]
    hard=[]
    repaired={}
    for k,v in groups.items():
        vv=sorted(v,key=lambda p:(p.get("narrative_order",999),role_rank(p.get("role"))))
        # demote lowest-utility non-must panels until capacity okay
        while (len(vv)>max_panels or group_density(vv)>max_density):
            movable=[p for p in vv if not p.get("must_main")]
            if not movable:
                hard.append({
                    "type":"must_main_capacity_violation",
                    "theme":k,
                    "panel_count":len(vv),
                    "density":group_density(vv)
                })
                break
            victim=min(movable,key=panel_utility)
            vv.remove(victim)
            supplement.append(victim)
        repaired[k]=vv
    return repaired,supplement,hard

def score_architecture(figures, selected, supplement, inp, hard, redundancy_pairs):
    claims=claim_priority_map(inp)
    coverage,_=weighted_claim_coverage(selected,claims)

    avg_utility=(sum(panel_utility(p) for p in selected)/len(selected)) if selected else 0
    avg_contrib=(sum(p.get("contribution_score",0) for p in selected)/len(selected)) if selected else 0
    families={p.get("evidence_family") for p in selected if p.get("evidence_family")}
    diversity=min(10.0,2.0*len(families))
    avg_bench=(sum(p.get("benchmark_support_score",0) for p in selected)/len(selected)) if selected else 0
    avg_trace=(sum(p.get("source_traceability_score",0) for p in selected)/len(selected)) if selected else 0

    constraints=inp.get("constraints",{}) or {}
    max_panels=float(constraints.get("max_panels_per_figure",4))
    max_density=float(constraints.get("max_visual_density_per_figure",26))
    visual_scores=[]
    for f in figures:
        pc=len(f["panels"]); den=f["total_visual_density"]
        pscore=max(0,10-2*max(0,pc-max_panels))
        dscore=max(0,10-0.7*max(0,den-max_density))
        visual_scores.append(min(pscore,dscore))
    visual=sum(visual_scores)/len(visual_scores) if visual_scores else 0

    preferred=(inp.get("benchmark_prior") or {}).get("preferred_main_figure_count")
    if preferred is None:
        bench_count_fit=8.0
    else:
        bench_count_fit=max(0.0,10.0-2.0*abs(len(figures)-float(preferred)))
    benchmark_concordance=0.7*avg_bench+0.3*bench_count_fit

    # information efficiency rewards main coverage with controlled panel count
    nmain=len(selected)
    info_eff=max(0.0,min(10.0, 10*coverage - 0.25*max(0,nmain-4*len(figures))))

    # redundancy control
    high_red=sum(1 for x in redundancy_pairs if x["high_redundancy"])
    redundancy_control=max(0.0,10.0-1.5*high_red)

    boundary=10.0 if not hard else max(0.0,10.0-2.0*len(hard))
    scientific=10.0 if not hard else max(0.0,10.0-2.5*len(hard))
    journal=10.0
    max_displays=(inp.get("journal_constraints") or {}).get("max_main_displays")
    if max_displays is not None and len(figures)>float(max_displays):
        journal=0.0

    dims={
        "scientific_fidelity":scientific,
        "weighted_claim_coverage":10*coverage,
        "contribution_visibility":avg_contrib,
        "evidence_diversity":diversity,
        "benchmark_concordance":benchmark_concordance,
        "journal_fit":journal,
        "information_efficiency":info_eff,
        "visual_feasibility":visual,
        "evidence_boundary_integrity":boundary,
        "source_traceability":avg_trace,
        "redundancy_control":redundancy_control,
    }
    weights={
        "scientific_fidelity":1.5,
        "weighted_claim_coverage":1.4,
        "contribution_visibility":1.25,
        "evidence_diversity":0.9,
        "benchmark_concordance":0.8,
        "journal_fit":1.0,
        "information_efficiency":1.0,
        "visual_feasibility":1.1,
        "evidence_boundary_integrity":1.5,
        "source_traceability":1.2,
        "redundancy_control":1.0,
    }
    total=sum(dims[k]*weights[k] for k in dims)/sum(weights.values())
    return {k:round(v,3) for k,v in dims.items()} | {"overall_score":round(total,3)}

def optimize(input_path: Path):
    inp=yaml.safe_load(input_path.read_text(encoding="utf-8"))
    inventory=(input_path.parent / inp["panel_inventory_tsv"]).resolve()
    panels=load_panels(inventory)

    constraints=inp.get("constraints",{}) or {}
    allow_adapt=bool(constraints.get("allow_structurally_adaptable",True))
    red_thr=float(constraints.get("redundancy_threshold",0.72))
    max_panels=int(constraints.get("max_panels_per_figure",4))
    max_density=float(constraints.get("max_visual_density_per_figure",26))
    min_fig=int(constraints.get("figure_count_min",3))
    max_fig=int(constraints.get("figure_count_max",5))

    eligible_panels=[p for p in panels if eligible(p,allow_adapt)]
    upgrade=[p for p in panels if p.get("availability")=="OPTIONAL_NEW_ANALYSIS"]
    not_app=[p for p in panels if p.get("availability")=="NOT_APPLICABLE"]

    # Start with must-main and then high utility / claim coverage.
    selected=[p for p in eligible_panels if p.get("must_main")]
    selected_ids={p["panel_id"] for p in selected}
    claims=claim_priority_map(inp)

    candidates=sorted(
        [p for p in eligible_panels if p["panel_id"] not in selected_ids],
        key=lambda p:(panel_utility(p),p.get("priority",0)),
        reverse=True
    )

    # Add panels that cover new claims or are high-contribution evidence.
    covered=set()
    for p in selected: covered.update(p.get("claim_ids",[]))
    for p in candidates:
        new_claim=any(c not in covered for c in p.get("claim_ids",[]))
        if new_claim or p.get("contribution_score",0)>=7 or p.get("role") in {"robustness","external_context","replication"}:
            selected.append(p)
            covered.update(p.get("claim_ids",[]))

    selected, merged_pairs=reduce_redundancy(selected,red_thr)

    # redundancy report among selected
    red_pairs=[]
    for i,a in enumerate(selected):
        for b in selected[i+1:]:
            s=redundancy_score(a,b)
            if s>0:
                red_pairs.append({
                    "panel_a":a["panel_id"],"panel_b":b["panel_id"],
                    "score":s,"high_redundancy":s>=red_thr
                })

    results=[]
    for target in range(min_fig,max_fig+1):
        groups=group_by_theme(selected)
        if len(groups)>target:
            groups=merge_groups(groups,target)
        elif len(groups)<target:
            groups=split_groups(groups,target)

        groups,supp_capacity,hard=enforce_capacity(groups,max_panels,max_density)

        # If still not exact target count, this is advisory, not automatic fail.
        if len(groups)!=target:
            hard.append({
                "type":"target_figure_count_not_reached",
                "target":target,
                "actual":len(groups)
            })

        # Build figure objects in narrative order.
        group_items=list(groups.items())
        group_items.sort(
            key=lambda kv:min((p.get("narrative_order",999) for p in kv[1]),default=999)
        )
        figures=[]
        selected_now=[]
        for idx,(theme,plist) in enumerate(group_items,start=1):
            plist=sorted(plist,key=lambda p:(p.get("narrative_order",999),role_rank(p.get("role"))))
            selected_now.extend(plist)
            cids=sorted(set(c for p in plist for c in p.get("claim_ids",[])))
            figures.append({
                "figure":idx,
                "theme":theme,
                "panels":[p["panel_id"] for p in plist],
                "panel_roles":[p.get("role") for p in plist],
                "claim_ids":cids,
                "total_visual_density":round(group_density(plist),2),
            })

        supp_ids=[p["panel_id"] for p in supp_capacity]
        merged_ids=[p["panel_id"] for p,_,_ in merged_pairs]
        scores=score_architecture(figures,selected_now,supp_capacity,inp,hard,red_pairs)

        # Hard gates
        coverage,covered_now=weighted_claim_coverage(selected_now,claims)
        min_cov=float(constraints.get("minimum_main_claim_coverage",0.0))
        for cid,meta in (inp.get("claims",{}) or {}).items():
            if meta.get("must_cover_main") and cid not in covered_now:
                hard.append({"type":"must_cover_claim_missing","claim_id":cid})
        if coverage < min_cov:
            hard.append({
                "type":"claim_coverage_below_minimum",
                "coverage":round(coverage,4),
                "minimum":min_cov
            })

        results.append({
            "target_figure_count":target,
            "actual_figure_count":len(figures),
            "figures":figures,
            "supplementary_panels":sorted(set(supp_ids+merged_ids)),
            "upgrade_candidates":[p["panel_id"] for p in upgrade],
            "not_applicable":[p["panel_id"] for p in not_app],
            "merged_redundant_pairs":[
                {"panel":p["panel_id"],"partner":q["panel_id"],"score":s}
                for p,q,s in merged_pairs
            ],
            "scores":scores,
            "hard_gates":{"pass":len(hard)==0,"failures":hard},
        })

    eligible_results=[r for r in results if r["hard_gates"]["pass"]]
    ranked=sorted(eligible_results,key=lambda r:r["scores"]["overall_score"],reverse=True)

    return {
        "input":str(input_path),
        "candidates":results,
        "recommended_target_figure_count":ranked[0]["target_figure_count"] if ranked else None,
        "recommended_score":ranked[0]["scores"]["overall_score"] if ranked else None,
        "ranked_eligible":[
            {"target_figure_count":r["target_figure_count"],"score":r["scores"]["overall_score"]}
            for r in ranked
        ],
        "manual_expert_review_required":True,
        "note":"Benchmark figure count is a soft prior. Scientific fidelity and claim coverage have veto power."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("optimizer_input")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=optimize(Path(args.optimizer_input))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
