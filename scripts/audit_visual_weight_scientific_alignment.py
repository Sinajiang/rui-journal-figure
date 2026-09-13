from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def load_contract(path: Path|None):
    if path: return yaml.safe_load(path.read_text(encoding='utf-8'))
    p=Path(__file__).resolve().parents[1]/'templates'/'contribution_scoring_contract.yaml'
    return yaml.safe_load(p.read_text(encoding='utf-8'))

def audit(plan_json: Path, contract: Path|None=None):
    p=json.loads(plan_json.read_text(encoding='utf-8')); c=load_contract(contract); r=c['visual_weight_rules']
    review=[]; blocking=[]
    for fig in p.get('figures',[]):
        panels=fig.get('panels',[])
        for x in panels:
            role=(x.get('role') or '').lower(); area=float(x['normalized_area_share']); score=float(x['contribution_score']); density=float(x['visual_density'])
            if x.get('visual_weight_class')=='ANCHOR' and area < float(r['anchor_floor_share'])-1e-6:
                blocking.append({'type':'ANCHOR_AREA_TOO_SMALL','figure':fig['figure'],'panel_id':x['panel_id'],'area':area})
            if role in {'workflow','provenance','design'} and area > float(r['workflow_cap_share'])+1e-6:
                review.append({'type':'WORKFLOW_AREA_TOO_LARGE','figure':fig['figure'],'panel_id':x['panel_id'],'area':area})
            if density>=float(r['dense_panel_threshold']) and area<float(r['dense_panel_min_share'])-1e-6:
                review.append({'type':'DENSE_PANEL_UNDERSIZED','figure':fig['figure'],'panel_id':x['panel_id'],'area':area,'density':density})
        # pairwise inversion
        tol=float(r['contribution_inversion_tolerance'])
        for i,a in enumerate(panels):
            for b in panels[i+1:]:
                sa=float(a['contribution_score']); sb=float(b['contribution_score']); aa=float(a['normalized_area_share']); ab=float(b['normalized_area_share'])
                if sa >= sb+tol and aa+0.04 < ab:
                    review.append({'type':'CONTRIBUTION_AREA_INVERSION','figure':fig['figure'],'higher_panel':a['panel_id'],'lower_panel':b['panel_id'],'higher_score':sa,'lower_score':sb,'higher_area':aa,'lower_area':ab})
                elif sb >= sa+tol and ab+0.04 < aa:
                    review.append({'type':'CONTRIBUTION_AREA_INVERSION','figure':fig['figure'],'higher_panel':b['panel_id'],'lower_panel':a['panel_id'],'higher_score':sb,'lower_score':sa,'higher_area':ab,'lower_area':aa})
    return {'blocking':blocking,'review':review,'pass':len(blocking)==0}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('visual_weight_plan'); ap.add_argument('--contract'); ap.add_argument('--out')
    a=ap.parse_args(); res=audit(Path(a.visual_weight_plan),Path(a.contract) if a.contract else None)
    txt=json.dumps(res,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding='utf-8')
