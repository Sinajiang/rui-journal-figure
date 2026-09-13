from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

DIMS=[
    "scientific_fidelity",
    "claim_coverage",
    "contribution_visibility",
    "evidence_diversity",
    "benchmark_concordance",
    "journal_fit",
    "information_efficiency",
    "visual_feasibility",
    "evidence_boundary_integrity",
    "source_traceability",
]

DEFAULT_WEIGHTS={
    "scientific_fidelity":1.5,
    "claim_coverage":1.25,
    "contribution_visibility":1.2,
    "evidence_diversity":1.0,
    "benchmark_concordance":0.8,
    "journal_fit":0.9,
    "information_efficiency":1.0,
    "visual_feasibility":1.0,
    "evidence_boundary_integrity":1.5,
    "source_traceability":1.2,
}

def score(plan_path: Path, weights=None):
    p=yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    s=p.get("score") or {}
    weights=weights or DEFAULT_WEIGHTS
    missing=[d for d in DIMS if s.get(d) is None]
    invalid=[d for d in DIMS if s.get(d) is not None and not (0 <= float(s[d]) <= 10)]
    if missing or invalid:
        return {
            "candidate_id":p.get("candidate_id"),
            "pass":False,
            "missing_scores":missing,
            "invalid_scores":invalid
        }
    numerator=sum(float(s[d])*weights[d] for d in DIMS)
    denom=sum(weights.values())
    total=numerator/denom
    return {
        "candidate_id":p.get("candidate_id"),
        "pass":True,
        "weighted_score_0_to_10":round(total,3),
        "dimension_scores":{d:float(s[d]) for d in DIMS},
        "weights":weights
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=score(Path(args.plan))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
