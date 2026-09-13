from __future__ import annotations
import argparse, json
from pathlib import Path

def recommend(contribution_json: Path):
    c=json.loads(contribution_json.read_text(encoding='utf-8'))
    out=[]
    for p in c['panels']:
        score=float(p['scientific_contribution_score']); cls=p['visual_weight_class']; cur=(p.get('current_location') or '').lower(); red=float(p.get('max_redundancy_score',0)); must=bool(p.get('must_main'))
        if must:
            action='KEEP_MAIN' if cur=='main' else 'PROMOTE_MAIN'; reason='must-main evidence'
        elif cls=='ANCHOR':
            action='KEEP_MAIN' if cur=='main' else 'PROMOTE_MAIN'; reason='anchor-level contribution'
        elif score>=7:
            action='KEEP_MAIN' if cur=='main' else 'PROMOTE_MAIN'; reason='major supporting contribution'
        elif red>=0.72:
            action='MERGE_OR_DEMOTE'; reason=f'high redundancy {red:.2f}'
        elif score<4.5:
            action='DEMOTE_SUPPLEMENTARY'; reason='low incremental contribution'
        else:
            action='KEEP_OR_COMPACT'; reason='support/context evidence'
        out.append({'panel_id':p['panel_id'],'action':action,'reason':reason,'contribution_score':score,'visual_weight_class':cls})
    return {'actions':out}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('contribution_json'); ap.add_argument('--out'); a=ap.parse_args()
    r=recommend(Path(a.contribution_json)); txt=json.dumps(r,indent=2,ensure_ascii=False); print(txt)
    if a.out: Path(a.out).write_text(txt,encoding='utf-8')
