from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
import yaml

from validate_frozen_sentinels import validate as validate_sentinels
from render_real_data_figure import render

def produce(spec: Path, sentinel_contract: Path|None, output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True)

    sent=None
    if sentinel_contract:
        sent=validate_sentinels(sentinel_contract,sentinel_contract.parent)
        (output_dir/"sentinel_results.json").write_text(
            json.dumps(sent,indent=2,ensure_ascii=False),encoding="utf-8"
        )
        if not sent["pass"]:
            return {
                "status":"FAIL_SENTINEL",
                "sentinels":sent,
                "rendered":False
            }

    prov=render(spec,output_dir)
    pdf=Path(prov["outputs"]["pdf"])

    # Run terminal PDF QA using existing package script.
    qa_path=output_dir/"terminal_qa.json"
    cmd=[
        sys.executable,
        str(Path(__file__).resolve().parent/"terminal_qa.py"),
        str(pdf),
        "--out",str(qa_path)
    ]
    subprocess.run(cmd,check=False,capture_output=True,text=True)
    qa=json.loads(qa_path.read_text(encoding="utf-8")) if qa_path.exists() else None

    return {
        "status":"RENDERED_PRE_PROMOTION",
        "sentinels":sent,
        "provenance":prov,
        "terminal_qa":qa,
        "manual_visual_review_required":True
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("render_spec")
    ap.add_argument("--sentinels")
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=produce(
        Path(args.render_spec),
        Path(args.sentinels) if args.sentinels else None,
        Path(args.output_dir)
    )
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
    raise SystemExit(0 if res["status"]!="FAIL_SENTINEL" else 2)
