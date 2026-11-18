#!/usr/bin/env python3
# Walk-through test: runs the same plan on the EN Gunk original and on the JP port, saves states per segment
# and writes side-by-side comparison sheets (EN left, JP right) to /tmp/walk/cmp_<segment>.png
import sys, os, json
sys.path.insert(0, '/home/claude/tools')
from walker import *

ST = '/tmp/walkst'
os.makedirs(ST, exist_ok=True)

def run_segment(name, prev, plan):
    recs = {}
    info = {}
    for k in ('en', 'jp'):
        src = f'{ST}/{prev}_{k}.ss'
        if isinstance(prev, dict): src = f'{ST}/{prev[k]}_{k}.ss'
        g = Game(k, src)
        g.run(5)
        if k == 'en' or os.environ.get('BOOST_ALL'): g.boost()
        rec = []
        try:
            plan(g, rec)
        except Exception as e:
            rec.append((f'ERROR {e!r}', [g.snap('error')]))
        g.save(f'{ST}/{name}_{k}.ss'); g.run(1)
        info[k] = g.pos()
        recs[k] = rec
        g.close()
    json.dump(recs, open(f'{ST}/{name}_recs.json', 'w'))
    out = compare(recs['en'], recs['jp'], f'/tmp/walk/cmp_{name}.png')
    compact(recs['en'], recs['jp'], f'/tmp/walk/cpt_{name}.png')
    print(name, 'en', info['en'], 'jp', info['jp'], 'rows', len(recs['en']), len(recs['jp']))
    return recs

if __name__ == '__main__':
    pass
