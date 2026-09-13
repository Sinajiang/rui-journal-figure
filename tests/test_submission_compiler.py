from pathlib import Path
import sys, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"submission_compiler"
sys.path.insert(0,str(ROOT/"scripts"))

from validate_figure_set_manifest import validate
from audit_cross_figure_style import audit as audit_style
from audit_figure_set_rasters import audit as audit_rasters
from compile_final_submission_figures import compile as compile_pkg
from figure_package_promotion_controller import decide

def test_good_manifest_passes():
    r=validate(FIX/"manifest.yaml")
    assert r["pass"] is True

def test_unpromoted_figure_blocks():
    r=validate(FIX/"bad_manifest.yaml")
    assert r["pass"] is False
    assert any(x["type"]=="unpromoted_figure" for x in r["blocking"])

def test_semantic_color_mismatch_blocks():
    r=audit_style(FIX/"color_mismatch_manifest.yaml")
    assert r["pass"] is False
    assert any(x["type"]=="semantic_color_mismatch" for x in r["blocking"])

def test_raster_audit_passes():
    r=audit_rasters(FIX/"manifest.yaml",min_dpi=300)
    assert r["pass"] is True

def test_compiler_creates_package(tmp_path):
    r=compile_pkg(FIX/"manifest.yaml",tmp_path)
    assert r["state"] == "FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION"
    assert (tmp_path/"FINAL_SUBMISSION_FIGURES"/"Figure_1.pdf").exists()
    assert (tmp_path/"SOURCE_DATA"/"Figure_2").exists()
    assert (tmp_path/"QA"/"figure_set_contact_sheet.png").exists()
    assert (tmp_path/"MANIFEST_SHA256.json").exists()

def test_promotion_controller_requires_manual_review(tmp_path):
    r=compile_pkg(FIX/"manifest.yaml",tmp_path)
    d=decide(
        tmp_path/"COMPILATION_SUMMARY.json",
        "PENDING",
        manuscript_reintegration_pass=True,
        journal_upload_contract_pass=True
    )
    assert d["decision"] == "HOLD"

def test_promotion_controller_promotes_when_all_pass(tmp_path):
    r=compile_pkg(FIX/"manifest.yaml",tmp_path)
    d=decide(
        tmp_path/"COMPILATION_SUMMARY.json",
        "PASS",
        manuscript_reintegration_pass=True,
        journal_upload_contract_pass=True
    )
    assert d["state"] == "FIGURE_PACKAGE_SUBMISSION_READY"
