from __future__ import annotations
import argparse, json, re
from pathlib import Path

CANONICAL = [
    "abstract","introduction","methods","materials and methods","results",
    "discussion","conclusion","conclusions","references","figure legends"
]

def read_docx(path: Path):
    from docx import Document
    doc=Document(path)
    out=[]
    for p in doc.paragraphs:
        out.append({"text":p.text,"style":p.style.name if p.style else ""})
    return out

def read_text(path: Path):
    text=path.read_text(encoding="utf-8",errors="replace")
    return [{"text":x,"style":""} for x in text.splitlines()]

def normalize_heading(text):
    t=re.sub(r"^\s*\d+(?:\.\d+)*\s*[\.\-:]?\s*","",text.strip()).lower()
    return t

def extract(path: Path):
    rows=read_docx(path) if path.suffix.lower()==".docx" else read_text(path)
    sections={}
    current="preamble"
    sections[current]=[]
    for row in rows:
        txt=row["text"].strip()
        if not txt:
            continue
        norm=normalize_heading(txt)
        style=(row["style"] or "").lower()
        is_heading=("heading" in style) or (norm in CANONICAL)
        if is_heading and len(txt)<100:
            current=norm
            sections.setdefault(current,[])
        else:
            sections.setdefault(current,[]).append(txt)
    return {
        "file":str(path),
        "sections":{k:"\n".join(v) for k,v in sections.items()}
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manuscript")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=extract(Path(args.manuscript))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
