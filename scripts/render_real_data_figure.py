from __future__ import annotations
import argparse, json, hashlib, datetime
from pathlib import Path
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

from real_data_utils import load_table, apply_filters, sha256_file
from panel_renderers import RENDERERS

def render_direct_annotation_block(ax, panel, local_style):
    ann=(panel.get("annotation_intelligence") or {}).get("direct_annotations") or []
    texts=[str(x.get("text") or "").strip() for x in ann if str(x.get("text") or "").strip()]
    if not texts:
        return []
    fs=float(local_style.get("annotation_size_pt") or 6.0)
    # Put panel-level statistical summaries immediately above the data viewport,
    # right-aligned. This avoids obscuring observations; final collision QA remains mandatory.
    artist=ax.text(1.0,1.012,"\n".join(texts),transform=ax.transAxes,ha="right",va="bottom",
                   fontsize=fs,linespacing=1.15,clip_on=False)
    return [{"annotation_id":x.get("annotation_id"),"text":x.get("text")} for x in ann]

def build_annotation_legend_fragment(spec):
    lines=[]
    shared=(spec.get("annotation_intelligence") or {}).get("shared_legend_clauses") or []
    for x in shared:
        if str(x).strip(): lines.append(str(x).strip().rstrip(".")+".")
    for p in spec.get("panels",[]) or []:
        anns=(p.get("annotation_intelligence") or {}).get("legend_annotations") or []
        vals=[str(x.get("text") or "").strip() for x in anns if str(x.get("text") or "").strip()]
        if not vals: continue
        prefix=f"({p.get('panel_letter')}) " if p.get("panel_letter") else f"{p.get('panel_id')}: "
        lines.append(prefix+"; ".join(vals).rstrip(".")+".")
    return lines


def panel_source_data(df,mapping):
    cols=[]
    for v in (mapping or {}).values():
        if isinstance(v,str) and v in df.columns:
            cols.append(v)
        elif isinstance(v,list):
            cols.extend([x for x in v if isinstance(x,str) and x in df.columns])
    cols=list(dict.fromkeys(cols))
    return df[cols].copy() if cols else df.copy()

def render(spec_path: Path, output_dir: Path):
    spec=yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    figcfg=spec["figure"]
    style=spec.get("style",{})
    panels=spec.get("panels",[])
    output_dir.mkdir(parents=True,exist_ok=True)
    src_dir=output_dir/"SOURCE_DATA"
    src_dir.mkdir(exist_ok=True)

    width=float(figcfg["width_mm"])/25.4
    height=float(figcfg["height_mm"])/25.4
    plt.rcParams.update({
        "font.family":style.get("font_family","DejaVu Sans"),
        "font.size":float(figcfg.get("base_font_size_pt",6.5)),
        "pdf.fonttype":42,
        "ps.fonttype":42,
    })

    max_row=max(int((p.get("layout") or {}).get("row",0))+int((p.get("layout") or {}).get("rowspan",1)) for p in panels)
    max_col=max(int((p.get("layout") or {}).get("col",0))+int((p.get("layout") or {}).get("colspan",1)) for p in panels)

    fig=plt.figure(figsize=(width,height),facecolor=figcfg.get("background","white"))
    gs=fig.add_gridspec(max_row,max_col,left=.07,right=.98,top=.95,bottom=.09,wspace=.35,hspace=.45)

    provenance={
        "figure_id":figcfg["id"],
        "scientific_authority":figcfg.get("scientific_authority"),
        "manuscript_authority":figcfg.get("manuscript_authority"),
        "render_timestamp":datetime.datetime.now().isoformat(),
        "render_spec_sha256":hashlib.sha256(spec_path.read_bytes()).hexdigest(),
        "sources":[],
        "filters":[],
        "transformations":[],
        "panels":[],
        "annotation_intelligence":{"decision_binding":bool((spec.get("annotation_intelligence") or {}).get("decision_binding")),"rendered_direct":[],"legend_fragment":None},
        "outputs":{},
    }

    for p in panels:
        lay=p.get("layout") or {}
        row=int(lay.get("row",0)); col=int(lay.get("col",0))
        rs=int(lay.get("rowspan",1)); cs=int(lay.get("colspan",1))
        ax=fig.add_subplot(gs[row:row+rs,col:col+cs])

        panel_letter=p.get("panel_letter","")
        if panel_letter:
            ax.text(-.12,1.06,panel_letter,transform=ax.transAxes,ha="left",va="bottom",
                    fontsize=float(figcfg.get("panel_label_size_pt",8)),fontweight="bold")

        title=p.get("title") or ""
        if title:
            ax.set_title(title,loc="left",fontsize=float(figcfg.get("base_font_size_pt",6.5)),pad=4)

        chart=p["chart_type"]
        mapping=p.get("mapping") or {}
        src=p.get("source") or {}
        vh=p.get("visual_hierarchy") or {}
        local_style=dict(style)
        if vh:
            local_style["marker_size_pt"]=vh.get("marker_size_pt")
            local_style["line_width_pt"]=vh.get("line_width_pt")
            local_style["annotation_size_pt"]=vh.get("annotation_size_pt")
        df=pd.DataFrame()

        if chart!="workflow":
            path_value=src.get("path")
            if not path_value:
                raise ValueError(f"Panel {p['panel_id']} requires a source path.")
            sp=(spec_path.parent/path_value).resolve()
            if not sp.exists():
                raise FileNotFoundError(sp)
            df0=load_table(sp)
            df,flog=apply_filters(df0,p.get("filters") or [])
            provenance["sources"].append({
                "panel_id":p["panel_id"],
                "path":str(sp),
                "sha256":sha256_file(sp),
                "rows_before":int(len(df0)),
                "rows_after":int(len(df))
            })
            provenance["filters"].extend([{"panel_id":p["panel_id"],**x} for x in flog])

            # Required mapped columns
            required=[]
            for k,v in mapping.items():
                if isinstance(v,str) and k not in {"xlabel","ylabel","reference","matrix_transform","cmap"}:
                    if v in df.columns:
                        required.append(v)
            # Save panel source data
            psd=panel_source_data(df,mapping)
            src_path=src_dir/f"{figcfg['id']}_{p['panel_id']}_source_data.tsv"
            psd.to_csv(src_path,sep="\t",index=False)

        if chart not in RENDERERS:
            raise ValueError(f"Unsupported chart_type: {chart}")
        result=RENDERERS[chart](ax,df,mapping,local_style)
        rendered_ann=render_direct_annotation_block(ax,p,local_style)
        if rendered_ann:
            provenance["annotation_intelligence"]["rendered_direct"].append({"panel_id":p.get("panel_id"),"items":rendered_ann})

        if not p.get("legend",False):
            leg=ax.get_legend()
            if leg is not None:
                leg.remove()

        # Minimal clean style for quantitative axes.
        if chart not in {"workflow"}:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            tick_size=float(vh.get("tick_label_size_pt",float(figcfg.get("base_font_size_pt",6.5))-0.5))
            axis_size=float(vh.get("axis_label_size_pt",float(figcfg.get("base_font_size_pt",6.5))))
            line_w=float(vh.get("line_width_pt",0.8))
            ax.tick_params(labelsize=tick_size,width=max(0.45,line_w*0.8))
            ax.xaxis.label.set_size(axis_size)
            ax.yaxis.label.set_size(axis_size)
            ax.spines["left"].set_linewidth(line_w)
            ax.spines["bottom"].set_linewidth(line_w)

        provenance["panels"].append({
            "panel_id":p["panel_id"],
            "panel_letter":panel_letter,
            "chart_type":chart,
            "role":p.get("role"),
            "mapping":mapping
        })

    base=output_dir/figcfg["id"]
    pdf=base.with_suffix(".pdf")
    svg=base.with_suffix(".svg")
    png=output_dir/f"{figcfg['id']}_preview.png"
    tiff=base.with_suffix(".tiff")

    fig.savefig(pdf,facecolor=figcfg.get("background","white"))
    fig.savefig(svg,facecolor=figcfg.get("background","white"))
    fig.savefig(png,dpi=220,facecolor=figcfg.get("background","white"))
    fig.savefig(tiff,dpi=int(figcfg.get("tiff_dpi",600)),facecolor=figcfg.get("background","white"))
    plt.close(fig)

    legend_lines=build_annotation_legend_fragment(spec)
    if legend_lines:
        legend_path=output_dir/f"{figcfg['id']}_annotation_legend_fragment.txt"
        legend_path.write_text("\n".join(legend_lines)+"\n",encoding="utf-8")
        provenance["annotation_intelligence"]["legend_fragment"]=str(legend_path)

    provenance["outputs"]={
        "pdf":str(pdf),
        "svg":str(svg),
        "png_preview":str(png),
        "tiff":str(tiff),
    }
    (output_dir/"render_provenance.json").write_text(
        json.dumps(provenance,indent=2,ensure_ascii=False),encoding="utf-8"
    )
    return provenance

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("render_spec")
    ap.add_argument("--output-dir",required=True)
    args=ap.parse_args()
    render(Path(args.render_spec),Path(args.output_dir))
