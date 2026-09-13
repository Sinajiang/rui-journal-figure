from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from real_data_utils import zscore_matrix

def _color(style,key,default="0.35"):
    return (style.get("semantic_colors") or {}).get(key,default)

def _metric(style,key,default):
    v=style.get(key)
    try:
        return float(v) if v is not None else float(default)
    except:
        return float(default)

def _marker_area(style,default_pt=4.0):
    return _metric(style,"marker_size_pt",default_pt)**2

def dot_box(ax,df,mapping,style):
    xcol=mapping["group"]; ycol=mapping["value"]
    groups=mapping.get("order") or list(dict.fromkeys(df[xcol].astype(str)))
    lw=_metric(style,"line_width_pt",.8); ms=_marker_area(style,4.0)
    for i,g in enumerate(groups):
        vals=df.loc[df[xcol].astype(str)==str(g),ycol].astype(float).dropna().values
        if len(vals)==0: continue
        jitter=np.linspace(-0.08,0.08,len(vals)) if len(vals)>1 else np.array([0])
        ax.scatter(np.full(len(vals),i)+jitter,vals,s=ms,facecolors="white",edgecolors="0.25",linewidth=max(.45,lw*.85),zorder=3)
        q1,med,q3=np.percentile(vals,[25,50,75])
        ax.add_patch(plt.Rectangle((i-.18,q1),.36,max(q3-q1,1e-12),facecolor="0.93",edgecolor="0.35",lw=lw,zorder=1))
        ax.hlines(med,i-.18,i+.18,color="0.2",lw=max(.7,lw*1.2),zorder=2)
    ax.set_xticks(range(len(groups)),groups); ax.set_ylabel(mapping.get("ylabel",ycol))

def paired_dot(ax,df,mapping,style):
    idc=mapping["id"]; xc=mapping["condition"]; yc=mapping["value"]
    order=mapping.get("order") or list(dict.fromkeys(df[xc].astype(str)))
    wide=df.pivot(index=idc,columns=xc,values=yc)
    lw=_metric(style,"line_width_pt",.8); ms=_marker_area(style,3.8)
    for _,row in wide.iterrows():
        ys=[row.get(o,np.nan) for o in order]
        if sum(pd.notna(ys))>=2:
            ax.plot(range(len(order)),ys,color="0.75",lw=max(.5,lw*.85),zorder=1)
            ax.scatter(range(len(order)),ys,s=ms,color="0.35",zorder=2)
    ax.set_xticks(range(len(order)),order); ax.set_ylabel(mapping.get("ylabel",yc))

def effect_plot(ax,df,mapping,style):
    lab=mapping["label"]; est=mapping["estimate"]; lo=mapping.get("lower"); hi=mapping.get("upper")
    d=df.copy(); order=mapping.get("order")
    if order:
        d["_ord"]=pd.Categorical(d[lab].astype(str),categories=order,ordered=True); d=d.sort_values("_ord")
    y=np.arange(len(d)); x=d[est].astype(float).values
    lw=_metric(style,"line_width_pt",.8); mpt=_metric(style,"marker_size_pt",4.0)
    if lo and hi:
        xerr=np.vstack([x-d[lo].astype(float).values,d[hi].astype(float).values-x])
        ax.errorbar(x,y,xerr=xerr,fmt="o",color="0.25",ecolor="0.55",elinewidth=lw,capsize=2,ms=mpt)
    else:
        ax.scatter(x,y,s=mpt**2,color="0.25")
    ax.axvline(float(mapping.get("reference",0)),color="0.75",lw=max(.55,lw*.85),ls="--")
    ax.set_yticks(y,d[lab].astype(str)); ax.invert_yaxis(); ax.set_xlabel(mapping.get("xlabel",est))

def lollipop(ax,df,mapping,style):
    lab=mapping["label"]; val=mapping["value"]; d=df.copy(); y=np.arange(len(d)); x=d[val].astype(float).values
    ref=float(mapping.get("reference",0)); lw=_metric(style,"line_width_pt",.8); mpt=_metric(style,"marker_size_pt",4.0)
    ax.hlines(y,ref,x,color="0.6",lw=lw); ax.scatter(x,y,s=mpt**2,color="0.3",zorder=3)
    ax.axvline(ref,color="0.8",lw=max(.5,lw*.8)); ax.set_yticks(y,d[lab].astype(str)); ax.invert_yaxis(); ax.set_xlabel(mapping.get("xlabel",val))

def scatter(ax,df,mapping,style):
    x=mapping["x"]; y=mapping["y"]; lw=_metric(style,"line_width_pt",.8); mpt=_metric(style,"marker_size_pt",4.0)
    ax.scatter(df[x].astype(float),df[y].astype(float),s=mpt**2,facecolors="white",edgecolors="0.3",linewidth=max(.45,lw*.8))
    if mapping.get("identity_line"):
        mn=min(df[x].min(),df[y].min()); mx=max(df[x].max(),df[y].max())
        ax.plot([mn,mx],[mn,mx],ls="--",lw=lw,color="0.7")
    ax.set_xlabel(mapping.get("xlabel",x)); ax.set_ylabel(mapping.get("ylabel",y))

def grouped_bar(ax,df,mapping,style):
    cat=mapping["category"]; val=mapping["value"]; grp=mapping.get("group")
    if grp:
        pv=df.pivot(index=cat,columns=grp,values=val); pv.plot(kind="bar",ax=ax,legend=True); ax.set_xlabel("")
    else:
        ax.bar(df[cat].astype(str),df[val].astype(float),color="0.55")
    ax.set_ylabel(mapping.get("ylabel",val))

def heatmap(ax,df,mapping,style):
    row=mapping["row"]; col=mapping["column"]; val=mapping["value"]; pv=df.pivot(index=row,columns=col,values=val)
    arr=pv.values.astype(float); tr=(mapping.get("matrix_transform") or "none").lower()
    if tr=="zscore_by_row": arr=zscore_matrix(arr,"row")
    elif tr=="zscore_by_column": arr=zscore_matrix(arr,"column")
    im=ax.imshow(arr,aspect="auto",interpolation="nearest",cmap=mapping.get("cmap","coolwarm"))
    ax.set_yticks(np.arange(len(pv.index)),pv.index.astype(str)); ax.set_xticks(np.arange(len(pv.columns)),pv.columns.astype(str),rotation=45,ha="right")
    return im

def evidence_matrix(ax,df,mapping,style):
    row=mapping["row"]; col=mapping["column"]; status=mapping["status"]
    rows=list(dict.fromkeys(df[row].astype(str))); cols=list(dict.fromkeys(df[col].astype(str)))
    pos={(str(r[row]),str(r[col])):str(r[status]) for _,r in df.iterrows()}
    base=_metric(style,"marker_size_pt",4.0); size=(base*1.45)**2
    for i,rr in enumerate(rows):
        for j,cc in enumerate(cols):
            st=pos.get((rr,cc),"missing")
            if st=="gene": ax.scatter(j,i,marker="^",s=size,color=_color(style,"positive","#4C78A8"))
            elif st=="composite": ax.scatter(j,i,marker="D",s=size*.82,color=_color(style,"context","#59A14F"))
            elif st=="opposite": ax.scatter(j,i,marker="X",s=size*.9,color="#7A5195")
            else: ax.scatter(j,i,marker="x",s=size*.85,color=_color(style,"missing","#C44E52"))
    ax.set_xticks(range(len(cols)),cols,rotation=45,ha="right"); ax.set_yticks(range(len(rows)),rows); ax.invert_yaxis()
    ax.set_xlim(-.6,len(cols)-.4); ax.set_ylim(len(rows)-.4,-.6)

def workflow(ax,df,mapping,style):
    labels=mapping.get("labels") or ["Input","Analysis","Output"]; n=len(labels); xs=np.linspace(.15,.85,n)
    lw=_metric(style,"line_width_pt",.8); fs=_metric(style,"annotation_size_pt",6.0)
    for i,(x,label) in enumerate(zip(xs,labels)):
        ax.add_patch(FancyBboxPatch((x-.10,.40),.20,.18,boxstyle="round,pad=.02,rounding_size=.02",facecolor="0.95",edgecolor="0.6",lw=lw))
        ax.text(x,.49,label,ha="center",va="center",fontsize=fs)
        if i<n-1:
            ax.annotate("",xy=(xs[i+1]-.11,.49),xytext=(x+.11,.49),arrowprops=dict(arrowstyle="->",lw=lw,color=".45"))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")

RENDERERS={
    "dot_box":dot_box,"paired_dot":paired_dot,"effect_plot":effect_plot,"lollipop":lollipop,
    "scatter":scatter,"grouped_bar":grouped_bar,"heatmap":heatmap,"evidence_matrix":evidence_matrix,"workflow":workflow,
}
