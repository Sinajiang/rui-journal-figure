from __future__ import annotations
import argparse, json
from pathlib import Path
import fitz, yaml

def nrect_to_pdf(rect, page):
    l,b,w,h=rect
    # contract coordinates use bottom-left normalized; PDF uses top-left
    x0=l*page.rect.width
    x1=(l+w)*page.rect.width
    y1=(1-b)*page.rect.height
    y0=(1-(b+h))*page.rect.height
    return fitz.Rect(x0,y0,x1,y1)

def centroid(r):
    return ((r.x0+r.x1)/2,(r.y0+r.y1)/2)

def contains(outer, inner, margin=0.0):
    return (
        inner.x0 >= outer.x0+margin and
        inner.y0 >= outer.y0+margin and
        inner.x1 <= outer.x1-margin and
        inner.y1 <= outer.y1-margin
    )

def audit(pdf_path: Path, contract_path: Path):
    contract=yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    doc=fitz.open(pdf_path)
    if len(doc)!=1:
        raise ValueError("Layout contract audit currently expects a single-page figure PDF.")
    page=doc[0]

    texts=[]
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines",[]):
            for sp in ln.get("spans",[]):
                txt=sp["text"].strip()
                if txt:
                    texts.append({"text":txt,"bbox":fitz.Rect(sp["bbox"]),"size_pt":float(sp["size"])})

    blocking=[]
    review=[]

    # Panel and zone geometry
    panel_rects={}
    for pname,p in contract.get("panels",{}).items():
        pr=nrect_to_pdf(p["rect"],page)
        panel_rects[pname]=pr
        for zname,zrect in (p.get("zones") or {}).items():
            if zrect is None:
                continue
            zr=nrect_to_pdf(zrect,page)
            if not contains(pr,zr,margin=-0.1):
                blocking.append({
                    "type":"zone_outside_panel",
                    "panel":pname,"zone":zname,
                    "panel_rect":list(pr),"zone_rect":list(zr)
                })

    # Cross-panel overlap
    keys=list(panel_rects)
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            inter=panel_rects[a] & panel_rects[b]
            if not inter.is_empty and inter.get_area()>0.5:
                blocking.append({
                    "type":"panel_overlap","a":a,"b":b,
                    "area_pt2":round(inter.get_area(),2)
                })

    # Forbidden regions
    for fr in contract.get("forbidden_regions",[]) or []:
        rr=nrect_to_pdf(fr["rect"],page)
        if fr.get("allow_text",True) is False:
            for t in texts:
                if rr.intersects(t["bbox"]):
                    blocking.append({
                        "type":"text_in_forbidden_region",
                        "region":fr["name"],
                        "text":t["text"],
                        "bbox":list(t["bbox"])
                    })

    # Card containment: any text whose centroid is in a card should be fully inside card.
    tol=(contract.get("geometry_tolerances") or {}).get("boundary_margin_pt",0.6)
    for card in contract.get("cards",[]) or []:
        cr=nrect_to_pdf(card["rect"],page)
        if card.get("text_must_remain_inside",False):
            for t in texts:
                cx,cy=centroid(t["bbox"])
                if cr.contains(fitz.Point(cx,cy)) and not contains(cr,t["bbox"],margin=tol):
                    blocking.append({
                        "type":"card_text_boundary_violation",
                        "card":card["name"],
                        "text":t["text"],
                        "text_bbox":list(t["bbox"]),
                        "card_rect":list(cr)
                    })

    doc.close()
    return {
        "file":str(pdf_path),
        "contract":str(contract_path),
        "blocking":blocking,
        "review":review,
        "pass":len(blocking)==0
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("contract")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.pdf),Path(args.contract))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
