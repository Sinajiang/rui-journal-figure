from __future__ import annotations
import argparse,json,yaml
from pathlib import Path

def apply(render_spec:Path,hierarchy_json:Path,out:Path):
    spec=yaml.safe_load(render_spec.read_text(encoding="utf-8"))
    h=json.loads(hierarchy_json.read_text(encoding="utf-8"))
    fid=spec["figure"]["id"]
    fig=next((x for x in h.get("figures",[]) if x.get("figure_id")==fid),None)
    if fig is None:
        raise KeyError(f"Figure not found in hierarchy: {fid}")
    pmap={p["panel_id"]:p for p in fig["panels"]}
    spec.setdefault("style",{})["font_family"]=h.get("font_family",spec.get("style",{}).get("font_family","DejaVu Sans"))
    spec["figure"]["panel_label_size_pt"]=h.get("panel_label_size_pt",spec["figure"].get("panel_label_size_pt",8))
    for p in spec.get("panels",[]):
        pid=p["panel_id"]
        if pid not in pmap:
            continue
        hp=pmap[pid]
        p["visual_hierarchy"]={k:hp[k] for k in [
            "tier","axis_label_size_pt","tick_label_size_pt","annotation_size_pt",
            "marker_size_pt","line_width_pt","annotation_priority",
            "max_chars_per_annotation_line","max_annotation_lines","max_annotation_chars",
            "max_x_tick_labels","max_y_tick_labels","max_legend_items",
            "legend_strategy","direct_labels_preferred"
        ]}
    out.write_text(yaml.safe_dump(spec,sort_keys=False,allow_unicode=True),encoding="utf-8")
    return spec

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("render_spec"); ap.add_argument("visual_hierarchy"); ap.add_argument("--out",required=True)
    a=ap.parse_args(); apply(Path(a.render_spec),Path(a.visual_hierarchy),Path(a.out))
