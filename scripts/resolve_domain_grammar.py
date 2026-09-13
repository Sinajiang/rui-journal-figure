from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def load_profile(profile_dir, did):
    p=Path(profile_dir)/f"{did}.yaml"
    if not p.exists():
        raise FileNotFoundError(p)
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def dedup(xs):
    out=[]; seen=set()
    for x in xs:
        key=json.dumps(x,sort_keys=True,ensure_ascii=False) if isinstance(x,(dict,list)) else str(x)
        if key not in seen:
            out.append(x); seen.add(key)
    return out

def resolve(selection_path: Path, profile_dir: Path):
    s=yaml.safe_load(selection_path.read_text(encoding="utf-8"))
    primary=s["primary_domain"]
    secondary=s.get("secondary_domains",[]) or []
    profs=[load_profile(profile_dir,primary)] + [load_profile(profile_dir,x) for x in secondary]
    return {
        "primary_domain":primary,
        "secondary_domains":secondary,
        "display_name":profs[0].get("display_name"),
        "core_questions":dedup([x for p in profs for x in p.get("core_questions",[])]),
        "main_figure_archetypes":dedup([x for p in profs for x in p.get("main_figure_archetypes",[])]),
        "preferred_chart_types":dedup([x for p in profs for x in p.get("preferred_chart_types",[])]),
        "supplementary_preferred":dedup([x for p in profs for x in p.get("supplementary_preferred",[])]),
        "risk_flags":dedup([x for p in profs for x in p.get("risk_flags",[])]),
        "benchmark_terms":dedup([x for p in profs for x in p.get("benchmark_terms",[])])
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("selection")
    ap.add_argument("--profile-dir",default=str(Path(__file__).resolve().parents[1]/"domain_profiles"))
    ap.add_argument("--out")
    args=ap.parse_args()
    res=resolve(Path(args.selection),Path(args.profile_dir))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
