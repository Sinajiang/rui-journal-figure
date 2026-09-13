from __future__ import annotations
import argparse
from pathlib import Path
import yaml

def make(profile_path: Path, stage: str, out: Path):
    p=yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if stage not in p["stages"]:
        raise ValueError(f"Unknown stage {stage}")
    payload={
        "journal":p["journal"],
        "publisher":p.get("publisher"),
        "profile_retrieved":p.get("retrieved"),
        "official_sources":p.get("official_sources",[]),
        "stage":stage,
        "constraints":p["stages"][stage],
        "status":"EXTERNAL-CONTRACT / VERIFY IF SUBMISSION DATE CHANGES"
    }
    out.write_text(yaml.safe_dump(payload,sort_keys=False,allow_unicode=True),encoding="utf-8")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("--stage",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    make(Path(args.profile),args.stage,Path(args.out))
