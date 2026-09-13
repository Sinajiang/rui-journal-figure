from __future__ import annotations
import argparse,json
from pathlib import Path

def build(path:Path,out:Path):
    h=json.loads(path.read_text(encoding="utf-8"))
    L=["# Visual hierarchy and typography report","",
       f"- Font family: **{h.get('font_family')}**",
       f"- Panel-label size: **{h.get('panel_label_size_pt')} pt**",
       f"- Operational minimum font: **{h.get('operational_min_font_pt')} pt**",""]
    for f in h.get("figures",[]):
        L.append(f"## {f.get('figure_id')}")
        L.append("")
        for p in f.get("panels",[]):
            L.append(
                f"- **{p['panel_id']}** — {p['tier']}; score {p['contribution_score']}; "
                f"{p['panel_width_mm']}×{p['panel_height_mm']} mm; "
                f"axis/tick/annotation {p['axis_label_size_pt']}/{p['tick_label_size_pt']}/{p['annotation_size_pt']} pt; "
                f"marker {p['marker_size_pt']} pt; line {p['line_width_pt']} pt; "
                f"annotation budget {p['max_annotation_lines']} lines / {p['max_annotation_chars']} chars."
            )
        L.append("")
    if h.get("review_flags"):
        L += ["## Review flags",""]+[f"- `{x['type']}` — {x.get('panel_id','')}" for x in h["review_flags"]]
    out.write_text("\n".join(L)+"\n",encoding="utf-8")

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("visual_hierarchy"); ap.add_argument("--out",required=True)
    a=ap.parse_args(); build(Path(a.visual_hierarchy),Path(a.out))
