from pathlib import Path
import sys, csv, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"benchmark_retrieval"
sys.path.insert(0,str(ROOT/"scripts"))

from generate_benchmark_queries import generate
from normalize_benchmark_candidates import normalize
from rank_benchmark_candidates import rank
from audit_benchmark_provenance import audit as audit_prov
from audit_search_saturation import audit as audit_sat
from select_diverse_benchmark_set import select

def test_query_generation_has_multiple_rounds():
    r=generate(FIX/"brief.yaml")
    rounds={x["round"] for x in r["generated_queries"]}
    assert {1,2,3,4}.issubset(rounds)

def test_provenance_audit_passes():
    r=audit_prov(FIX/"candidates.tsv")
    assert r["pass"] is True
    assert r["count"] == 7

def test_normalization_detects_duplicate_doi(tmp_path):
    out=tmp_path/"normalized.tsv"
    r=normalize(FIX/"candidates.tsv",out)
    assert r["kept_count"] == 6
    assert any(x["duplicate_benchmark_id"]=="B7" for x in r["duplicates"])

def test_ranking_penalizes_unverified_figure_detail():
    r=rank(FIX/"candidates.tsv")
    score={x["benchmark_id"]:x["score_0_to_5"] for x in r["ranked"]}
    assert score["B6"] < score["B4"]

def test_saturation_stops_after_two_stagnant_rounds():
    r=audit_sat(FIX/"round_log.tsv",min_selected=5,saturation_rounds=2)
    assert r["stop"] is True
    assert r["reason"] == "saturation_reached"

def test_diverse_selector_respects_maximum(tmp_path):
    ranked=rank(FIX/"candidates.tsv")
    p=tmp_path/"ranked.json"
    p.write_text(json.dumps(ranked),encoding="utf-8")
    r=select(p,minimum=5,maximum=5,max_per_journal=2)
    assert r["selected_count"] == 5
    assert len(r["selected"]) == 5
