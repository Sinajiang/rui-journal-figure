from pathlib import Path
import argparse, json
from audit_pdf_text import audit as audit_text
from audit_figure_collisions import audit as audit_collisions

def validate(pdf, min_pt=5.5):
    text = audit_text(Path(pdf), min_pt)
    collision = audit_collisions(Path(pdf))
    return {
        "file": str(pdf),
        "text_audit": text,
        "collision_audit": collision,
        "pass": bool(text["pass"] and collision["pass"]),
        "note": "Automated PASS does not replace final-size manual visual review."
    }

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--min-pt",type=float,default=5.5)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=validate(args.pdf,args.min_pt)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
