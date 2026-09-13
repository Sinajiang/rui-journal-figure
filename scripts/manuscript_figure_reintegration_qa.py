from __future__ import annotations
import argparse, json, sys
from pathlib import Path

from audit_evidence_graph import audit as audit_graph
from audit_figure_citations import audit as audit_citations
from audit_legend_architecture import audit as audit_legend
from audit_supplementary_numbering import audit as audit_supp

def run(manuscript, graph, legend_arch):
    g=audit_graph(graph)
    c=audit_citations(manuscript,graph)
    l=audit_legend(graph,legend_arch)
    s=audit_supp(manuscript)
    hard_pass=all(x["pass"] for x in [g,c,l,s])
    return {
        "manuscript":str(manuscript),
        "evidence_graph":str(graph),
        "legend_architecture":str(legend_arch),
        "evidence_graph_audit":g,
        "figure_citation_audit":c,
        "legend_architecture_audit":l,
        "supplementary_numbering_audit":s,
        "hard_pass":hard_pass,
        "manual_scientific_review_required":True,
        "promotion_rule":"Promote only if hard_pass is true and claim strength/evidence-status review is scientifically accepted."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manuscript")
    ap.add_argument("evidence_graph")
    ap.add_argument("legend_architecture")
    ap.add_argument("--out")
    args=ap.parse_args()
    res=run(Path(args.manuscript),Path(args.evidence_graph),Path(args.legend_architecture))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
