from __future__ import annotations
import argparse,json,math
from pathlib import Path
import yaml

PT_TO_MM=25.4/72.0

def contract(path:Path|None):
    if path:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    p=Path(__file__).resolve().parents[1]/"templates"/"visual_hierarchy_contract.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def tier(panel):
    cls=(panel.get("visual_weight_class") or "").upper()
    role=(panel.get("role") or "").lower()
    score=float(panel.get("contribution_score",0))
    if cls in {"ANCHOR","MAJOR_SUPPORT","SUPPORT","CONTEXT","PROVENANCE"}:
        return cls
    if role in {"workflow","provenance","design"}:
        return "PROVENANCE"
    if score>=8.5:return "ANCHOR"
    if score>=7.0:return "MAJOR_SUPPORT"
    if score>=5.5:return "SUPPORT"
    return "CONTEXT"

def clamp(x,a,b): return max(a,min(b,x))

def derive(layouts_path:Path,contract_path:Path|None=None):
    layouts=json.loads(layouts_path.read_text(encoding="utf-8"))
    c=contract(contract_path); glob=c["global"]; bud=c["budget"]; tiers=c["tiers"]
    fw=float(layouts.get("figure_width_mm",180)); fh=float(layouts.get("figure_height_mm",120))
    minfont=float(glob["operational_min_font_pt"])
    result={
        "figure_width_mm":fw,"figure_height_mm":fh,
        "font_family":glob["font_family"],
        "panel_label_size_pt":float(glob["panel_label_size_pt"]),
        "operational_min_font_pt":minfont,
        "figures":[],
        "review_flags":[]
    }

    for fig in layouts.get("figures",[]):
        fitem={"figure":fig.get("figure"),"figure_id":fig.get("figure_id"),"topology":fig.get("topology"),
               "legend_strategy":fig.get("legend_strategy"),"panels":[]}
        for p in fig.get("panels",[]):
            r=p["rect"]; pw=fw*float(r[2]); ph=fh*float(r[3])
            t=tier(p); tc=tiers[t]

            axis=clamp(float(glob["base_axis_label_size_pt"])+float(tc["axis_delta_pt"]),minfont,9)
            tick=clamp(float(glob["base_tick_label_size_pt"])+float(tc["tick_delta_pt"]),minfont,8)
            ann=clamp(float(glob["base_annotation_size_pt"])+float(tc["annotation_delta_pt"]),minfont,8)
            marker=float(glob["base_marker_size_pt"])*float(tc["marker_scale"])
            line=float(glob["base_line_width_pt"])*float(tc["line_scale"])

            glyph_mm=float(bud["avg_glyph_width_factor"])*ann*PT_TO_MM
            chars=max(8,int((pw*0.88)/max(glyph_mm,0.1)))

            line_h=ann*PT_TO_MM*float(bud["line_height_factor"])
            ann_h=ph*float(bud["annotation_height_fraction"])
            max_lines=max(1,min(int(bud["max_annotation_lines_cap"]),int(ann_h/max(line_h,0.1))))
            max_chars=chars*max_lines

            x_spacing=tick*PT_TO_MM*float(bud["horizontal_tick_spacing_em"])
            y_spacing=tick*PT_TO_MM*float(bud["vertical_tick_spacing_em"])
            max_x=max(2,int((pw*0.92)/max(x_spacing,0.1)))
            max_y=max(2,int((ph*0.84)/max(y_spacing,0.1)))

            legend_line=tick*PT_TO_MM*float(bud["line_height_factor"])
            leg_h=ph*float(bud["legend_height_fraction"])
            max_leg=max(2,min(int(bud["max_legend_items_cap"]),int(leg_h/max(legend_line,0.1))))

            direct=(fig.get("legend_strategy")=="direct_labels_only" and max_leg<=6) or (
                fig.get("legend_strategy") in {"none","embedded"} and t in {"ANCHOR","MAJOR_SUPPORT"} and max_leg<=6
            )

            item={
                "panel_id":p["panel_id"],
                "role":p.get("role"),
                "tier":t,
                "contribution_score":float(p.get("contribution_score",0)),
                "visual_density":float(p.get("visual_density",0)),
                "rect":r,
                "panel_width_mm":round(pw,3),
                "panel_height_mm":round(ph,3),
                "axis_label_size_pt":round(axis,2),
                "tick_label_size_pt":round(tick,2),
                "annotation_size_pt":round(ann,2),
                "marker_size_pt":round(marker,2),
                "line_width_pt":round(line,2),
                "annotation_priority":int(tc["annotation_priority"]),
                "max_chars_per_annotation_line":chars,
                "max_annotation_lines":max_lines,
                "max_annotation_chars":max_chars,
                "max_x_tick_labels":max_x,
                "max_y_tick_labels":max_y,
                "max_legend_items":max_leg,
                "legend_strategy":fig.get("legend_strategy") or "none",
                "direct_labels_preferred":bool(direct),
            }
            fitem["panels"].append(item)

            if min(axis,tick,ann)<minfont-1e-9:
                result["review_flags"].append({"type":"FONT_BELOW_OPERATIONAL_FLOOR","panel_id":p["panel_id"]})
            if pw<35 and float(p.get("visual_density",0))>=7:
                result["review_flags"].append({"type":"DENSE_NARROW_PANEL","panel_id":p["panel_id"],"width_mm":round(pw,2)})

        result["figures"].append(fitem)
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("solved_layouts")
    ap.add_argument("--contract")
    ap.add_argument("--out")
    a=ap.parse_args()
    res=derive(Path(a.solved_layouts),Path(a.contract) if a.contract else None)
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
