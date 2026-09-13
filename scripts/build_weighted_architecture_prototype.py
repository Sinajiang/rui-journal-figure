from __future__ import annotations
import argparse, json, math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def draw_panel(fig, rect, label, meta):
    ax=fig.add_axes(rect)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_edgecolor('0.65'); s.set_linewidth(.8)
    ax.text(.03,.95,label,transform=ax.transAxes,ha='left',va='top',fontsize=7,fontweight='bold')
    ax.text(.03,.78,meta['panel_id'],transform=ax.transAxes,ha='left',va='top',fontsize=6)
    ax.text(.03,.58,f"{meta.get('role','')} | contribution {meta['contribution_score']:.1f}",transform=ax.transAxes,ha='left',va='top',fontsize=5.2,color='.25')
    ax.text(.03,.40,f"area {meta['normalized_area_share']:.2f} | density {meta['visual_density']:.1f}",transform=ax.transAxes,ha='left',va='top',fontsize=5.0,color='.35')
    ax.add_patch(Rectangle((.08,.08),.84,.20,facecolor='0.94',edgecolor='0.75',lw=.5))

def build(plan_json: Path, out_pdf: Path, out_png: Path|None=None, width_mm=180, height_mm=120):
    p=json.loads(plan_json.read_text(encoding='utf-8'))
    figs=p.get('figures',[]); n=len(figs); cols=2 if n>1 else 1; rows=math.ceil(n/cols)
    fig=plt.figure(figsize=(width_mm/25.4,height_mm/25.4),facecolor='white')
    fig.text(.5,.975,'WEIGHTED STRUCTURAL PROTOTYPE — NO DATA',ha='center',va='top',fontsize=8,fontweight='bold')
    left=.04; right=.98; top=.91; bottom=.06; gapx=.04; gapy=.08
    cellw=(right-left-gapx*(cols-1))/cols; cellh=(top-bottom-gapy*(rows-1))/rows
    for fi,fobj in enumerate(figs):
        r=fi//cols; c=fi%cols; x0=left+c*(cellw+gapx); y0=top-(r+1)*cellh-r*gapy
        fig.text(x0,y0+cellh+.01,f"Figure {fobj['figure']} | {fobj.get('layout_strategy','')}",fontsize=6.2,ha='left',va='bottom')
        ps=sorted(fobj['panels'],key=lambda x:x['normalized_area_share'],reverse=True)
        if len(ps)==1:
            draw_panel(fig,[x0,y0,cellw,cellh],'A',ps[0]); continue
        if fobj.get('layout_strategy')=='dominant_anchor':
            anchor=ps[0]; rest=ps[1:]; aw=cellw*.56
            draw_panel(fig,[x0,y0,aw,cellh],'A',anchor)
            rh=cellh/len(rest)
            for j,m in enumerate(rest):
                draw_panel(fig,[x0+aw+.012,y0+cellh-(j+1)*rh,cellw-aw-.012,rh-.008],chr(66+j),m)
        else:
            nr=2 if len(ps)>2 else 1; nc=math.ceil(len(ps)/nr)
            w=cellw/nc; h=cellh/nr
            for j,m in enumerate(ps):
                rr=j//nc; cc=j%nc
                draw_panel(fig,[x0+cc*w,y0+cellh-(rr+1)*h,w-.008,h-.008],chr(65+j),m)
    fig.savefig(out_pdf,facecolor='white')
    if out_png: fig.savefig(out_png,dpi=220,facecolor='white')
    plt.close(fig)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('visual_weight_plan'); ap.add_argument('--out-pdf',required=True); ap.add_argument('--out-png'); ap.add_argument('--width-mm',type=float,default=180); ap.add_argument('--height-mm',type=float,default=120)
    a=ap.parse_args(); build(Path(a.visual_weight_plan),Path(a.out_pdf),Path(a.out_png) if a.out_png else None,a.width_mm,a.height_mm)
