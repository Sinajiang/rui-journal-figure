from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml
from architecture_utils import load_panels, redundancy_score, panel_utility

def recommend(input_path: Path):
    inp=yaml.safe_load(input_path.read_text(encoding="utf-8"))
    inv=(input_path.parent/inp["panel_inventory_tsv"]).resolve()
    panels=load_panels(inv)
    thr=float((inp.get("constraints") or {}).get("redundancy_threshold",0.72))
    max_density=float((inp.get("constraints") or {}).get("max_visual_density_per_figure",26))
    actions=[]

    # Identify strongest redundancy partner.
    partner={}
    for i,a in enumerate(panels):
        for b in panels[i+1:]:
            s=redundancy_score(a,b)
            if s>=thr:
                for x,y in [(a,b),(b,a)]:
                    cur=partner.get(x["panel_id"])
                    if cur is None or s>cur[1]:
                        partner[x["panel_id"]]=(y,s)

    for p in panels:
        pid=p["panel_id"]
        avail=p.get("availability")
        current=(p.get("current_location") or "unassigned").lower()
        util=panel_utility(p)

        if avail=="OPTIONAL_NEW_ANALYSIS":
            action="UPGRADE_CANDIDATE"; target=""
            reason="Benchmark-informed evidence is not yet available."
            recommended="upgrade_candidate"
        elif avail=="NOT_APPLICABLE":
            action="DROP_NOT_APPLICABLE"; target=""
            reason="Panel concept is incompatible with current study evidence."
            recommended="drop"
        elif pid in partner and not p.get("must_main"):
            q,s=partner[pid]
            if util <= panel_utility(q):
                action="MERGE"; target=q["panel_id"]
                reason=f"High redundancy score {s:.2f} with higher-value partner."
                recommended="supplement_or_merge"
            else:
                action="KEEP"; target=""
                reason="Higher-value member of a redundant pair."
                recommended=current
        elif p.get("must_main"):
            action="KEEP" if current=="main" else "PROMOTE"
            target=""
            reason="Declared must-main evidence."
            recommended="main"
        elif p.get("visual_density",0)>=8 and util>=6.5:
            action="REPAIR"; target=""
            reason="Scientifically valuable but visually dense."
            recommended="main_or_compact_main"
        elif util>=7:
            action="KEEP" if current=="main" else "PROMOTE"
            target=""
            reason=f"High panel utility {util:.2f}."
            recommended="main"
        else:
            action="DEMOTE"; target=""
            reason=f"Lower panel utility {util:.2f} relative to main-display competition."
            recommended="supplement"

        actions.append({
            "panel_id":pid,
            "action":action,
            "target_or_partner":target,
            "reason":reason,
            "current_location":current,
            "recommended_location":recommended
        })

    return {"actions":actions}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("optimizer_input")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=recommend(Path(args.optimizer_input))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
