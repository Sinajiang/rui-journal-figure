from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def audit(candidate_json: Path, optimizer_input: Path):
    c=json.loads(candidate_json.read_text(encoding="utf-8"))
    inp=yaml.safe_load(optimizer_input.read_text(encoding="utf-8"))
    claims=inp.get("claims",{}) or {}

    covered=set()
    for fig in c.get("figures",[]):
        covered.update(fig.get("claim_ids",[]) or [])

    total_weight=sum(float(v.get("priority",0)) for v in claims.values())
    covered_weight=sum(float(v.get("priority",0)) for k,v in claims.items() if k in covered)
    ratio=covered_weight/total_weight if total_weight else 1.0

    blocking=[]
    for cid,meta in claims.items():
        if meta.get("must_cover_main") and cid not in covered:
            blocking.append({"type":"must_cover_claim_missing","claim_id":cid})

    min_cov=float((inp.get("constraints") or {}).get("minimum_main_claim_coverage",0.0))
    if ratio < min_cov:
        blocking.append({
            "type":"weighted_claim_coverage_below_minimum",
            "coverage":round(ratio,4),
            "minimum":min_cov
        })

    return {
        "covered_claims":sorted(covered),
        "weighted_claim_coverage":round(ratio,4),
        "blocking":blocking,
        "pass":len(blocking)==0
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("optimizer_input")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.candidate_json),Path(args.optimizer_input))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
