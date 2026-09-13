from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import hashlib, json

def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def load_table(path: Path):
    suf=path.suffix.lower()
    if suf in {".tsv",".txt"}:
        return pd.read_csv(path,sep="\t")
    if suf==".csv":
        return pd.read_csv(path)
    if suf in {".xlsx",".xlsm"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported table format: {suf}")

def apply_filters(df, filters):
    out=df.copy()
    log=[]
    for f in filters or []:
        col=f["column"]; op=f["op"]; val=f.get("value")
        if col not in out.columns:
            raise KeyError(f"Filter column missing: {col}")
        before=len(out)
        if op=="==":
            out=out[out[col]==val]
        elif op=="!=":
            out=out[out[col]!=val]
        elif op=="in":
            out=out[out[col].isin(val)]
        elif op=="notin":
            out=out[~out[col].isin(val)]
        elif op==">":
            out=out[out[col]>val]
        elif op==">=":
            out=out[out[col]>=val]
        elif op=="<":
            out=out[out[col]<val]
        elif op=="<=":
            out=out[out[col]<=val]
        elif op=="notna":
            out=out[out[col].notna()]
        elif op=="isna":
            out=out[out[col].isna()]
        else:
            raise ValueError(f"Unsupported filter op: {op}")
        log.append({"column":col,"op":op,"value":val,"rows_before":before,"rows_after":len(out)})
    return out.copy(),log

def transform_series(s, kind):
    kind=(kind or "none").lower()
    if kind=="none":
        return s
    if kind=="log10":
        return np.log10(s.astype(float))
    if kind=="log2":
        return np.log2(s.astype(float))
    if kind=="percent":
        return s.astype(float)*100.0
    if kind=="neglog10":
        return -np.log10(s.astype(float))
    raise ValueError(f"Unsupported scalar transform: {kind}")

def zscore_matrix(mat, axis):
    arr=np.asarray(mat,dtype=float)
    if axis=="row":
        m=np.nanmean(arr,axis=1,keepdims=True)
        sd=np.nanstd(arr,axis=1,ddof=0,keepdims=True)
    elif axis=="column":
        m=np.nanmean(arr,axis=0,keepdims=True)
        sd=np.nanstd(arr,axis=0,ddof=0,keepdims=True)
    else:
        raise ValueError("axis must be row or column")
    sd=np.where(sd==0,1,sd)
    return (arr-m)/sd
