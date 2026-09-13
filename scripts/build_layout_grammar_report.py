from __future__ import annotations
import argparse,json
from pathlib import Path
def build(gp,out):
    g=json.loads(Path(gp).read_text(encoding="utf-8"))
    L=["# Benchmark-derived layout grammar report","",
       f"- Benchmark figures: **{g['corpus']['n_figures']}**",
       f"- Dominant topology: **{g['topology']['dominant']}**",
       f"- Median panel count: **{g['panel_count']['median']}**",
       f"- Median anchor share: **{g['anchor_area_share']['median']}**",
       f"- Median workflow share: **{g['workflow_area_share']['median']}**",
       f"- Median white-space: **{g['white_space_fraction']['median']}**",
       f"- Dominant legend strategy: **{g['legend_strategy']['dominant']}**","",
       "## Role-specific area priors"]
    for role,v in g.get("role_area_priors",{}).items():
        L.append(f"- **{role}**: median {v['median']}, IQR {v['q1']}–{v['q3']} (n={v['n']})")
    Path(out).write_text("\n".join(L)+"\n",encoding="utf-8")
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("layout_grammar"); ap.add_argument("--out",required=True)
    a=ap.parse_args(); build(a.layout_grammar,a.out)
