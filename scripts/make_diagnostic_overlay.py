from __future__ import annotations
import argparse, json
from pathlib import Path
import fitz, yaml

def nrect_to_pdf(rect,page):
    l,b,w,h=rect
    x0=l*page.rect.width
    x1=(l+w)*page.rect.width
    y1=(1-b)*page.rect.height
    y0=(1-(b+h))*page.rect.height
    return fitz.Rect(x0,y0,x1,y1)

def overlay(pdf_path: Path, out_pdf: Path, contract_path: Path|None=None):
    doc=fitz.open(pdf_path)
    for page in doc:
        # text boxes
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines",[]):
                for sp in ln.get("spans",[]):
                    txt=sp["text"].strip()
                    if not txt:
                        continue
                    r=fitz.Rect(sp["bbox"])
                    page.draw_rect(r,color=(1,0,0),width=0.4,overlay=True)

        # drawing bboxes
        for d in page.get_drawings():
            page.draw_rect(d["rect"],color=(0,0.5,1),width=0.25,overlay=True)

        # semantic layout
        if contract_path:
            c=yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            for pname,p in c.get("panels",{}).items():
                pr=nrect_to_pdf(p["rect"],page)
                page.draw_rect(pr,color=(0,0.6,0),width=0.8,overlay=True)
                page.insert_text((pr.x0+2,pr.y0+8),f"PANEL {pname}",fontsize=5,color=(0,0.5,0),overlay=True)
                for zname,zr0 in (p.get("zones") or {}).items():
                    if zr0 is None: continue
                    zr=nrect_to_pdf(zr0,page)
                    page.draw_rect(zr,color=(0.7,0,0.8),width=0.5,overlay=True)
                    page.insert_text((zr.x0+2,zr.y0+7),zname,fontsize=4.5,color=(0.6,0,0.7),overlay=True)

            for fr in c.get("forbidden_regions",[]) or []:
                rr=nrect_to_pdf(fr["rect"],page)
                page.draw_rect(rr,color=(1,0.4,0),fill=(1,0.9,0.7),fill_opacity=0.18,width=0.7,overlay=True)
                page.insert_text((rr.x0+2,rr.y0+7),fr["name"],fontsize=4.5,color=(0.8,0.2,0),overlay=True)

    doc.save(out_pdf)
    doc.close()

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_pdf")
    ap.add_argument("--contract")
    args=ap.parse_args()
    overlay(Path(args.pdf),Path(args.out_pdf),Path(args.contract) if args.contract else None)
