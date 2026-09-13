from pathlib import Path
import sys,json,yaml
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests/fixtures/visual_hierarchy"
sys.path.insert(0,str(ROOT/"scripts"))
from solve_layouts_from_visual_weight_plan import solve
from derive_visual_hierarchy import derive
from audit_label_density_budget import audit as audit_labels
from audit_visual_hierarchy_consistency import audit as audit_h
from apply_visual_hierarchy_to_render_spec import apply

def build(tmp_path):
    layouts=solve(FIX/"visual_weight_plan.json",FIX/"layout_grammar.json",180,120)
    lp=tmp_path/"layouts.json"; lp.write_text(json.dumps(layouts))
    h=derive(lp)
    hp=tmp_path/"hierarchy.json"; hp.write_text(json.dumps(h))
    return layouts,h,hp

def test_hierarchy_assigns_anchor_and_uniform_panel_label(tmp_path):
    layouts,h,hp=build(tmp_path)
    p={x["panel_id"]:x for f in h["figures"] for x in f["panels"]}
    assert p["P1"]["tier"]=="ANCHOR"
    assert h["panel_label_size_pt"]==8.0
    assert p["P1"]["marker_size_pt"] > p["P3"]["marker_size_pt"]

def test_physical_budget_tracks_panel_size(tmp_path):
    layouts,h,hp=build(tmp_path)
    p={x["panel_id"]:x for f in h["figures"] for x in f["panels"]}
    assert p["P1"]["panel_width_mm"] > 80
    assert p["P1"]["max_chars_per_annotation_line"] > 20
    assert min(p["P1"]["tick_label_size_pt"],p["P2"]["tick_label_size_pt"]) >= 5.5

def test_label_density_flags_overloaded_panel(tmp_path):
    layouts,h,hp=build(tmp_path)
    r=audit_labels(hp,FIX/"labels.tsv")
    assert r["pass"] is True
    assert any(x["panel_id"]=="P3" for x in r["review"])

def test_hierarchy_consistency_passes_default(tmp_path):
    layouts,h,hp=build(tmp_path)
    r=audit_h(hp)
    assert r["pass"] is True
    assert not any(x["type"]=="MARKER_HIERARCHY_INVERSION" for x in r["review"])

def test_hierarchy_consistency_detects_tampered_inversion(tmp_path):
    layouts,h,hp=build(tmp_path)
    p={x["panel_id"]:x for f in h["figures"] for x in f["panels"]}
    p["P1"]["marker_size_pt"]=2.5
    hp.write_text(json.dumps(h))
    r=audit_h(hp)
    assert any(x["type"]=="MARKER_HIERARCHY_INVERSION" for x in r["review"])

def test_apply_hierarchy_injects_render_spec(tmp_path):
    layouts,h,hp=build(tmp_path)
    out=tmp_path/"render_with_hierarchy.yaml"
    spec=apply(FIX/"render_spec.yaml",hp,out)
    assert out.exists()
    assert spec["panels"][0]["visual_hierarchy"]["tier"]=="ANCHOR"
    assert "marker_size_pt" in spec["panels"][0]["visual_hierarchy"]

def test_workflow_stage_registered():
    from workflow_utils import STAGE_ORDER
    assert "VISUAL_HIERARCHY" in STAGE_ORDER
    assert STAGE_ORDER.index("LAYOUT_GRAMMAR") < STAGE_ORDER.index("VISUAL_HIERARCHY") < STAGE_ORDER.index("PROTOTYPE")
