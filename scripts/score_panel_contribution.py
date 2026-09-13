from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import yaml
from architecture_utils import load_panels, redundancy_score

def load_contract(path: Path|None):
    if path:
        return yaml.safe_load(path.read_text(encoding='utf-8'))
    p=Path(__file__).resolve().parents[1]/'templates'/'contribution_scoring_contract.yaml'
    return yaml.safe_load(p.read_text(encoding='utf-8'))

def classify(score, role):
    r=(role or '').lower()
    if r in {'workflow','provenance','design'} and score < 8.5:
        return 'PROVENANCE'
    if score >= 8.5: return 'ANCHOR'
    if score >= 7.0: return 'MAJOR_SUPPORT'
    if score >= 5.5: return 'SUPPORT'
    if score >= 4.0: return 'CONTEXT'
    return 'SUPPLEMENTARY_CANDIDATE'

def score(inventory: Path, contract: Path|None=None):
    panels=load_panels(inventory)
    c=load_contract(contract)
    w=c['weights']; role_scores=c['role_directness_scores']
    # strongest redundancy partner for penalty
    max_red={p['panel_id']:0.0 for p in panels}
    for i,a in enumerate(panels):
        for b in panels[i+1:]:
            s=redundancy_score(a,b)
            max_red[a['panel_id']]=max(max_red[a['panel_id']],s)
            max_red[b['panel_id']]=max(max_red[b['panel_id']],s)
    out=[]
    for p in panels:
        role=(p.get('role') or '').lower()
        direct=float(role_scores.get(role,5.0))
        density_need=min(10.0,float(p.get('visual_density',0)))
        vals={
            'claim_priority':float(p.get('priority',0)),
            'contribution_score':float(p.get('contribution_score',0)),
            'source_traceability':float(p.get('source_traceability_score',0)),
            'benchmark_support':float(p.get('benchmark_support_score',0)),
            'role_directness':direct,
            'density_need':density_need,
        }
        num=sum(vals[k]*float(w[k]) for k in vals)
        den=sum(float(w[k]) for k in vals)
        base=num/den if den else 0
        penalty=float(w.get('redundancy_penalty',1.0))*10*max_red[p['panel_id']]*0.18
        final=max(0.0,min(10.0,base-penalty))
        out.append({
            'panel_id':p['panel_id'],
            'theme':p.get('theme'),
            'role':p.get('role'),
            'scientific_contribution_score':round(final,3),
            'visual_weight_class':classify(final,p.get('role')),
            'max_redundancy_score':round(max_red[p['panel_id']],3),
            'visual_density':float(p.get('visual_density',0)),
            'must_main':bool(p.get('must_main')),
            'current_location':p.get('current_location'),
            'components':vals,
        })
    return {'panels':out,'contract':c}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('inventory'); ap.add_argument('--contract'); ap.add_argument('--out')
    a=ap.parse_args(); r=score(Path(a.inventory),Path(a.contract) if a.contract else None)
    txt=json.dumps(r,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding='utf-8')
