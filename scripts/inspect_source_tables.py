from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def inspect_one(path: Path):
    suf=path.suffix.lower()
    if suf in {".tsv",".txt"}:
        df=pd.read_csv(path,sep="\t")
    elif suf==".csv":
        df=pd.read_csv(path)
    elif suf in {".xlsx",".xlsm"}:
        df=pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported source table: {suf}")

    return {
        "path":str(path),
        "rows":int(df.shape[0]),
        "columns":int(df.shape[1]),
        "column_names":[str(x) for x in df.columns],
        "dtypes":{str(k):str(v) for k,v in df.dtypes.items()},
        "missing_by_column":{str(k):int(v) for k,v in df.isna().sum().items()},
        "numeric_columns":[str(x) for x in df.select_dtypes(include="number").columns],
        "categorical_candidate_columns":[
            str(c) for c in df.columns
            if df[c].nunique(dropna=True) <= 20 and not pd.api.types.is_numeric_dtype(df[c])
        ],
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("files",nargs="+")
    ap.add_argument("--out")
    args=ap.parse_args()
    res={"tables":[inspect_one(Path(x)) for x in args.files]}
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
