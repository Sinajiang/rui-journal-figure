from __future__ import annotations
import argparse, csv, re, json
from pathlib import Path

def norm_doi(x):
    x=(x or "").strip().lower()
    x=re.sub(r"^https?://(?:dx\.)?doi\.org/","",x)
    x=re.sub(r"^doi:\s*","",x)
    return x.strip()

def norm_title(x):
    x=(x or "").lower()
    x=re.sub(r"[^a-z0-9]+"," ",x)
    return " ".join(x.split())

def normalize(path: Path, out_path: Path|None=None):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    seen={}
    kept=[]
    duplicates=[]
    for r in rows:
        r["doi"]=norm_doi(r.get("doi"))
        key=("doi",r["doi"]) if r["doi"] else ("title",norm_title(r.get("title")))
        if key in seen:
            duplicates.append({
                "duplicate_benchmark_id":r.get("benchmark_id"),
                "kept_benchmark_id":seen[key],
                "key_type":key[0],
                "key":key[1],
            })
            continue
        seen[key]=r.get("benchmark_id")
        kept.append(r)

    if out_path:
        fields=list(rows[0].keys()) if rows else []
        with out_path.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields,delimiter="\t")
            w.writeheader(); w.writerows(kept)

    return {"input_count":len(rows),"kept_count":len(kept),"duplicates":duplicates}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidates")
    ap.add_argument("--normalized-out")
    ap.add_argument("--report-out")
    args=ap.parse_args()
    res=normalize(
        Path(args.candidates),
        Path(args.normalized_out) if args.normalized_out else None
    )
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.report_out:
        Path(args.report_out).write_text(txt,encoding="utf-8")
