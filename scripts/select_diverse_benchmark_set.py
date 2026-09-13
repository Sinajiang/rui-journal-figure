from __future__ import annotations
import argparse, json
from pathlib import Path

def select(ranked_json: Path, minimum=5, maximum=10, max_per_journal=3):
    data=json.loads(ranked_json.read_text(encoding="utf-8"))
    ranked=data["ranked"]
    chosen=[]
    journal_counts={}

    # First pass: score order with journal cap.
    for x in ranked:
        j=x.get("journal") or "UNKNOWN"
        if journal_counts.get(j,0) >= max_per_journal:
            continue
        chosen.append(x)
        journal_counts[j]=journal_counts.get(j,0)+1
        if len(chosen)>=maximum:
            break

    # If cap prevents minimum, fill by score.
    if len(chosen)<minimum:
        chosen_ids={x["benchmark_id"] for x in chosen}
        for x in ranked:
            if x["benchmark_id"] in chosen_ids:
                continue
            chosen.append(x)
            if len(chosen)>=minimum:
                break

    return {
        "selected":chosen[:maximum],
        "selected_count":min(len(chosen),maximum),
        "minimum_requested":minimum,
        "maximum_requested":maximum,
        "journal_counts":journal_counts,
        "manual_diversity_review_required":True
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("ranked_json")
    ap.add_argument("--minimum",type=int,default=5)
    ap.add_argument("--maximum",type=int,default=10)
    ap.add_argument("--max-per-journal",type=int,default=3)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=select(Path(args.ranked_json),args.minimum,args.maximum,args.max_per_journal)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
