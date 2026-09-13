from __future__ import annotations
import argparse, json
from pathlib import Path
from PIL import Image
from submission_compiler_utils import load_yaml, resolve

def audit(manifest_path: Path, min_dpi=300):
    m=load_yaml(manifest_path); base=manifest_path.parent
    blocking=[]; review=[]; figures=[]
    for f in m.get("figures",[]) or []:
        n=f["number"]; tp=resolve(base,f.get("tiff"))
        if not tp or not tp.exists():
            review.append({"type":"tiff_missing","figure":n})
            continue
        im=Image.open(tp)
        dpi=im.info.get("dpi",(None,None))
        dx=float(dpi[0]) if dpi and dpi[0] else None
        dy=float(dpi[1]) if dpi and dpi[1] else None
        rec={"figure":n,"path":str(tp),"width_px":im.width,"height_px":im.height,"mode":im.mode,"dpi_x":dx,"dpi_y":dy}
        figures.append(rec)
        if dx is not None and dx < min_dpi-1:
            blocking.append({"type":"dpi_below_minimum","figure":n,"dpi":dx,"minimum":min_dpi})
        if im.mode not in {"RGB","RGBA"}:
            review.append({"type":"unexpected_color_mode","figure":n,"mode":im.mode})
    return {"figures":figures,"blocking":blocking,"review":review,"pass":len(blocking)==0}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--min-dpi",type=float,default=300)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.manifest),args.min_dpi)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
