from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))

from workflow_utils import STAGE_ORDER
from run_top_journal_figure_workflow import Workflow

def test_visual_weighting_stage_order():
    assert 'VISUAL_WEIGHTING' in STAGE_ORDER
    assert STAGE_ORDER.index('ARCHITECTURE') < STAGE_ORDER.index('VISUAL_WEIGHTING') < STAGE_ORDER.index('PROTOTYPE')

def test_workflow_exposes_visual_weighting_method():
    assert hasattr(Workflow,'visual_weighting')
