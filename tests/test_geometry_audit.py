from pathlib import Path
import subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
FIX=Path(__file__).resolve().parent/"fixtures"
sys.path.insert(0,str(ROOT/"scripts"))

from audit_pdf_geometry import audit

def setup_module(module):
    subprocess.check_call([
        sys.executable,
        str(Path(__file__).resolve().parent/"make_synthetic_figures.py")
    ])

def test_clean_has_no_blocking_text_text_overlap():
    r=audit(FIX/"clean.pdf")
    assert r["blocking_count"] == 0

def test_overlap_is_detected():
    r=audit(FIX/"text_overlap.pdf")
    assert r["blocking_count"] >= 1
    assert any(
        issue["type"]=="text_text_overlap"
        for page in r["pages"]
        for issue in page["blocking"]
    )
