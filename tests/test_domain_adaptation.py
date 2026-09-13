from pathlib import Path
import sys, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"domain_adaptation"
sys.path.insert(0,str(ROOT/"scripts"))

from infer_scientific_domain import infer
from resolve_domain_grammar import resolve
from audit_domain_figure_architecture import audit

def test_domain_inference_identifies_transcriptomics():
    r=infer([FIX/"transcriptomics.txt"],ROOT/"domain_profiles")
    assert r["suggested_primary_domain"]=="transcriptomics_bulk"
    assert r["ranked_domains"][0]["score"] > 0

def test_domain_grammar_resolves_primary_secondary():
    r=resolve(FIX/"selection.yaml",ROOT/"domain_profiles")
    assert r["primary_domain"]=="transcriptomics_bulk"
    assert "effect_plot" in r["preferred_chart_types"]
    assert len(r["core_questions"]) >= 5

def test_domain_architecture_audit_runs(tmp_path):
    g=resolve(FIX/"selection.yaml",ROOT/"domain_profiles")
    gp=tmp_path/"grammar.json"
    gp.write_text(json.dumps(g),encoding="utf-8")
    r=audit(FIX/"candidate.json",gp,FIX/"panels.tsv")
    assert r["pass"] is True
    assert r["domain_archetype_coverage"] >= 0.5

def test_all_seven_profiles_exist():
    expected={
        "transcriptomics_bulk","single_cell","clinical_cohort",
        "survival_longitudinal","prediction_modeling","meta_analysis",
        "multimodal_clinical"
    }
    found={p.stem for p in (ROOT/"domain_profiles").glob("*.yaml")}
    assert expected.issubset(found)
