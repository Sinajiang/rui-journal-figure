from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

VALID_VERIFICATION={"VERIFIED","PARTIAL","FIGURE_DETAIL_UNVERIFIED","UNVERIFIED"}

def audit(path: Path):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    blocking=[]
    review=[]
    seen_ids=set()
    doi_map={}
    title_map={}

    for i,r in enumerate(rows,start=2):
        bid=(r.get("benchmark_id") or "").strip()
        if not bid:
            blocking.append({"type":"missing_benchmark_id","row":i})
        elif bid in seen_ids:
            blocking.append({"type":"duplicate_benchmark_id","row":i,"benchmark_id":bid})
        seen_ids.add(bid)

        required=["title","journal","year","url","retrieval_date","search_round","search_query","verification_status"]
        missing=[k for k in required if not (r.get(k) or "").strip()]
        if missing:
            blocking.append({"type":"missing_provenance_fields","row":i,"benchmark_id":bid,"fields":missing})

        vs=(r.get("verification_status") or "").upper()
        if vs and vs not in VALID_VERIFICATION:
            blocking.append({"type":"invalid_verification_status","row":i,"benchmark_id":bid,"status":vs})

        doi=(r.get("doi") or "").strip().lower()
        title=re.sub(r"[^a-z0-9]+"," ",(r.get("title") or "").lower()).strip()
        if doi:
            if doi in doi_map:
                review.append({"type":"duplicate_doi","benchmark_id":bid,"other":doi_map[doi],"doi":doi})
            doi_map[doi]=bid
        if title:
            if title in title_map:
                review.append({"type":"duplicate_title","benchmark_id":bid,"other":title_map[title]})
            title_map[title]=bid

        if vs=="FIGURE_DETAIL_UNVERIFIED":
            review.append({"type":"figure_detail_unverified","benchmark_id":bid})

    return {"count":len(rows),"blocking":blocking,"review":review,"pass":len(blocking)==0}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidates")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.candidates))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
