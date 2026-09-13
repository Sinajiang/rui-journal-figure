from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def build(selected_json: Path, candidate_tsv: Path, out_md: Path):
    selected=json.loads(selected_json.read_text(encoding="utf-8"))["selected"]
    rows={r["benchmark_id"]:r for r in csv.DictReader(candidate_tsv.open(encoding="utf-8"),delimiter="\t")}
    lines=["# Benchmark dossier",""]
    for rank,x in enumerate(selected,start=1):
        bid=x["benchmark_id"]
        r=rows.get(bid,{})
        lines += [
            f"## {rank}. {r.get('title','')}",
            "",
            f"- Benchmark ID: `{bid}`",
            f"- Journal / year: {r.get('journal','')} / {r.get('year','')}",
            f"- DOI: {r.get('doi','') or 'not recorded'}",
            f"- URL: {r.get('url','')}",
            f"- Verification: {r.get('verification_status','')}",
            f"- Ranking score: {x.get('score_0_to_5','')}/5",
            f"- Search provenance: round {r.get('search_round','')} — `{r.get('search_query','')}`",
            "",
            "### Why selected",
            f"- Scientific similarity: {r.get('scientific_similarity','')}/5",
            f"- Method similarity: {r.get('method_similarity','')}/5",
            f"- Modality similarity: {r.get('modality_similarity','')}/5",
            f"- Figure-role relevance: {r.get('figure_role_relevance','')}/5",
            "",
            "### Manual grammar extraction required",
            "- Figure-level question:",
            "- Anchor panel:",
            "- Evidence sequence:",
            "- Main vs Supplementary allocation:",
            "- Chart vocabulary:",
            "- Transferable principles:",
            "- Features not to copy:",
            "- Current-study mapping:",
            "",
        ]
    out_md.write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("selected_json")
    ap.add_argument("candidate_tsv")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    build(Path(args.selected_json),Path(args.candidate_tsv),Path(args.out))
