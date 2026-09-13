from pathlib import Path
import sys, json

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests'/'fixtures'/'contribution_optimizer'
sys.path.insert(0,str(ROOT/'scripts'))

from score_panel_contribution import score
from allocate_visual_area import allocate
from audit_visual_weight_scientific_alignment import audit
from recommend_contribution_actions import recommend

def test_anchor_scores_higher_than_workflow():
    r=score(FIX/'panels.tsv')
    m={x['panel_id']:x for x in r['panels']}
    assert m['P2']['scientific_contribution_score'] > m['P1']['scientific_contribution_score']
    assert m['P2']['visual_weight_class']=='ANCHOR'

def test_area_allocator_gives_anchor_more_area(tmp_path):
    c=score(FIX/'panels.tsv'); cp=tmp_path/'c.json'; cp.write_text(json.dumps(c),encoding='utf-8')
    r=allocate(FIX/'candidate.json',cp)
    f1=r['figures'][0]; m={x['panel_id']:x for x in f1['panels']}
    assert m['P2']['normalized_area_share'] > m['P1']['normalized_area_share']
    assert m['P2']['normalized_area_share'] >= 0.30

def test_visual_alignment_audit_passes_generated_plan(tmp_path):
    c=score(FIX/'panels.tsv'); cp=tmp_path/'c.json'; cp.write_text(json.dumps(c),encoding='utf-8')
    p=allocate(FIX/'candidate.json',cp); pp=tmp_path/'p.json'; pp.write_text(json.dumps(p),encoding='utf-8')
    r=audit(pp)
    assert r['pass'] is True

def test_redundant_low_value_panel_is_not_promoted():
    c=score(FIX/'panels.tsv'); tmp=FIX/'_tmp_contribution.json'; tmp.write_text(json.dumps(c),encoding='utf-8')
    try:
        r=recommend(tmp); m={x['panel_id']:x for x in r['actions']}
        assert m['P5']['action'] in {'MERGE_OR_DEMOTE','DEMOTE_SUPPLEMENTARY','KEEP_OR_COMPACT'}
    finally:
        tmp.unlink(missing_ok=True)
