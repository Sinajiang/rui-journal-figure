from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

NONCLAIM_ROLES={"workflow","provenance","methods","design"}
DIRECT_STATUSES={"DIRECT"}
ALLOWED_STATUSES={"DIRECT","SUPPORTING","CONTEXTUAL","ROBUSTNESS","MECHANISTIC","BOUNDARY","UNSUPPORTED"}

def audit(path: Path):
    g=yaml.safe_load(path.read_text(encoding="utf-8"))
    blocking=[]
    review=[]
    claims={c["id"]:c for c in g.get("claims",[]) or []}
    figures=g.get("figures",{}) or {}
    sources=g.get("sources",{}) or {}
    legends=g.get("legend_clauses",{}) or {}

    # Claim links resolve.
    for cid,c in claims.items():
        if c.get("status") not in ALLOWED_STATUSES:
            blocking.append({"type":"invalid_evidence_status","claim_id":cid,"status":c.get("status")})
        for link in c.get("figure_links",[]) or []:
            f=str(link["figure"])
            p=str(link.get("panel") or "")
            fobj=figures.get(int(f),figures.get(f))
            if fobj is None:
                blocking.append({"type":"missing_figure","claim_id":cid,"figure":f})
                continue
            if p and p not in (fobj.get("panels") or {}):
                blocking.append({"type":"missing_panel","claim_id":cid,"figure":f,"panel":p})

        strength=(c.get("strength") or "").lower()
        status=c.get("status")
        if strength=="replication" and status not in {"DIRECT"}:
            review.append({"type":"replication_claim_without_direct_status","claim_id":cid,"status":status})
        if strength=="causal" and status not in {"DIRECT","MECHANISTIC"}:
            review.append({"type":"causal_claim_evidence_mismatch","claim_id":cid,"status":status})

    # Panels resolve to claims/sources/legends.
    for fkey,fobj in figures.items():
        for panel,pobj in (fobj.get("panels") or {}).items():
            role=(pobj.get("role") or "").lower()
            claim_ids=pobj.get("claim_ids",[]) or []
            if role not in NONCLAIM_ROLES and not claim_ids:
                review.append({"type":"orphan_panel_no_claim","figure":fkey,"panel":panel,"role":role})
            for cid in claim_ids:
                if cid not in claims:
                    blocking.append({"type":"panel_links_missing_claim","figure":fkey,"panel":panel,"claim_id":cid})
            sid=pobj.get("source_id")
            if sid and sid not in sources:
                blocking.append({"type":"missing_source","figure":fkey,"panel":panel,"source_id":sid})
            if role not in NONCLAIM_ROLES and not sid:
                review.append({"type":"quantitative_or_evidence_panel_without_source","figure":fkey,"panel":panel})
            lid=pobj.get("legend_clause_id")
            if lid and lid not in legends:
                blocking.append({"type":"missing_legend_clause","figure":fkey,"panel":panel,"legend_clause_id":lid})

    # Legend clauses resolve to existing panels.
    for lid,l in legends.items():
        f=str(l["figure"]); p=str(l["panel"])
        fobj=figures.get(int(f),figures.get(f))
        if fobj is None or p not in (fobj.get("panels") or {}):
            blocking.append({"type":"legend_clause_orphan","legend_clause_id":lid,"figure":f,"panel":p})

    return {
        "file":str(path),
        "blocking":blocking,
        "review":review,
        "pass":len(blocking)==0,
        "counts":{"claims":len(claims),"figures":len(figures),"sources":len(sources),"legend_clauses":len(legends)}
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("evidence_graph")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=audit(Path(args.evidence_graph))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
