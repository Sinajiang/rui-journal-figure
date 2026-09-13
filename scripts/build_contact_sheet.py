from pathlib import Path
import argparse
from PIL import Image

def build(paths, out, cell_width=1200, gap=30):
    ims=[]
    for p in paths:
        im=Image.open(p).convert("RGB")
        r=cell_width/im.width
        ims.append(im.resize((cell_width, round(im.height*r)), Image.Resampling.LANCZOS))
    rows=[]
    for i in range(0, len(ims), 2):
        row=ims[i:i+2]
        h=max(x.height for x in row)
        canvas=Image.new("RGB",(cell_width*2+gap,h),"white")
        canvas.paste(row[0],(0,0))
        if len(row)>1:
            canvas.paste(row[1],(cell_width+gap,0))
        rows.append(canvas)
    H=sum(r.height for r in rows)+gap*(len(rows)-1)
    outim=Image.new("RGB",(cell_width*2+gap,H),"white")
    y=0
    for r in rows:
        outim.paste(r,(0,y)); y+=r.height+gap
    outim.save(out)

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("images", nargs="+")
    args=ap.parse_args()
    build(args.images,args.out)
