from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; FIX=ROOT/"tests/fixtures/layout_grammar"; sys.path.insert(0,str(ROOT/"scripts"))
from validate_benchmark_layout_annotations import validate
from aggregate_benchmark_layout_grammar import aggregate
from solve_benchmark_weighted_layout import solve
def test_annotations(): assert validate(FIX/"annotations.tsv")["pass"]
def test_aggregate():
    g=aggregate(FIX/"annotations.tsv"); assert g["topology"]["dominant"]=="anchor_left_stack_right"; assert "anchor" in g["role_area_priors"]
def test_solver(tmp_path):
    g=aggregate(FIX/"annotations.tsv"); p=tmp_path/"g.json"; p.write_text(json.dumps(g))
    r=solve(FIX/"contribution.json",p,"Figure_1"); assert len(r["panels"])==3; assert r["panels"][0]["target_area_share"]>r["panels"][1]["target_area_share"]
