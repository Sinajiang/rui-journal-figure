from pathlib import Path
import subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
FIX=Path(__file__).resolve().parent/"fixtures"
sys.path.insert(0,str(ROOT/"scripts"))

from audit_layout_contract import audit

def setup_module(module):
    subprocess.check_call([
        sys.executable,
        str(Path(__file__).resolve().parent/"make_synthetic_figures.py")
    ])

def test_card_contract_passes():
    r=audit(FIX/"card_clean.pdf",FIX/"card_contract.yaml")
    assert r["pass"] is True
