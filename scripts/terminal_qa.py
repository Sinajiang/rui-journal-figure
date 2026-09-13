from __future__ import annotations
import argparse, json
from pathlib import Path
from audit_pdf_text import audit as audit_text
from audit_pdf_geometry import audit as audit_geometry

try:
    from audit_layout_contract import audit as audit_contract
except Exception:
    audit_contract=None

def run(pdf: Path, min_pt=5.5, contract: Path|None=None):
    text=audit_text(pdf,min_pt)
    geom=audit_geometry(pdf)
    contract_res=None
    if contract and audit_contract:
        contract_res=audit_contract(pdf,contract)

    hard_pass = text["pass"] and geom["blocking_pass"]
    if contract_res is not None:
        hard_pass = hard_pass and contract_res["pass"]

    return {
        "file":str(pdf),
        "production_text":text,
        "rendered_geometry":geom,
        "layout_contract":contract_res,
        "automated_hard_pass":bool(hard_pass),
        "manual_visual_review_required":True,
        "promotion_rule":"Promote only if automated_hard_pass == true AND final-size manual visual review == PASS."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--min-pt",type=float,default=5.5)
    ap.add_argument("--contract")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=run(Path(args.pdf),args.min_pt,Path(args.contract) if args.contract else None)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
