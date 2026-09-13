from __future__ import annotations
import argparse, json
from pathlib import Path
import fitz

def rect_area(r: fitz.Rect) -> float:
    return max(0.0, r.width) * max(0.0, r.height)

def intersection_area(a: fitz.Rect, b: fitz.Rect) -> float:
    i = a & b
    return rect_area(i) if not i.is_empty else 0.0

def extract_text(page):
    spans=[]
    for bi,b in enumerate(page.get_text("dict")["blocks"]):
        for li,ln in enumerate(b.get("lines",[])):
            for si,sp in enumerate(ln.get("spans",[])):
                txt=sp["text"].strip()
                if txt:
                    spans.append({
                        "text":txt,
                        "bbox":list(sp["bbox"]),
                        "size_pt":float(sp["size"]),
                        "block":bi,"line":li,"span":si,
                    })
    return spans

def extract_drawings(page):
    out=[]
    for di,d in enumerate(page.get_drawings()):
        out.append({
            "index":di,
            "bbox":list(d["rect"]),
            "fill":str(d.get("fill")),
            "color":str(d.get("color")),
            "width":d.get("width"),
            "items":len(d.get("items",[])),
        })
    return out

def audit(
    pdf: Path,
    text_text_min_area=1.0,
    text_drawing_min_area=2.0,
    max_review_items=200,
):
    doc=fitz.open(pdf)
    report={
        "file":str(pdf),
        "pages":[],
        "blocking_count":0,
        "review_count":0,
        "review_truncated":False,
    }

    for pno,page in enumerate(doc):
        texts=extract_text(page)
        drawings=extract_drawings(page)
        blocking=[]
        review=[]
        review_total=0

        # Text-text overlaps: exclude spans in the same PDF line.
        for i,a in enumerate(texts):
            ra=fitz.Rect(a["bbox"])
            for b in texts[i+1:]:
                if a["block"]==b["block"] and a["line"]==b["line"]:
                    continue
                rb=fitz.Rect(b["bbox"])
                area=intersection_area(ra,rb)
                if area >= text_text_min_area:
                    blocking.append({
                        "type":"text_text_overlap",
                        "area_pt2":round(area,3),
                        "a":a,"b":b
                    })

        # Potential text-drawing collisions are REVIEW, not automatic FAIL.
        for a in texts:
            ra=fitz.Rect(a["bbox"])
            for d in drawings:
                rd=fitz.Rect(d["bbox"])
                area=intersection_area(ra,rd)
                if area >= text_drawing_min_area:
                    review_total += 1
                    if len(review) < max_review_items:
                        review.append({
                            "type":"text_drawing_intersection",
                            "area_pt2":round(area,3),
                            "text":a,
                            "drawing":d,
                        })

        if review_total > len(review):
            report["review_truncated"]=True

        report["pages"].append({
            "page":pno+1,
            "width_pt":page.rect.width,
            "height_pt":page.rect.height,
            "blocking":blocking,
            "review":review,
            "review_total":review_total,
        })
        report["blocking_count"] += len(blocking)
        report["review_count"] += review_total

    doc.close()
    report["blocking_pass"] = report["blocking_count"] == 0
    report["note"] = (
        "Text-drawing intersections are REVIEW flags, not automatic failures. "
        "Use semantic layout contracts plus final-size manual inspection."
    )
    return report

def summary(res):
    return {
        "file":res["file"],
        "blocking_count":res["blocking_count"],
        "review_count":res["review_count"],
        "review_truncated":res["review_truncated"],
        "blocking_pass":res["blocking_pass"],
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--text-text-min-area",type=float,default=1.0)
    ap.add_argument("--text-drawing-min-area",type=float,default=2.0)
    ap.add_argument("--max-review-items",type=int,default=200)
    ap.add_argument("--out", help="Write full JSON report to this file.")
    ap.add_argument("--verbose", action="store_true", help="Print full report instead of concise summary.")
    args=ap.parse_args()

    res=audit(
        Path(args.pdf),
        args.text_text_min_area,
        args.text_drawing_min_area,
        args.max_review_items,
    )

    if args.out:
        Path(args.out).write_text(
            json.dumps(res,indent=2,ensure_ascii=False),
            encoding="utf-8"
        )

    payload=res if args.verbose else summary(res)
    print(json.dumps(payload,indent=2,ensure_ascii=False))
