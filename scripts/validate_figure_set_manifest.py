from __future__ import annotations
import argparse, json
from pathlib import Path
from submission_compiler_utils import load_yaml, resolve

def validate(path: Path):
    m=load_yaml(path)
    base=path.parent
    blocking=[]; review=[]
    figs=m.get("figures",[]) or []

    nums=[int(f["number"]) for f in figs if "number" in f]
    if len(nums)!=len(set(nums)):
        blocking.append({"type":"duplicate_figure_number","numbers":nums})
    if nums:
        expected=list(range(1,max(nums)+1))
        if sorted(nums)!=expected:
            blocking.append({"type":"nonsequential_figure_numbers","observed":sorted(nums),"expected":expected})

    for f in figs:
        n=f.get("number")
        if not f.get("promoted"):
            blocking.append({"type":"unpromoted_figure","figure":n})

        for key in ["pdf","legend","provenance"]:
            rp=resolve(base,f.get(key))
            if not rp or not rp.exists():
                blocking.append({"type":"required_file_missing","figure":n,"field":key,"path":str(rp) if rp else None})

        # TIFF is expected for manuscript-level production package unless explicitly absent by policy.
        tp=resolve(base,f.get("tiff"))
        if not tp or not tp.exists():
            review.append({"type":"tiff_missing","figure":n,"path":str(tp) if tp else None})

        sd=resolve(base,f.get("source_data_dir"))
        if not sd or not sd.exists() or not any(x.is_file() for x in sd.rglob("*")):
            review.append({"type":"source_data_missing_or_empty","figure":n,"path":str(sd) if sd else None})

        sp=resolve(base,f.get("style_contract"))
        if not sp or not sp.exists():
            review.append({"type":"style_contract_missing","figure":n})

    return {
        "figure_count":len(figs),
        "blocking":blocking,
        "review":review,
        "pass":len(blocking)==0
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=validate(Path(args.manifest))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
