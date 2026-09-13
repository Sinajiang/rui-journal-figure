from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml
from extract_figure_mentions import extract

def audit(manuscript: Path, evidence_graph: Path):
    mentions=extract(manuscript)
    g=yaml.safe_load(evidence_graph.read_text(encoding="utf-8"))
    figures=g.get("figures",{}) or {}
    blocking=[]
    review=[]

    declared={}
    for fk,fobj in figures.items():
        declared[str(fk)] = set((fobj.get("panels") or {}).keys())

    for m in mentions["figures"]:
        f=m["figure"]
        if f.startswith("S"):
            continue
        if f not in declared:
            blocking.append({"type":"citation_missing_figure","citation":m})
            continue
        for p in m["panels"]:
            if p not in declared[f]:
                blocking.append({"type":"citation_missing_panel","citation":m,"declared_panels":sorted(declared[f])})

    # Main panels not cited anywhere.
    cited={(m["figure"],p) for m in mentions["figures"] if not m["figure"].startswith("S") for p in m["panels"]}
    for f,panels in declared.items():
        for p in panels:
            role=(figures.get(int(f),figures.get(f))["panels"][p].get("role") or "").lower()
            if (f,p) not in cited and role not in {"workflow","provenance","methods","design"}:
                review.append({"type":"panel_not_explicitly_cited","figure":f,"panel":p,"role":role})

    return {
        "manuscript":str(manuscript),
        "evidence_graph":str(evidence_graph),
        "blocking":blocking,
        "review":review,
        "pass":len(blocking)==0,
        "mentions":mentions,
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manuscript")
    ap.add_argument("evidence_graph")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.manuscript),Path(args.evidence_graph))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
