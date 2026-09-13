from __future__ import annotations
import argparse,json
from pathlib import Path
def audit(layout_path,grammar_path):
    l=json.loads(Path(layout_path).read_text(encoding="utf-8")); g=json.loads(Path(grammar_path).read_text(encoding="utf-8"))
    rev=[]; dom=(g.get("topology") or {}).get("dominant")
    if dom and l.get("topology")!=dom: rev.append({"type":"topology_divergence","observed":l.get("topology"),"benchmark_dominant":dom})
    if l.get("panels"):
        a=l["panels"][0].get("target_area_share"); q1=(g.get("anchor_area_share") or {}).get("q1"); q3=(g.get("anchor_area_share") or {}).get("q3")
        if q1 is not None and a<q1-.08: rev.append({"type":"anchor_share_below_benchmark_range"})
        if q3 is not None and a>q3+.10: rev.append({"type":"anchor_share_above_benchmark_range"})
    return {"review":rev,"pass":True,"note":"Benchmark divergence is advisory."}
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("layout_spec"); ap.add_argument("layout_grammar"); ap.add_argument("--out")
    a=ap.parse_args(); res=audit(a.layout_spec,a.layout_grammar); txt=json.dumps(res,indent=2); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding="utf-8")
