from __future__ import annotations
import argparse, json, re
from pathlib import Path
from extract_figure_mentions import extract

def nums(items, key):
    out=[]
    for x in items:
        v=x[key]
        if v.startswith("S"):
            try: out.append(int(v[1:]))
            except: pass
    return out

def seq_issues(values, label):
    if not values:
        return []
    unique=sorted(set(values))
    expected=list(range(1,max(unique)+1))
    issues=[]
    if unique != expected:
        issues.append({"type":"supplementary_sequence_gap","kind":label,"observed":unique,"expected":expected})
    return issues

def audit(manuscript: Path):
    m=extract(manuscript)
    blocking=[]
    blocking += seq_issues(nums(m["figures"],"figure"),"figure")
    blocking += seq_issues(nums(m["tables"],"table"),"table")
    return {"file":str(manuscript),"blocking":blocking,"pass":len(blocking)==0,"mentions":m}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manuscript")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.manuscript))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
