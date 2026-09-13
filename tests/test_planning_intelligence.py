from pathlib import Path
import sys, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"planning"
sys.path.insert(0,str(ROOT/"scripts"))

from validate_benchmark_manifest import validate as validate_benchmarks
from validate_candidate_figure_plan import validate as validate_plan
from score_candidate_figure_plan import score
from compare_candidate_figure_plans import compare
from inspect_source_tables import inspect_one

def test_benchmark_manifest_passes():
    r=validate_benchmarks(FIX/"benchmarks.tsv")
    assert r["pass"] is True
    assert r["count"] == 3

def test_source_table_inspection():
    r=inspect_one(FIX/"source.tsv")
    assert r["rows"] == 2
    assert "effect" in r["numeric_columns"]

def test_good_candidate_passes():
    r=validate_plan(FIX/"candidate_good.yaml",allow_new_analysis=False)
    assert r["pass"] is True

def test_optional_new_analysis_blocks_promotion():
    r=validate_plan(FIX/"candidate_bad.yaml",allow_new_analysis=False)
    assert r["pass"] is False
    assert any(x["type"]=="unavailable_panel_in_promoted_plan" for x in r["blocking"])

def test_candidate_score_computes():
    r=score(FIX/"candidate_good.yaml")
    assert r["pass"] is True
    assert r["weighted_score_0_to_10"] > 8

def test_compare_recommends_best_eligible():
    r=compare([FIX/"candidate_good.yaml",FIX/"candidate_bad.yaml",FIX/"candidate_alt.yaml"])
    assert r["recommended_candidate"] == "Candidate_A"
    assert all(x["candidate_id"] != "Candidate_B" for x in r["eligible_ranked"])
