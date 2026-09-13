from pathlib import Path
import argparse
import fitz
from PIL import Image

def render(pdf, out_png, dpi=220):
    doc = fitz.open(pdf)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), alpha=False)
    pix.save(out_png)
    doc.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_png")
    ap.add_argument("--dpi", type=int, default=220)
    args = ap.parse_args()
    render(args.pdf, args.out_png, args.dpi)
