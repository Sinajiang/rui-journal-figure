from __future__ import annotations
import argparse,json
from pathlib import Path

def build(plan:Path):
    d=json.loads(plan.read_text(encoding="utf-8")); s=d.get("summary",{})
    lines=["# Annotation and legend intelligence report","",f"Candidates: {s.get('candidate_count',0)}; DIRECT: {s.get('direct_count',0)}; LEGEND: {s.get('legend_count',0)}; SUPPRESS: {s.get('suppress_count',0)}.",""]
    for fig in d.get("figures",[]):
        lines += [f"## {fig.get('figure_id')}",""]
        if fig.get("shared_legend_clauses"):
            lines.append("Shared legend clauses:")
            for x in fig["shared_legend_clauses"]: lines.append(f"- {x}")
            lines.append("")
        if fig.get("shared_legend_guidance"):
            lines.append("Legend guidance (not verbatim submission prose):")
            for x in fig["shared_legend_guidance"]: lines.append(f"- {x}")
            lines.append("")
        for p in fig.get("panels",[]):
            lines.append(f"### {p.get('panel_id')} — {p.get('tier','')}")
            for key,title in [("direct_annotations","Direct"),("legend_annotations","Legend"),("suppressed_annotations","Suppressed")]:
                xs=p.get(key,[]); lines.append(f"**{title}**")
                if not xs: lines.append("- None")
                for x in xs:
                    reason=", ".join(x.get("reasons") or [])
                    lines.append(f"- `{x.get('annotation_id')}` {x.get('statistic_type')}: {x.get('text') or '[encoding only]'} — {reason}")
            lines.append("")
    if d.get("review_flags"):
        lines += ["## Review flags",""]+[f"- {json.dumps(x,ensure_ascii=False)}" for x in d["review_flags"]]
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("--out")
    a=ap.parse_args(); txt=build(Path(a.plan)); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
