from __future__ import annotations
import argparse, json
from pathlib import Path

def recommend(grammar_json: Path):
    g=json.loads(grammar_json.read_text(encoding="utf-8"))
    return {
        "primary_domain":g["primary_domain"],
        "recommended_figure_archetypes":g.get("main_figure_archetypes",[]),
        "preferred_chart_types":g.get("preferred_chart_types",[]),
        "move_to_supplementary_when_applicable":g.get("supplementary_preferred",[]),
        "domain_specific_risks":g.get("risk_flags",[]),
        "benchmark_search_terms":g.get("benchmark_terms",[]),
        "boundary":"Recommendations are advisory and cannot authorize unavailable evidence."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("grammar_json")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=recommend(Path(args.grammar_json))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
