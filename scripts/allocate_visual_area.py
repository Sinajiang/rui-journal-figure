from __future__ import annotations
import argparse, json, math
from pathlib import Path
import yaml

def load_contract(path: Path|None):
    if path: return yaml.safe_load(path.read_text(encoding='utf-8'))
    p=Path(__file__).resolve().parents[1]/'templates'/'contribution_scoring_contract.yaml'
    return yaml.safe_load(p.read_text(encoding='utf-8'))

def normalize_with_caps(raw, mins, maxs, iterations=20):
    n=len(raw)
    if n==0: return []
    s=sum(raw) or 1.0
    x=[r/s for r in raw]
    for _ in range(iterations):
        fixed=[False]*n
        for i in range(n):
            if x[i] < mins[i]: x[i]=mins[i]; fixed[i]=True
            elif x[i] > maxs[i]: x[i]=maxs[i]; fixed[i]=True
        total=sum(x)
        if abs(total-1)<1e-8: break
        free=[i for i in range(n) if not fixed[i]]
        if not free: break
        free_total=sum(x[i] for i in free) or 1.0
        delta=1-total
        for i in free:
            x[i]+=delta*(x[i]/free_total)
    total=sum(x) or 1
    return [max(0,v/total) for v in x]

def allocate(candidate_json: Path, contribution_json: Path, contract: Path|None=None):
    cand=json.loads(candidate_json.read_text(encoding='utf-8'))
    cont=json.loads(contribution_json.read_text(encoding='utf-8'))
    c=load_contract(contract); rules=c['visual_weight_rules']
    cmap={x['panel_id']:x for x in cont['panels']}
    figures=[]
    for fig in cand.get('figures',[]):
        pids=fig.get('panels',[])
        vals=[]; mins=[]; maxs=[]
        for pid in pids:
            x=cmap[pid]
            # nonlinear contribution + density need
            raw=(max(x['scientific_contribution_score'],0.1)**1.25)*(1+0.035*x['visual_density'])
            vals.append(raw)
            role=(x.get('role') or '').lower()
            mn=float(rules['minimum_panel_share']); mx=float(rules['maximum_panel_share'])
            if x['visual_weight_class']=='ANCHOR': mn=max(mn,float(rules['anchor_floor_share']))
            if role in {'workflow','provenance','design'}: mx=min(mx,float(rules['workflow_cap_share']))
            if x['visual_density']>=float(rules['dense_panel_threshold']): mn=max(mn,float(rules['dense_panel_min_share']))
            mins.append(mn); maxs.append(mx)
        shares=normalize_with_caps(vals,mins,maxs)
        # layout strategy
        order=sorted(range(len(pids)),key=lambda i:shares[i],reverse=True)
        dominant=(len(order)>1 and shares[order[0]] >= 1.28*shares[order[1]]) or (len(order)==1)
        strategy='dominant_anchor' if dominant else 'balanced_grid'
        panels=[]
        for i,pid in enumerate(pids):
            x=cmap[pid]
            panels.append({
                'panel_id':pid,
                'contribution_score':x['scientific_contribution_score'],
                'visual_weight_class':x['visual_weight_class'],
                'visual_density':x['visual_density'],
                'normalized_area_share':round(shares[i],4),
                'layout_priority':order.index(i)+1,
                'role':x.get('role')
            })
        figures.append({'figure':fig.get('figure'),'theme':fig.get('theme'),'layout_strategy':strategy,'panels':panels})
    return {'figures':figures,'rules':rules}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('candidate_json'); ap.add_argument('contribution_json'); ap.add_argument('--contract'); ap.add_argument('--out')
    a=ap.parse_args(); r=allocate(Path(a.candidate_json),Path(a.contribution_json),Path(a.contract) if a.contract else None)
    txt=json.dumps(r,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding='utf-8')
