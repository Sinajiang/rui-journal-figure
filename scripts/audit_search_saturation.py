from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def truthy(x):
    return str(x).strip().lower() in {"1","true","yes","y"}

def audit(path: Path, min_selected=5, saturation_rounds=2):
    rows=list(csv.DictReader(path.open(encoding="utf-8"),delimiter="\t"))
    if not rows:
        return {"pass":False,"stop":False,"reason":"no_search_rounds"}

    selected=sum(int(r.get("eligible_added") or 0) for r in rows)
    tail=rows[-saturation_rounds:] if len(rows)>=saturation_rounds else rows
    stagnant=len(tail)>=saturation_rounds and all(
        int(r.get("new_high_ranked_added") or 0)==0 and int(r.get("new_grammar_patterns") or 0)==0
        for r in tail
    )
    stop=(selected>=min_selected and stagnant)
    return {
        "rounds":len(rows),
        "eligible_added_total":selected,
        "minimum_selected":min_selected,
        "saturation_rounds":saturation_rounds,
        "recent_rounds_stagnant":stagnant,
        "stop":stop,
        "pass":True,
        "reason":"saturation_reached" if stop else "continue_search"
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("round_log")
    ap.add_argument("--min-selected",type=int,default=5)
    ap.add_argument("--saturation-rounds",type=int,default=2)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.round_log),args.min_selected,args.saturation_rounds)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
