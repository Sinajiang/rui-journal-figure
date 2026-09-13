from __future__ import annotations
import argparse, json
from pathlib import Path

def score(audit_json: Path):
    a=json.loads(audit_json.read_text(encoding="utf-8"))
    archetype=float(a.get("domain_archetype_coverage",0))
    chart=float(a.get("domain_chart_match",0))
    domain_score=10*(0.7*archetype+0.3*chart)
    return {
        "domain_fit_score_0_to_10":round(domain_score,3),
        "archetype_coverage":archetype,
        "chart_match":chart,
        "review":a.get("review",[])
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("domain_architecture_audit")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=score(Path(args.domain_architecture_audit))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
