from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def summarize(path: Path):
    data=yaml.safe_load(path.read_text(encoding="utf-8"))
    papers=data.get("benchmark_set",{}).get("papers",[])
    principles=[]
    for p in papers:
        for x in p.get("transferable_principles",[]) or []:
            principles.append(x)
    # stable dedup preserving order
    seen=set()
    uniq=[]
    for x in principles:
        if x not in seen:
            uniq.append(x); seen.add(x)
    return {
        "target_journal":data.get("benchmark_set",{}).get("target_journal"),
        "n_papers":len(papers),
        "transferable_principles":uniq,
        "warning":"Adapt principles; do not copy exact layouts or artwork."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("benchmark_yaml")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=summarize(Path(args.benchmark_yaml))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
