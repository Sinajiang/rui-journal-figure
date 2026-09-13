from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def first(xs):
    return xs[0] if xs else ""

def uniq(seq):
    out=[]; seen=set()
    for x in seq:
        x=" ".join(str(x).split())
        if x and x not in seen:
            out.append(x); seen.add(x)
    return out

def generate(brief_path: Path):
    b=yaml.safe_load(brief_path.read_text(encoding="utf-8"))
    p=b["project"]; c=b["concepts"]

    journal=p.get("target_journal","")
    topic=first(c.get("disease_or_topic",[]))
    design=first(c.get("study_design",[]))
    modality=first(c.get("modality",[]))
    outcome=first(c.get("primary_estimand_or_outcome",[]))
    method=first(c.get("key_methods",[]))
    roles=c.get("desired_figure_roles",[])

    q=[]
    # Round 1: closest scientific match in target journal
    q += [
        {"round":1,"family":"target_scientific","query":f'"{journal}" {topic} {outcome} {modality}'},
        {"round":1,"family":"target_design","query":f'"{journal}" {topic} {design} {method}'},
    ]
    # Round 2: target journal methodological analogues
    q += [
        {"round":2,"family":"target_method","query":f'"{journal}" {modality} {method} {design}'},
        {"round":2,"family":"target_modality","query":f'"{journal}" {modality} original research'},
    ]
    # Round 3: peer-journal style broad queries
    q += [
        {"round":3,"family":"peer_scientific","query":f'{topic} {outcome} {modality} {design}'},
        {"round":3,"family":"peer_method","query":f'{topic} {method} {modality} {design}'},
    ]
    # Role-specific
    for role in roles[:4]:
        q.append({"round":3,"family":"figure_role","query":f'{topic} {modality} {role}'})
    # Round 4: field-defining / broad
    q += [
        {"round":4,"family":"field_defining","query":f'{topic} {modality} landmark study'},
    ]

    # Clean empty double spaces and dedup by query
    cleaned=[]
    seen=set()
    for x in q:
        qq=" ".join(x["query"].split()).strip()
        if qq and qq not in seen:
            x["query"]=qq
            cleaned.append(x)
            seen.add(qq)

    return {
        "project":p,
        "generated_queries":cleaned,
        "note":"Adapt syntax to the available search engine. Verify all retrieved paper metadata."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("search_brief")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=generate(Path(args.search_brief))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
