from __future__ import annotations
import argparse, json
from pathlib import Path

def decide(compilation_summary: Path, manual_contact_sheet_status: str,
           manuscript_reintegration_pass: bool, journal_upload_contract_pass: bool):
    s=json.loads(compilation_summary.read_text(encoding="utf-8"))
    manual=(manual_contact_sheet_status or "PENDING").upper()

    if s.get("blocking"):
        return {"decision":"BLOCKED","state":"FIGURE_PACKAGE_BLOCKED","reason":"Automated blocking defects remain."}
    if manual not in {"PASS","FAIL"}:
        return {"decision":"HOLD","state":"FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION","reason":"Manual contact-sheet review incomplete."}
    if manual=="FAIL":
        return {"decision":"REPAIR","state":"FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION","reason":"Cross-figure visual review failed."}
    if not manuscript_reintegration_pass:
        return {"decision":"REPAIR","state":"FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION","reason":"Manuscript/legend reintegration QA failed."}
    if not journal_upload_contract_pass:
        return {"decision":"REPAIR","state":"FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION","reason":"Journal upload contract is not closed."}
    return {
        "decision":"PROMOTE",
        "state":"FIGURE_PACKAGE_SUBMISSION_READY",
        "reason":"Automated figure-set QA, manual visual review, manuscript reintegration, and journal upload contract all pass."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("compilation_summary")
    ap.add_argument("--manual-contact-sheet-status",required=True)
    ap.add_argument("--manuscript-reintegration-pass",choices=["true","false"],required=True)
    ap.add_argument("--journal-upload-contract-pass",choices=["true","false"],required=True)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=decide(
        Path(args.compilation_summary),
        args.manual_contact_sheet_status,
        args.manuscript_reintegration_pass=="true",
        args.journal_upload_contract_pass=="true",
    )
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
