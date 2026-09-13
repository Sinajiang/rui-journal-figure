from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path
from architecture_utils import load_panels, redundancy_score

def compute(path: Path, threshold=0.72):
    panels=load_panels(path)
    pairs=[]
    for i,a in enumerate(panels):
        for b in panels[i+1:]:
            s=redundancy_score(a,b)
            if s>0:
                pairs.append({
                    "panel_a":a["panel_id"],
                    "panel_b":b["panel_id"],
                    "redundancy_score":s,
                    "high_redundancy":s>=threshold
                })
    pairs.sort(key=lambda x:x["redundancy_score"],reverse=True)
    return {"threshold":threshold,"pairs":pairs}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("panel_inventory")
    ap.add_argument("--threshold",type=float,default=0.72)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=compute(Path(args.panel_inventory),args.threshold)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
