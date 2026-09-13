from __future__ import annotations
import argparse, json
from pathlib import Path

def build(state_path: Path, out: Path):
    s=json.loads(state_path.read_text(encoding="utf-8"))
    lines=[
        "# Top-journal figure workflow handoff",
        "",
        f"- Project ID: `{s.get('project_id','')}`",
        f"- Run ID: `{s.get('run_id','')}`",
        f"- Current state: **{s.get('current_state','')}**",
        "",
        "## Pending agent actions",
    ]
    acts=s.get("pending_agent_actions",[])
    if not acts:
        lines.append("- None")
    else:
        for x in acts:
            lines.append(f"- **{x['stage']}** — {x['action']}")
            if x.get("required_artifacts"):
                lines.append(f"  - Required artifacts: {', '.join(x['required_artifacts'])}")
    lines += ["","## Pending human reviews"]
    rev=s.get("pending_human_reviews",[])
    if not rev:
        lines.append("- None")
    else:
        for x in rev:
            lines.append(f"- **{x['stage']}** — {x['review']}")
            if x.get("required_artifact"):
                lines.append(f"  - Record: `{x['required_artifact']}`")
    lines += ["","## Stage statuses"]
    for stage,rec in s.get("stages",{}).items():
        lines.append(f"- {stage}: `{rec.get('status')}`")
    out.write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    build(Path(args.state),Path(args.out))
