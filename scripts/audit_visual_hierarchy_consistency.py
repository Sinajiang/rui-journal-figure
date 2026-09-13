from __future__ import annotations
import argparse,json
from pathlib import Path

def audit(path:Path,score_gap=1.5):
    h=json.loads(path.read_text(encoding="utf-8"))
    review=[]; blocking=[]
    minfont=float(h.get("operational_min_font_pt",5.5))
    for fig in h.get("figures",[]):
        panels=fig.get("panels",[])
        for p in panels:
            for k in ["axis_label_size_pt","tick_label_size_pt","annotation_size_pt"]:
                if float(p[k])<minfont-1e-9:
                    blocking.append({"type":"FONT_BELOW_OPERATIONAL_FLOOR","panel_id":p["panel_id"],"field":k,"value":p[k],"floor":minfont})
        for i,a in enumerate(panels):
            for b in panels[i+1:]:
                sa=float(a["contribution_score"]); sb=float(b["contribution_score"])
                if sa>=sb+score_gap:
                    hi,lo=a,b
                elif sb>=sa+score_gap:
                    hi,lo=b,a
                else:
                    continue
                if float(hi["marker_size_pt"])+.05<float(lo["marker_size_pt"]):
                    review.append({"type":"MARKER_HIERARCHY_INVERSION","higher_panel":hi["panel_id"],"lower_panel":lo["panel_id"]})
                if float(hi["line_width_pt"])+.02<float(lo["line_width_pt"]):
                    review.append({"type":"LINE_HIERARCHY_INVERSION","higher_panel":hi["panel_id"],"lower_panel":lo["panel_id"]})
                if int(hi["annotation_priority"])<int(lo["annotation_priority"]):
                    review.append({"type":"ANNOTATION_PRIORITY_INVERSION","higher_panel":hi["panel_id"],"lower_panel":lo["panel_id"]})
        # global panel label consistency is figure-level by construction
    return {"blocking":blocking,"review":review,"pass":not blocking}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("visual_hierarchy"); ap.add_argument("--out")
    a=ap.parse_args(); res=audit(Path(a.visual_hierarchy))
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
