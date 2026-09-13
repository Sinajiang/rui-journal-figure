from __future__ import annotations
import argparse, json, re
from pathlib import Path
import yaml

def load_text(path: Path):
    suf=path.suffix.lower()
    if suf==".json":
        obj=json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(obj,ensure_ascii=False)
    return path.read_text(encoding="utf-8",errors="replace")

def load_profiles(profile_dir: Path):
    out={}
    for p in profile_dir.glob("*.yaml"):
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        out[d["domain_id"]]=d
    return out

def infer(text_paths, profile_dir: Path):
    profiles=load_profiles(profile_dir)
    text="\n".join(load_text(Path(p)) for p in text_paths).lower()
    scored=[]
    for did,p in profiles.items():
        hits=[]
        score=0.0
        for kw in p.get("keywords",[]):
            k=str(kw).lower()
            count=text.count(k)
            if count:
                hits.append({"keyword":kw,"count":count})
                score += min(3,count)
        scored.append({
            "domain_id":did,
            "display_name":p.get("display_name"),
            "score":round(score,3),
            "hits":hits
        })
    scored.sort(key=lambda x:x["score"],reverse=True)
    top=scored[0] if scored else None
    second=scored[1] if len(scored)>1 else None
    margin=(top["score"]-second["score"]) if top and second else (top["score"] if top else 0)
    confidence="high" if top and top["score"]>=6 and margin>=3 else "medium" if top and top["score"]>=3 and margin>=1 else "low"
    return {
        "ranked_domains":scored,
        "suggested_primary_domain":top["domain_id"] if top and top["score"]>0 else None,
        "confidence":confidence,
        "manual_confirmation_required":confidence!="high"
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("inputs",nargs="+")
    ap.add_argument("--profile-dir",default=str(Path(__file__).resolve().parents[1]/"domain_profiles"))
    ap.add_argument("--out")
    args=ap.parse_args()
    res=infer(args.inputs,Path(args.profile_dir))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
