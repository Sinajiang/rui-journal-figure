from pathlib import Path
import sys, tempfile, json, yaml

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"real_data_engine"
sys.path.insert(0,str(ROOT/"scripts"))

from validate_frozen_sentinels import validate as validate_sentinels
from validate_render_spec import validate as validate_spec
from render_real_data_figure import render
from produce_real_data_figure import produce

def test_good_sentinels_pass():
    r=validate_sentinels(FIX/"sentinels.yaml",FIX)
    assert r["pass"] is True

def test_bad_sentinel_fails():
    r=validate_sentinels(FIX/"bad_sentinels.yaml",FIX)
    assert r["pass"] is False

def test_render_spec_passes():
    r=validate_spec(FIX/"render_spec.yaml")
    assert r["pass"] is True

def test_renderer_exports_files(tmp_path):
    r=render(FIX/"render_spec.yaml",tmp_path)
    assert Path(r["outputs"]["pdf"]).exists()
    assert Path(r["outputs"]["svg"]).exists()
    assert Path(r["outputs"]["tiff"]).exists()
    assert Path(r["outputs"]["png_preview"]).exists()
    assert (tmp_path/"SOURCE_DATA"/"Figure_1_P2_source_data.tsv").exists()

def test_production_stops_on_bad_sentinel(tmp_path):
    r=produce(FIX/"render_spec.yaml",FIX/"bad_sentinels.yaml",tmp_path)
    assert r["status"] == "FAIL_SENTINEL"
    assert r["rendered"] is False

def test_production_runs_on_good_sentinel(tmp_path):
    r=produce(FIX/"render_spec.yaml",FIX/"sentinels.yaml",tmp_path)
    assert r["status"] == "RENDERED_PRE_PROMOTION"
    assert Path(r["provenance"]["outputs"]["pdf"]).exists()
