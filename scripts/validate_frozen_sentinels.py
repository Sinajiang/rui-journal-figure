from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml
from real_data_utils import load_table

def subset(df, where):
    out=df
    for col,val in (where or {}).items():
        if col not in out.columns:
            raise KeyError(f"Sentinel where column missing: {col}")
        out=out[out[col]==val]
    return out

def validate_one(s, base_dir: Path):
    path=(base_dir/s["source_path"]).resolve()
    if not path.exists():
        return {
            "id":s["id"],
            "kind":s.get("kind"),
            "pass":False,
            "reason":"source_missing",
            "path":str(path)
        }

    df=load_table(path)
    kind=s["kind"]
    expected=s.get("expected")
    result={
        "id":s["id"],
        "kind":kind,
        "source_path":str(path),
        "pass":False
    }

    if kind=="row_count":
        observed=int(len(df))
        result["observed"]=observed
        result["expected"]=int(expected)
        result["pass"]=(observed==int(expected))

    elif kind=="exact_value":
        sub=subset(df,s.get("where"))
        col=s["column"]
        if col not in sub.columns or len(sub)!=1:
            result["reason"]="exact_value_not_unique"
            result["rows"]=int(len(sub))
            return result
        observed=float(sub.iloc[0][col])
        exp=float(expected)
        tol=float(s.get("tolerance",0))
        result["observed"]=observed
        result["expected"]=exp
        result["tolerance"]=tol
        result["pass"]=abs(observed-exp)<=tol

    elif kind=="category_set":
        col=s["column"]
        if col not in df.columns:
            result["reason"]="column_missing"
            result["column"]=col
            return result
        observed=sorted(str(x) for x in df[col].dropna().unique())
        exp=sorted(str(x) for x in expected)
        result["observed"]=observed
        result["expected"]=exp
        result["pass"]=(observed==exp)

    elif kind=="value_count":
        sub=subset(df,s.get("where"))
        observed=int(len(sub))
        result["observed"]=observed
        result["expected"]=int(expected)
        result["pass"]=(observed==int(expected))

    else:
        result["reason"]=f"unsupported_kind:{kind}"

    return result

def validate(contract: Path, base_dir: Path|None=None):
    c=yaml.safe_load(contract.read_text(encoding="utf-8"))
    base=base_dir or contract.parent
    results=[validate_one(s,base) for s in c.get("sentinels",[])]
    return {
        "results":results,
        "pass":all(x.get("pass") for x in results)
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("contract")
    ap.add_argument("--base-dir")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=validate(
        Path(args.contract),
        Path(args.base_dir) if args.base_dir else None
    )
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
    raise SystemExit(0 if res["pass"] else 2)
