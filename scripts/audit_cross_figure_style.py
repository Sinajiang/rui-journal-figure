from __future__ import annotations
import argparse, json
from pathlib import Path
from submission_compiler_utils import load_yaml, resolve, canonical_hex

def audit(manifest_path: Path):
    m=load_yaml(manifest_path); base=manifest_path.parent
    blocking=[]; review=[]
    global_style=m.get("global_style") or {}
    gfont=global_style.get("font_family")
    gcase=(global_style.get("panel_label_case") or "").lower()
    gcolors={k:canonical_hex(v) for k,v in (global_style.get("semantic_colors") or {}).items()}

    observed={}
    for f in m.get("figures",[]) or []:
        n=f["number"]
        sp=resolve(base,f.get("style_contract"))
        if not sp or not sp.exists():
            continue
        s=load_yaml(sp)
        observed[n]=s

        font=s.get("font_family")
        if gfont and font and font!=gfont:
            blocking.append({"type":"font_family_mismatch","figure":n,"observed":font,"expected":gfont})

        case=(s.get("panel_label_case") or "").lower()
        if gcase and case and case!=gcase:
            blocking.append({"type":"panel_label_case_mismatch","figure":n,"observed":case,"expected":gcase})

        exceptions=f.get("semantic_color_exceptions") or {}
        colors={k:canonical_hex(v) for k,v in (s.get("semantic_colors") or {}).items()}
        for sem,expected in gcolors.items():
            if sem in exceptions:
                continue
            obs=colors.get(sem)
            if obs is not None and expected is not None and obs!=expected:
                blocking.append({
                    "type":"semantic_color_mismatch",
                    "figure":n,"semantic":sem,
                    "observed":obs,"expected":expected
                })

        # Typography drift is review unless it violates explicit global contract.
        bfs=s.get("base_font_size_pt")
        pls=s.get("panel_label_size_pt")
        if bfs is not None and not (5 <= float(bfs) <= 9):
            review.append({"type":"unusual_base_font_size","figure":n,"value":bfs})
        if pls is not None and not (6 <= float(pls) <= 10):
            review.append({"type":"unusual_panel_label_size","figure":n,"value":pls})

    return {
        "blocking":blocking,
        "review":review,
        "pass":len(blocking)==0,
        "observed_style_contracts":observed
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.manifest))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
