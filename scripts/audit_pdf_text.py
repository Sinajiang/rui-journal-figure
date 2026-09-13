from pathlib import Path
import argparse, json
import fitz

def audit(pdf_path: Path, min_pt: float = 5.5):
    doc = fitz.open(pdf_path)
    out = {"file": str(pdf_path), "pages": [], "min_text_pt": None, "below_min": []}
    mins = []
    for pno, page in enumerate(doc):
        page_min = None
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for sp in ln.get("spans", []):
                    t = sp["text"].strip()
                    if not t:
                        continue
                    s = float(sp["size"])
                    mins.append(s)
                    page_min = s if page_min is None else min(page_min, s)
                    if s < min_pt:
                        out["below_min"].append({"page": pno+1, "text": t, "size_pt": s, "bbox": sp["bbox"]})
        out["pages"].append({"page": pno+1, "min_text_pt": page_min})
    doc.close()
    out["min_text_pt"] = min(mins) if mins else None
    out["pass"] = len(out["below_min"]) == 0
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--min-pt", type=float, default=5.5)
    ap.add_argument("--out")
    args = ap.parse_args()
    res = audit(Path(args.pdf), args.min_pt)
    text = json.dumps(res, indent=2, ensure_ascii=False)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
