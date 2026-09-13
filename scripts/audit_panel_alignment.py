from __future__ import annotations
import argparse, json
from pathlib import Path

def audit(rects, tolerance=0.015):
    """
    rects: dict panel -> [left, bottom, width, height] in normalized figure coordinates.
    Checks repeated widths/heights and overlap.
    """
    keys = list(rects)
    overlaps = []
    for i, a in enumerate(keys):
        ax, ay, aw, ah = rects[a]
        for b in keys[i+1:]:
            bx, by, bw, bh = rects[b]
            ov = not (ax+aw <= bx or bx+bw <= ax or ay+ah <= by or by+bh <= ay)
            if ov:
                overlaps.append([a,b])
    return {"panel_rects": rects, "overlap_pairs": overlaps, "pass": len(overlaps)==0}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file", help="JSON mapping panel -> [left,bottom,width,height]")
    ap.add_argument("--out")
    args = ap.parse_args()
    rects = json.loads(Path(args.json_file).read_text())
    res = audit(rects)
    txt = json.dumps(res, indent=2)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt)
