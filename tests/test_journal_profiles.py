from pathlib import Path
import sys, yaml, json

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from validate_journal_contract import validate

def load(name):
    return yaml.safe_load((ROOT/"journal_profiles"/name).read_text(encoding="utf-8"))

def test_nature_profile_width_and_font_pass():
    profile=load("nature.yaml")
    meta={
        "format":"pdf",
        "width_mm":180.0,
        "height_mm":150.0,
        "min_text_pt":5.6,
        "max_text_pt":7.0,
        "is_vector_container":True
    }
    r=validate(meta,profile,"initial_submission")
    assert r["pass"] is True
    assert not r["hard_failures"]

def test_nature_height_failure():
    profile=load("nature.yaml")
    meta={
        "format":"pdf",
        "width_mm":180.0,
        "height_mm":180.0,
        "min_text_pt":5.6,
        "max_text_pt":7.0,
    }
    r=validate(meta,profile,"initial_submission")
    assert r["pass"] is False
    assert any("height" in x for x in r["hard_failures"])

def test_headache_profile_does_not_invent_width():
    profile=load("headache.yaml")
    cfg=profile["stages"]["submission"]
    assert "preferred_width_mm" not in cfg
    assert any("not stated" in x for x in cfg["notes"])

def test_braincomms_recommended_text_is_warning_not_hard_fail():
    profile=load("brain_communications.yaml")
    meta={
        "format":"pdf",
        "width_mm":180.0,
        "height_mm":120.0,
        "min_text_pt":7.0,
        "max_text_pt":9.0,
    }
    r=validate(meta,profile,"publication")
    assert r["pass"] is True
    assert any("recommended" in x for x in r["warnings"])
