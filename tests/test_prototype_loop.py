from pathlib import Path
import sys, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"prototype_loop"
sys.path.insert(0,str(ROOT/"scripts"))

from score_structural_prototype import score
from promotion_controller import decide
from compare_to_visual_baseline import compare

def test_structural_visual_score_is_computable():
    r=score(FIX/"candidate.json",FIX/"panels.tsv")
    assert 0 <= r["metrics"]["overall_visual_score"] <= 10
    assert r["figure_count"] == 3

def test_promotion_controller_promotes_good_candidate():
    d=decide(
        architecture_score=8.8,
        visual_score=8.3,
        hard_gates_pass=True,
        manual_visual_status="PASS",
        baseline_visual_score=8.0,
        baseline_architecture_score=8.5,
        blocking_visual_issues=0
    )
    assert d["decision"] == "PROMOTE"

def test_promotion_controller_repairs_blocking_visual_issue():
    d=decide(
        architecture_score=8.8,
        visual_score=8.3,
        hard_gates_pass=True,
        manual_visual_status="PASS",
        baseline_visual_score=8.0,
        baseline_architecture_score=8.5,
        blocking_visual_issues=1
    )
    assert d["decision"] == "REPAIR"

def test_promotion_controller_rolls_back_visual_regression():
    d=decide(
        architecture_score=8.8,
        visual_score=7.2,
        hard_gates_pass=True,
        manual_visual_status="PASS",
        baseline_visual_score=8.0,
        baseline_architecture_score=8.5,
        blocking_visual_issues=0
    )
    assert d["decision"] == "ROLLBACK"

def test_promotion_controller_holds_without_manual_review():
    d=decide(
        architecture_score=8.8,
        visual_score=8.4,
        hard_gates_pass=True,
        manual_visual_status="PENDING",
        baseline_visual_score=8.0,
        baseline_architecture_score=8.5,
        blocking_visual_issues=0
    )
    assert d["decision"] == "HOLD"

def test_baseline_comparison_detects_regression(tmp_path):
    v={"metrics":{"overall_visual_score":7.0}}
    p=tmp_path/"v.json"
    p.write_text(json.dumps(v),encoding="utf-8")
    r=compare(FIX/"baseline.yaml",p,8.8)
    assert r["visual_regression"] is True
