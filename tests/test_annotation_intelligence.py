from pathlib import Path
import sys,json,yaml
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests/fixtures/annotation_intelligence'
sys.path.insert(0,str(ROOT/'scripts'))
from derive_annotation_legend_plan import derive
from audit_annotation_legend_plan import audit
from apply_annotation_plan_to_render_spec import apply

def make_plan(tmp_path):
    d=derive(FIX/'inventory.tsv',benchmark_path=FIX/'benchmark.json',hierarchy_path=FIX/'hierarchy.json')
    p=tmp_path/'plan.json'; p.write_text(json.dumps(d),encoding='utf-8')
    return d,p

def items(d):
    return {x['annotation_id']:x for f in d['figures'] for p in f['panels'] for key in ['direct_annotations','legend_annotations','suppressed_annotations'] for x in p[key]}

def test_effect_size_direct_and_raw_p_suppressed_when_fdr_exists(tmp_path):
    d,p=make_plan(tmp_path); m=items(d)
    assert m['A_EFFECT']['disposition']=='DIRECT'
    assert m['A_FDR']['disposition'] in {'DIRECT','LEGEND'}
    assert m['A_P']['disposition']=='SUPPRESS'
    assert 'adjusted_significance_available_for_same_inferential_unit' in m['A_P']['reasons']

def test_graphically_encoded_ci_and_direction_are_suppressed(tmp_path):
    d,p=make_plan(tmp_path); m=items(d)
    assert m['A_CI']['disposition']=='SUPPRESS'
    assert 'ci_already_graphically_encoded' in m['A_CI']['reasons']
    assert m['A_DIR']['disposition']=='SUPPRESS'

def test_n_and_method_move_to_legend(tmp_path):
    d,p=make_plan(tmp_path); m=items(d)
    assert m['A_N']['disposition']=='SUPPRESS'
    assert 'collapsed_to_shared_legend_clause' in m['A_N']['reasons']
    assert any('n=81' in x for f in d['figures'] for x in f['shared_legend_clauses'])
    assert m['A_METHOD']['disposition']=='LEGEND'

def test_nonencoded_direction_can_survive(tmp_path):
    d,p=make_plan(tmp_path); m=items(d)
    assert m['B_DIR']['disposition'] in {'DIRECT','LEGEND'}

def test_audit_passes_safe_plan(tmp_path):
    d,p=make_plan(tmp_path)
    r=audit(p)
    assert r['pass'] is True
    assert not r['blocking']

def test_apply_plan_injects_render_spec(tmp_path):
    d,p=make_plan(tmp_path); out=tmp_path/'render.yaml'
    spec=apply(FIX/'render_spec.yaml',p,out)
    p1=spec['panels'][0]['annotation_intelligence']
    assert any(x['annotation_id']=='A_EFFECT' for x in p1['direct_annotations'])
    assert 'A_P' in p1['suppressed_annotation_ids']
    assert spec['annotation_intelligence']['shared_legend_clauses']

def test_direct_budget_rebalances_to_legend(tmp_path):
    h=json.loads((FIX/'hierarchy.json').read_text()); h['figures'][0]['panels'][0]['max_annotation_lines']=1
    hp=tmp_path/'h.json'; hp.write_text(json.dumps(h))
    d=derive(FIX/'inventory.tsv',benchmark_path=FIX/'benchmark.json',hierarchy_path=hp)
    p1=next(p for f in d['figures'] for p in f['panels'] if p['panel_id']=='P1')
    assert len(p1['direct_annotations'])<=1
    assert any(x['type']=='DIRECT_ANNOTATION_BUDGET_EXCEEDED_REBALANCED' for x in d['review_flags'])

def test_workflow_stage_registered():
    from workflow_utils import STAGE_ORDER
    assert 'ANNOTATION_INTELLIGENCE' in STAGE_ORDER
    assert STAGE_ORDER.index('VISUAL_HIERARCHY') < STAGE_ORDER.index('ANNOTATION_INTELLIGENCE') < STAGE_ORDER.index('PROTOTYPE')

def _write_inventory(path, rows):
    import csv
    fields=["figure_id","panel_id","annotation_id","claim_id","statistic_type","label","value","lower","upper","interval_level","effect_metric","null_reference","display_text","inferential_unit","claim_importance","statistical_necessity","panel_tier","primary_test","multiplicity_applies","multiplicity_adjusted","uncertainty_encoded","estimate_encoded","direction_encoded","n_varies","repeated_across_panels","exact_value_required","redundancy_group","benchmark_direct_rate","benchmark_legend_rate","notes"]
    with path.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields,delimiter='\t'); w.writeheader()
        for r in rows:
            base={k:"" for k in fields}; base.update(r); w.writerow(base)

def test_adjusted_significance_suppression_is_panel_scoped(tmp_path):
    inv=tmp_path/'inv.tsv'
    _write_inventory(inv,[
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"FDR1","claim_id":"C1","statistic_type":"fdr","value":"0.02","inferential_unit":"U1","claim_importance":"4","statistical_necessity":"high","panel_tier":"ANCHOR","multiplicity_applies":"true"},
        {"figure_id":"Figure_1","panel_id":"P2","annotation_id":"P2RAW","claim_id":"C2","statistic_type":"p_value","value":"0.01","inferential_unit":"U1","claim_importance":"4","statistical_necessity":"high","panel_tier":"ANCHOR","multiplicity_applies":"true"},
    ])
    d=derive(inv); m=items(d)
    assert m['P2RAW']['disposition'] != 'SUPPRESS' or 'adjusted_significance_available_for_same_inferential_unit' not in m['P2RAW']['reasons']

def test_structured_ci_and_effect_metric_formatting(tmp_path):
    inv=tmp_path/'inv.tsv'
    _write_inventory(inv,[
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"E1","claim_id":"C1","statistic_type":"effect_size","label":"OR","value":"1.234","effect_metric":"OR","claim_importance":"5","statistical_necessity":"required","panel_tier":"ANCHOR","primary_test":"true"},
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"CI1","claim_id":"C1","statistic_type":"ci","label":"95% CI","lower":"1.01","upper":"1.49","interval_level":"95","claim_importance":"5","statistical_necessity":"required","panel_tier":"ANCHOR","primary_test":"true"},
    ])
    d=derive(inv); m=items(d)
    assert m['E1']['text']=='OR=1.2'
    assert m['CI1']['text']=='95% CI 1.01–1.5'

def test_encoded_effect_is_deprioritized_when_not_claim_critical(tmp_path):
    inv=tmp_path/'inv.tsv'
    _write_inventory(inv,[
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"E1","claim_id":"C1","statistic_type":"effect_size","value":"0.42","claim_importance":"2","statistical_necessity":"moderate","panel_tier":"SUPPORT","estimate_encoded":"true"},
    ])
    d=derive(inv); m=items(d)
    assert 'effect_magnitude_already_visually_encoded' in m['E1']['reasons']
    assert m['E1']['disposition'] in {'LEGEND','SUPPRESS'}

def test_audit_blocks_invalid_values_and_unresolved_legend_restructure(tmp_path):
    plan={
      "version":"2.5.1","review_flags":[{"type":"LEGEND_BUDGET_REQUIRES_RESTRUCTURE","figure_id":"Figure_1","panel_id":"P1","budget":1,"unresolved":1}],
      "figures":[{"figure_id":"Figure_1","panels":[{"panel_id":"P1","direct_annotations":[{"annotation_id":"BADP","claim_id":"C1","statistic_type":"p_value","raw_value":"1.2","disposition":"DIRECT","statistical_necessity":"high","reasons":[],"primary_test":True}],"legend_annotations":[],"suppressed_annotations":[],"density":{"direct_count":1,"direct_budget":2}}]}]
    }
    pp=tmp_path/'plan.json'; pp.write_text(json.dumps(plan),encoding='utf-8')
    r=audit(pp)
    types={x['type'] for x in r['blocking']}
    assert 'INVALID_SIGNIFICANCE_VALUE' in types
    assert 'UNRESOLVED_LEGEND_RESTRUCTURE_REQUIRED' in types
    assert r['pass'] is False

def test_apply_plan_is_figure_scoped_for_duplicate_panel_ids(tmp_path):
    import yaml
    plan={"version":"2.5.1","figures":[
      {"figure_id":"Figure_1","panels":[{"panel_id":"P1","direct_annotations":[{"annotation_id":"F1","statistic_type":"effect_size","text":"A","direct_score":9}],"legend_annotations":[],"suppressed_annotations":[],"density":{}}],"shared_legend_clauses":[]},
      {"figure_id":"Figure_2","panels":[{"panel_id":"P1","direct_annotations":[{"annotation_id":"F2","statistic_type":"effect_size","text":"B","direct_score":9}],"legend_annotations":[],"suppressed_annotations":[],"density":{}}],"shared_legend_clauses":[]}
    ]}
    pp=tmp_path/'plan.json'; pp.write_text(json.dumps(plan),encoding='utf-8')
    sp=tmp_path/'spec.yaml'; sp.write_text(yaml.safe_dump({"figure":{"id":"Figure_1"},"panels":[{"panel_id":"P1"}]}),encoding='utf-8')
    out=tmp_path/'out.yaml'; spec=apply(sp,pp,out)
    ids=[x['annotation_id'] for x in spec['panels'][0]['annotation_intelligence']['direct_annotations']]
    assert ids==['F1']
    assert spec['annotation_intelligence']['decision_binding'] is True

def test_required_repeated_n_can_collapse_to_shared_legend(tmp_path):
    inv=tmp_path/'inv.tsv'
    _write_inventory(inv,[
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"N1","claim_id":"C1","statistic_type":"n","value":"81","claim_importance":"4","statistical_necessity":"required","panel_tier":"ANCHOR","repeated_across_panels":"true","redundancy_group":"NALL"},
        {"figure_id":"Figure_1","panel_id":"P2","annotation_id":"N2","claim_id":"C2","statistic_type":"n","value":"81","claim_importance":"4","statistical_necessity":"required","panel_tier":"SUPPORT","repeated_across_panels":"true","redundancy_group":"NALL"},
    ])
    d=derive(inv); pp=tmp_path/'plan.json'; pp.write_text(json.dumps(d),encoding='utf-8')
    r=audit(pp)
    assert r['pass'] is True
    assert any('n=81 throughout unless otherwise indicated'==x for f in d['figures'] for x in f['shared_legend_clauses'])


def test_null_boundary_precision_is_preserved(tmp_path):
    inv=tmp_path/'inv.tsv'
    _write_inventory(inv,[
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"E1","claim_id":"C1","statistic_type":"effect_size","label":"OR","value":"1.01","effect_metric":"OR","claim_importance":"5","statistical_necessity":"required","panel_tier":"ANCHOR"},
        {"figure_id":"Figure_1","panel_id":"P1","annotation_id":"CI1","claim_id":"C1","statistic_type":"ci","label":"95% CI","lower":"1.01","upper":"1.49","interval_level":"95","effect_metric":"OR","claim_importance":"5","statistical_necessity":"required","panel_tier":"ANCHOR"},
    ])
    d=derive(inv); m=items(d)
    assert m['E1']['text']=='OR=1.01'
    assert m['CI1']['text'].startswith('95% CI 1.01–')
