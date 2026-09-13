from pathlib import Path
import sys, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"architecture_optimizer"
sys.path.insert(0,str(ROOT/"scripts"))

from architecture_utils import load_panels, redundancy_score
from compute_panel_redundancy import compute
from optimize_main_figure_architecture import optimize
from recommend_panel_actions import recommend

def test_redundancy_detects_similar_robustness_panels():
    panels={p["panel_id"]:p for p in load_panels(FIX/"panels.tsv")}
    s=redundancy_score(panels["P04"],panels["P05"])
    assert s >= 0.70

def test_optimizer_generates_three_four_five_candidates():
    r=optimize(FIX/"optimizer_input.yaml")
    assert [x["target_figure_count"] for x in r["candidates"]] == [3,4,5]

def test_unavailable_panels_never_promoted():
    r=optimize(FIX/"optimizer_input.yaml")
    for c in r["candidates"]:
        main={p for f in c["figures"] for p in f["panels"]}
        assert "P08" not in main
        assert "P09" not in main
        assert "P08" in c["upgrade_candidates"]

def test_must_main_panels_retained_in_eligible_candidates():
    r=optimize(FIX/"optimizer_input.yaml")
    for c in r["candidates"]:
        if c["hard_gates"]["pass"]:
            main={p for f in c["figures"] for p in f["panels"]}
            assert {"P01","P02","P06"}.issubset(main)

def test_optimizer_recommends_four_figures_in_fixture():
    r=optimize(FIX/"optimizer_input.yaml")
    assert r["recommended_target_figure_count"] == 4

def test_action_recommender_flags_optional_analysis():
    r=recommend(FIX/"optimizer_input.yaml")
    a={x["panel_id"]:x for x in r["actions"]}
    assert a["P08"]["action"] == "UPGRADE_CANDIDATE"

def test_action_recommender_merges_lower_value_redundant_panel():
    r=recommend(FIX/"optimizer_input.yaml")
    a={x["panel_id"]:x for x in r["actions"]}
    assert a["P05"]["action"] == "MERGE"
    assert a["P05"]["target_or_partner"] == "P04"
