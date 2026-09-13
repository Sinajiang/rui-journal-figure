from __future__ import annotations
import argparse, json
from pathlib import Path
import fitz

def intersects(a, b, pad=0.0):
    ra = fitz.Rect(a); rb = fitz.Rect(b)
    if pad:
        ra = fitz.Rect(ra.x0-pad, ra.y0-pad, ra.x1+pad, ra.y1+pad)
        rb = fitz.Rect(rb.x0-pad, rb.y0-pad, rb.x1+pad, rb.y1+pad)
    return ra.intersects(rb)

def audit(pdf_path: Path, text_pad_pt=0.4):
    doc = fitz.open(pdf_path)
    report = {"file": str(pdf_path), "pages": [], "pass": True}
    for pno, page in enumerate(doc):
        spans = []
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for sp in ln.get("spans", []):
                    txt = sp["text"].strip()
                    if txt:
                        spans.append({"text": txt, "bbox": sp["bbox"]})
        collisions = []
        for i, a in enumerate(spans):
            for j in range(i+1, len(spans)):
                b = spans[j]
                if intersects(a["bbox"], b["bbox"], text_pad_pt):
                    collisions.append({"a": a, "b": b})
        if collisions:
            report["pass"] = False
        report["pages"].append({"page": pno+1, "text_text_collisions": collisions})
    doc.close()
    return report

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pad", type=float, default=0.4)
    ap.add_argument("--out")
    args = ap.parse_args()
    res = audit(Path(args.pdf), args.pad)
    txt = json.dumps(res, indent=2, ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt, encoding="utf-8")
