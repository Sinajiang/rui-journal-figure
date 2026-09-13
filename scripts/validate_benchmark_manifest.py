from __future__ import annotations
import argparse, csv, json
from pathlib import Path

REQ=[
    "benchmark_id","citation","journal","year","url_or_doi","article_type",
    "scientific_similarity","method_similarity","modality_similarity",
    "figure_relevance","use_reason"
]

def validate(path: Path, min_count=3):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    blocking=[]
    review=[]
    if len(rows)<min_count:
        review.append({"type":"small_benchmark_set","count":len(rows),"recommended_min":min_count})
    ids=set()
    for i,r in enumerate(rows, start=2):
        missing=[k for k in REQ if not (r.get(k) or "").strip()]
        if missing:
            blocking.append({"type":"missing_fields","row":i,"fields":missing})
        bid=r.get("benchmark_id")
        if bid in ids:
            blocking.append({"type":"duplicate_benchmark_id","row":i,"benchmark_id":bid})
        ids.add(bid)
    return {"count":len(rows),"blocking":blocking,"review":review,"pass":len(blocking)==0}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--min-count",type=int,default=3)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=validate(Path(args.manifest),args.min_count)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
