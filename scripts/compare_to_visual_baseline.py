from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def compare(baseline_path: Path, candidate_visual_json: Path, candidate_architecture_score: float):
    b=yaml.safe_load(baseline_path.read_text(encoding="utf-8"))
    v=json.loads(candidate_visual_json.read_text(encoding="utf-8"))
    metrics=v.get("metrics",v)
    visual=float(metrics["overall_visual_score"])
    base_visual=b.get("visual_score")
    base_arch=b.get("architecture_score")

    visual_delta=None if base_visual is None else visual-float(base_visual)
    arch_delta=None if base_arch is None else float(candidate_architecture_score)-float(base_arch)

    return {
        "baseline_id":b.get("baseline_id"),
        "baseline_visual_score":base_visual,
        "candidate_visual_score":visual,
        "visual_delta":round(visual_delta,3) if visual_delta is not None else None,
        "baseline_architecture_score":base_arch,
        "candidate_architecture_score":float(candidate_architecture_score),
        "architecture_delta":round(arch_delta,3) if arch_delta is not None else None,
        "visual_regression":bool(visual_delta is not None and visual_delta < -0.6),
        "architecture_regression":bool(arch_delta is not None and arch_delta < -0.5),
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("baseline_yaml")
    ap.add_argument("candidate_visual_json")
    ap.add_argument("--architecture-score",type=float,required=True)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=compare(Path(args.baseline_yaml),Path(args.candidate_visual_json),args.architecture_score)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
