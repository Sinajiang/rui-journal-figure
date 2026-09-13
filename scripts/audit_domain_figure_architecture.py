from __future__ import annotations
import argparse, json
from pathlib import Path

def audit(candidate_json: Path, grammar_json: Path, panel_inventory_tsv: Path):
    import csv
    cand=json.loads(candidate_json.read_text(encoding="utf-8"))
    grammar=json.loads(grammar_json.read_text(encoding="utf-8"))
    rows=list(csv.DictReader(panel_inventory_tsv.open(encoding="utf-8"),delimiter="\t"))
    pmap={r["panel_id"]:r for r in rows}

    main_panels=[pid for f in cand.get("figures",[]) for pid in f.get("panels",[])]
    families=set()
    chart_types=set()
    roles=set()
    for pid in main_panels:
        p=pmap.get(pid,{})
        if p.get("evidence_family"): families.add(p["evidence_family"])
        if p.get("chart_type"): chart_types.add(p["chart_type"])
        if p.get("role"): roles.add(p["role"])

    archetype_results=[]
    for arch in grammar.get("main_figure_archetypes",[]):
        req=set(arch.get("evidence_families",[]))
        hit=bool(req & families)
        archetype_results.append({
            "name":arch.get("name"),
            "optional":bool(arch.get("optional",False)),
            "required_evidence_families":sorted(req),
            "covered":hit
        })

    nonoptional=[x for x in archetype_results if not x["optional"]]
    coverage=sum(1 for x in nonoptional if x["covered"])/len(nonoptional) if nonoptional else 1.0

    preferred=set(grammar.get("preferred_chart_types",[]))
    chart_match=sum(1 for x in chart_types if x in preferred)/len(chart_types) if chart_types else 1.0

    review=[]
    if coverage < 0.6:
        review.append({"type":"low_domain_archetype_coverage","coverage":round(coverage,3)})
    if chart_match < 0.5:
        review.append({"type":"low_domain_chart_grammar_match","match":round(chart_match,3)})

    return {
        "main_panels":main_panels,
        "observed_evidence_families":sorted(families),
        "observed_chart_types":sorted(chart_types),
        "archetype_results":archetype_results,
        "domain_archetype_coverage":round(coverage,3),
        "domain_chart_match":round(chart_match,3),
        "review":review,
        "pass":True
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("grammar_json")
    ap.add_argument("panel_inventory")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.candidate_json),Path(args.grammar_json),Path(args.panel_inventory))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
