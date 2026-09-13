from __future__ import annotations
import argparse, json, math
from pathlib import Path
import yaml
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D

def choose_grid(n):
    if n <= 1:
        return 1,1
    if n == 2:
        return 1,2
    if n <= 4:
        return 2,2
    if n <= 6:
        return 2,3
    return 3,3

def glyph(ax, chart_type):
    """Non-quantitative chart-type icon only."""
    ct=(chart_type or "").lower()
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    if "heat" in ct or "matrix" in ct:
        for i in range(4):
            for j in range(5):
                shade=0.82 if (i+j)%2==0 else 0.93
                ax.add_patch(Rectangle((0.12+j*0.13,0.17+i*0.13),0.11,0.11,
                                       facecolor=str(shade),edgecolor="0.75",lw=.3))
    elif "forest" in ct or "effect" in ct or "interval" in ct:
        ys=[.25,.45,.65]
        for k,y in enumerate(ys):
            x=.35+.12*k
            ax.hlines(y,x-.16,x+.16,color="0.45",lw=1.0)
            ax.plot(x,y,"o",ms=4,color="0.25")
        ax.axvline(.5,color="0.75",lw=.7,ls="--")
    elif "lollipop" in ct:
        xs=[.2,.35,.5,.65,.8]
        hs=[.35,.55,.42,.70,.50]
        for x,h in zip(xs,hs):
            ax.vlines(x,.18,h,color="0.5",lw=.9)
            ax.plot(x,h,"o",ms=3.8,color="0.3")
    elif "dot" in ct or "box" in ct or "violin" in ct:
        for i,x in enumerate([.35,.65]):
            ax.add_patch(Rectangle((x-.10,.35),.20,.22,facecolor="0.92",edgecolor="0.5",lw=.7))
            for j in range(5):
                ax.plot(x+(.02*(j-2)),.28+.09*j,"o",ms=3,color="0.35")
    elif "schematic" in ct or "workflow" in ct:
        for x in [.18,.48,.78]:
            ax.add_patch(FancyBboxPatch((x-.10,.40),.20,.18,
                                        boxstyle="round,pad=.01,rounding_size=.02",
                                        facecolor="0.94",edgecolor="0.6",lw=.7))
        ax.annotate("",xy=(.38,.49),xytext=(.28,.49),arrowprops=dict(arrowstyle="->",lw=.7,color=".4"))
        ax.annotate("",xy=(.68,.49),xytext=(.58,.49),arrowprops=dict(arrowstyle="->",lw=.7,color=".4"))
    elif "network" in ct:
        pts=[(.3,.55),(.5,.7),(.7,.55),(.5,.3)]
        for a,b in [(0,1),(1,2),(2,3),(3,0),(0,2)]:
            ax.plot([pts[a][0],pts[b][0]],[pts[a][1],pts[b][1]],color=".65",lw=.7)
        for x,y in pts:
            ax.plot(x,y,"o",ms=6,color=".4")
    else:
        ax.add_patch(Rectangle((.18,.25),.64,.48,facecolor="0.95",edgecolor="0.65",lw=.7))

def build(candidate_json: Path, panel_inventory_tsv: Path, out_pdf: Path, out_png: Path|None=None,
          width_mm=180, height_mm=120):
    cand=json.loads(candidate_json.read_text(encoding="utf-8"))

    import csv
    rows=list(csv.DictReader(panel_inventory_tsv.open(encoding="utf-8"),delimiter="\t"))
    pmap={r["panel_id"]:r for r in rows}

    figs=cand.get("figures",[])
    nfig=len(figs)
    cols=2 if nfig>1 else 1
    rows_n=math.ceil(nfig/cols)

    fig=plt.figure(figsize=(width_mm/25.4,height_mm/25.4),facecolor="white")
    gs=fig.add_gridspec(rows_n,cols,left=.04,right=.98,top=.90,bottom=.08,wspace=.10,hspace=.18)

    fig.text(.5,.965,"STRUCTURAL PROTOTYPE — NO DATA",ha="center",va="top",
             fontsize=9,fontweight="bold")

    for fi,fobj in enumerate(figs):
        r=fi//cols; c=fi%cols
        outer=fig.add_subplot(gs[r,c])
        outer.set_xticks([]); outer.set_yticks([])
        for s in outer.spines.values():
            s.set_edgecolor("0.75"); s.set_linewidth(.8)
        outer.set_title(
            f"Figure {fobj.get('figure')} | {fobj.get('theme','')} | density={fobj.get('total_visual_density','')}",
            loc="left",fontsize=6.5,pad=4
        )

        panels=fobj.get("panels",[])
        nr,nc=choose_grid(len(panels))
        bbox=outer.get_position()
        pad_x=.012; pad_y=.020
        usable_w=bbox.width-2*pad_x
        usable_h=bbox.height-2*pad_y
        cell_w=usable_w/nc
        cell_h=usable_h/nr

        for pi,pid in enumerate(panels):
            pr=pi//nc; pc=pi%nc
            x=bbox.x0+pad_x+pc*cell_w
            y=bbox.y1-pad_y-(pr+1)*cell_h
            ax=fig.add_axes([x+.01*cell_w,y+.10*cell_h,.90*cell_w,.68*cell_h])
            glyph(ax,pmap.get(pid,{}).get("chart_type",""))
            meta=pmap.get(pid,{})
            role=meta.get("role","")
            claims=meta.get("claim_ids","")
            density=meta.get("visual_density","")
            fig.text(x+.015*cell_w,y+.86*cell_h,
                     f"{chr(65+pi)}  {pid} · {role}",
                     fontsize=5.8,fontweight="bold",ha="left",va="top")
            fig.text(x+.015*cell_w,y+.76*cell_h,
                     f"{meta.get('chart_type','')} | claims {claims} | density {density}",
                     fontsize=4.8,ha="left",va="top",color=".35")

    fig.savefig(out_pdf,facecolor="white")
    if out_png:
        fig.savefig(out_png,dpi=220,facecolor="white")
    plt.close(fig)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("panel_inventory_tsv")
    ap.add_argument("--out-pdf",required=True)
    ap.add_argument("--out-png")
    ap.add_argument("--width-mm",type=float,default=180)
    ap.add_argument("--height-mm",type=float,default=120)
    args=ap.parse_args()
    build(
        Path(args.candidate_json),
        Path(args.panel_inventory_tsv),
        Path(args.out_pdf),
        Path(args.out_png) if args.out_png else None,
        args.width_mm,args.height_mm
    )
