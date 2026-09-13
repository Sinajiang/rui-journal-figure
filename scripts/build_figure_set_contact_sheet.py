from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from submission_compiler_utils import load_yaml, resolve

def build(manifest_path: Path, out: Path, cell_width=1300, gap=36):
    m=load_yaml(manifest_path); base=manifest_path.parent
    items=[]
    for f in m.get("figures",[]) or []:
        pp=resolve(base,f.get("preview"))
        if not pp or not pp.exists():
            continue
        im=Image.open(pp).convert("RGB")
        ratio=cell_width/im.width
        im=im.resize((cell_width,round(im.height*ratio)),Image.Resampling.LANCZOS)
        header=70
        canvas=Image.new("RGB",(cell_width,im.height+header),"white")
        draw=ImageDraw.Draw(canvas)
        draw.text((18,18),f"Figure {f['number']} — {f.get('promoted_version','')}",fill="black")
        canvas.paste(im,(0,header))
        items.append(canvas)

    if not items:
        raise ValueError("No preview images found.")

    cols=2 if len(items)>1 else 1
    rows=(len(items)+cols-1)//cols
    row_heights=[]
    for r in range(rows):
        row_heights.append(max(items[i].height for i in range(r*cols,min((r+1)*cols,len(items)))))
    W=cols*cell_width+(cols-1)*gap
    H=sum(row_heights)+(rows-1)*gap
    sheet=Image.new("RGB",(W,H),"white")
    y=0
    for r in range(rows):
        x=0
        rh=row_heights[r]
        for c in range(cols):
            i=r*cols+c
            if i>=len(items): break
            sheet.paste(items[i],(x,y))
            x+=cell_width+gap
        y+=rh+gap
    sheet.save(out)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--out",required=True)
    ap.add_argument("--cell-width",type=int,default=1300)
    args=ap.parse_args()
    build(Path(args.manifest),Path(args.out),args.cell_width)
