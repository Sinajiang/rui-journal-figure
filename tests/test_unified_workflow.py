from pathlib import Path
import sys, json, shutil, yaml

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"/"unified_workflow"
sys.path.insert(0,str(ROOT/"scripts"))

from run_top_journal_figure_workflow import Workflow
from workflow_utils import invalidate_downstream

def fresh(tmp_path):
    for name in ["manuscript.txt","source.tsv","workflow_project.yaml"]:
        shutil.copy2(FIX/name,tmp_path/name)
    return tmp_path/"workflow_project.yaml"

def test_workflow_ingest_passes(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    wf.ingest()
    assert wf.state["stages"]["INGEST"]["status"]=="COMPLETE"
    assert wf.state["current_state"]=="INGEST_COMPLETE"

def test_bundled_journal_profile_can_seed_contract(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    wf.ingest()
    wf.journal_contract()
    assert wf.state["stages"]["JOURNAL_CONTRACT"]["status"] in {"COMPLETE","COMPLETE_WITH_VERIFICATION_PENDING"}
    assert wf.state["current_state"]=="JOURNAL_CONTRACT_COMPLETE"

def test_benchmark_stops_for_agent_action_when_candidates_absent(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    wf.ingest(); wf.journal_contract(); wf.benchmark()
    assert wf.state["stages"]["BENCHMARK"]["status"]=="AGENT_ACTION_REQUIRED"
    assert wf.state["current_state"]=="BENCHMARK_SEARCH_REQUIRED"
    assert any(x["stage"]=="BENCHMARK" for x in wf.state["pending_agent_actions"])

def test_resume_stops_at_first_nonautomatable_gate(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    wf.resume()
    assert wf.state["current_state"]=="BENCHMARK_SEARCH_REQUIRED"

def test_reset_invalidates_downstream(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    wf.ingest(); wf.journal_contract()
    invalidate_downstream(wf.state,"INGEST")
    assert wf.state["stages"]["INGEST"]["status"]=="INVALIDATED"
    assert wf.state["stages"]["JOURNAL_CONTRACT"]["status"]=="INVALIDATED"

def test_dry_run_reports_next_incomplete(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    d=wf.dry_run()
    assert d["next_incomplete"]=="INGEST"

def test_real_data_automatically_binds_annotation_plan(tmp_path):
    cfg=fresh(tmp_path)
    wf=Workflow(cfg)
    out=wf.work/'07_REAL_DATA'; out.mkdir(parents=True,exist_ok=True)
    rfix=ROOT/'tests'/'fixtures'/'real_data_engine'
    shutil.copy2(rfix/'render_spec.yaml',out/'Figure_1_render_spec.yaml')
    for name in ['effects.tsv','dots.tsv','matrix.tsv']:
        shutil.copy2(rfix/name,out/name)
    plan={
      'version':'2.5.1',
      'figures':[{
        'figure_id':'Figure_1','shared_legend_clauses':['n=20 throughout unless otherwise indicated'],
        'panels':[{
          'panel_id':'P2','direct_annotations':[{'annotation_id':'A1','statistic_type':'effect_size','text':'logFC=0.42','direct_score':9.0,'claim_id':'C1'}],
          'legend_annotations':[],'suppressed_annotations':[],'density':{}
        }]
      }]
    }
    ap=tmp_path/'annotation_plan.json'; ap.write_text(json.dumps(plan),encoding='utf-8')
    wf.state.setdefault('artifacts',{})['ANNOTATION_INTELLIGENCE']={'plan':str(ap)}; wf.save()
    wf.real_data()
    annotated=out/'Figure_1_render_spec.annotated.yaml'
    assert annotated.exists()
    spec=yaml.safe_load(annotated.read_text(encoding='utf-8'))
    assert spec['annotation_intelligence']['decision_binding'] is True
    p2=next(p for p in spec['panels'] if p['panel_id']=='P2')
    assert p2['annotation_intelligence']['direct_annotations'][0]['annotation_id']=='A1'
    import fitz
    pdf=out/'Figure_1'/'Figure_1.pdf'
    text=''.join(page.get_text() for page in fitz.open(pdf))
    assert 'logFC=0.42' in text
    frag=out/'Figure_1'/'Figure_1_annotation_legend_fragment.txt'
    assert frag.exists() and 'n=20 throughout unless otherwise indicated' in frag.read_text(encoding='utf-8')
    assert wf.state['stages']['REAL_DATA']['status']=='COMPLETE'
