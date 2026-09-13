from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml
from architecture_utils import load_panels, panel_utility

def audit(candidate_json: Path, optimizer_input: Path):
    c=json.loads(candidate_json.read_text(encoding="utf-8"))
    inp=yaml.safe_load(optimizer_input.read_text(encoding="utf-8"))
    inv=(optimizer_input.parent/inp["panel_inventory_tsv"]).resolve()
    panels={p["panel_id"]:p for p in load_panels(inv)}

    main_ids=set()
    for f in c.get("figures",[]):
        main_ids.update(f.get("panels",[]))
    supp=set(c.get("supplementary_panels",[]) or [])

    review=[]
    for pid in main_ids:
        p=panels[pid]
        if not p.get("must_main") and panel_utility(p)<5.5:
            review.append({
                "type":"low_utility_main_panel",
                "panel_id":pid,
                "utility":round(panel_utility(p),3)
            })
    for pid in supp:
        if pid in panels:
            p=panels[pid]
            if p.get("must_main"):
                review.append({"type":"must_main_panel_in_supplement","panel_id":pid})
            elif panel_utility(p)>=8.0:
                review.append({
                    "type":"high_utility_panel_demoted",
                    "panel_id":pid,
                    "utility":round(panel_utility(p),3)
                })

    return {
        "main_panel_count":len(main_ids),
        "supplementary_panel_count":len(supp),
        "review":review,
        "pass":not any(x["type"]=="must_main_panel_in_supplement" for x in review)
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("optimizer_input")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.candidate_json),Path(args.optimizer_input))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
