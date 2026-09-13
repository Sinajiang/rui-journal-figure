from __future__ import annotations
import argparse,csv,json
from pathlib import Path

def audit(hierarchy_path:Path,label_inventory:Path):
    h=json.loads(hierarchy_path.read_text(encoding="utf-8"))
    pmap={p["panel_id"]:p for f in h.get("figures",[]) for p in f.get("panels",[])}
    rows=list(csv.DictReader(label_inventory.open(encoding="utf-8"),delimiter="\t"))
    review=[]; blocking=[]
    for r in rows:
        pid=r["panel_id"]; p=pmap.get(pid)
        if p is None:
            blocking.append({"type":"PANEL_NOT_IN_HIERARCHY","panel_id":pid}); continue
        def iv(k):
            try:return int(float(r.get(k) or 0))
            except:return 0
        xt=iv("x_tick_count"); yt=iv("y_tick_count"); leg=iv("legend_items")
        al=iv("annotation_lines"); ac=iv("annotation_chars")
        if xt>p["max_x_tick_labels"]:
            review.append({"type":"X_TICK_BUDGET_EXCEEDED","panel_id":pid,"observed":xt,"budget":p["max_x_tick_labels"]})
        if yt>p["max_y_tick_labels"]:
            review.append({"type":"Y_TICK_BUDGET_EXCEEDED","panel_id":pid,"observed":yt,"budget":p["max_y_tick_labels"]})
        if leg>p["max_legend_items"]:
            review.append({"type":"LEGEND_ITEM_BUDGET_EXCEEDED","panel_id":pid,"observed":leg,"budget":p["max_legend_items"]})
        if al>p["max_annotation_lines"]:
            review.append({"type":"ANNOTATION_LINE_BUDGET_EXCEEDED","panel_id":pid,"observed":al,"budget":p["max_annotation_lines"]})
        if ac>p["max_annotation_chars"]:
            review.append({"type":"ANNOTATION_CHAR_BUDGET_EXCEEDED","panel_id":pid,"observed":ac,"budget":p["max_annotation_chars"]})
    return {"blocking":blocking,"review":review,"pass":not blocking}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("visual_hierarchy"); ap.add_argument("label_inventory"); ap.add_argument("--out")
    a=ap.parse_args(); res=audit(Path(a.visual_hierarchy),Path(a.label_inventory))
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
