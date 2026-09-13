from __future__ import annotations
import argparse, json
from pathlib import Path
import fitz
from PIL import Image

def pdf_metadata(path: Path):
    doc=fitz.open(path)
    page=doc[0]
    sizes=[]
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines",[]):
            for sp in ln.get("spans",[]):
                if sp["text"].strip():
                    sizes.append(float(sp["size"]))
    out={
        "file":str(path),
        "format":"pdf",
        "width_mm":page.rect.width*25.4/72,
        "height_mm":page.rect.height*25.4/72,
        "min_text_pt":min(sizes) if sizes else None,
        "max_text_pt":max(sizes) if sizes else None,
        "is_vector_container":True,
    }
    doc.close()
    return out

def image_metadata(path: Path):
    im=Image.open(path)
    dpi=im.info.get("dpi",(None,None))
    return {
        "file":str(path),
        "format":path.suffix.lower().lstrip("."),
        "width_px":im.width,
        "height_px":im.height,
        "mode":im.mode,
        "dpi_x":float(dpi[0]) if dpi and dpi[0] else None,
        "dpi_y":float(dpi[1]) if dpi and dpi[1] else None,
    }

def extract(path: Path):
    if path.suffix.lower()==".pdf":
        return pdf_metadata(path)
    return image_metadata(path)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=extract(Path(args.file))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
