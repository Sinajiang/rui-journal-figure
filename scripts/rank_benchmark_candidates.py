from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path

SCORE_FIELDS=[
    "target_journal_match",
    "scientific_similarity",
    "method_similarity",
    "modality_similarity",
    "sample_structure_similarity",
    "figure_role_relevance",
    "main_supp_transferability",
    "figure_detail_accessibility",
    "recency_score",
]

WEIGHTS={
    "target_journal_match":0.8,
    "scientific_similarity":1.5,
    "method_similarity":1.25,
    "modality_similarity":1.25,
    "sample_structure_similarity":0.9,
    "figure_role_relevance":1.4,
    "main_supp_transferability":0.8,
    "figure_detail_accessibility":0.7,
    "recency_score":0.5,
}

VERIFICATION_PENALTY={
    "VERIFIED":0.0,
    "PARTIAL":0.6,
    "FIGURE_DETAIL_UNVERIFIED":1.0,
    "UNVERIFIED":1.5,
}

def f(x):
    try: return float(x)
    except: return 0.0

def rank(path: Path):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    ranked=[]
    denom=sum(WEIGHTS.values())
    for r in rows:
        scores={k:f(r.get(k)) for k in SCORE_FIELDS}
        invalid={k:v for k,v in scores.items() if not (0<=v<=5)}
        if invalid:
            ranked.append({
                "benchmark_id":r.get("benchmark_id"),
                "eligible":False,
                "reason":"score_out_of_range",
                "invalid":invalid
            })
            continue
        raw=sum(scores[k]*WEIGHTS[k] for k in SCORE_FIELDS)/denom
        penalty=VERIFICATION_PENALTY.get((r.get("verification_status") or "UNVERIFIED").upper(),1.5)
        total=max(0.0, raw-penalty)
        ranked.append({
            "benchmark_id":r.get("benchmark_id"),
            "title":r.get("title"),
            "journal":r.get("journal"),
            "year":r.get("year"),
            "doi":r.get("doi"),
            "url":r.get("url"),
            "verification_status":r.get("verification_status"),
            "eligible":True,
            "score_0_to_5":round(total,3),
            "raw_score_0_to_5":round(raw,3),
            "verification_penalty":penalty,
            "dimension_scores":scores,
        })
    eligible=sorted([x for x in ranked if x.get("eligible")],key=lambda x:x["score_0_to_5"],reverse=True)
    return {"ranked":eligible,"ineligible":[x for x in ranked if not x.get("eligible")]}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidates")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=rank(Path(args.candidates))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
