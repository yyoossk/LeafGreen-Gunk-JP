import json,sys
def info(m):
    j=json.load(open(f'/home/claude/pret/data/maps/{m}/map.json'))
    print(m)
    print('  obj',[(o['x'],o['y'],o.get('script','?').split('_')[-1],o.get('flag','0') if o.get('flag','0')!='0' else '') for o in j['object_events']])
    print('  coord',[(c['x'],c['y'],c.get('script','?').split('_')[-1],c.get('var'),c.get('var_value')) for c in j.get('coord_events',[])][:14])
    print('  bg',[(b['x'],b['y'],b.get('script',b.get('item','?')).split('_')[-1]) for b in j.get('bg_events',[])][:10])
    print('  warps',[(w['x'],w['y'],w['dest_map'][4:]) for w in j['warp_events']])
for m in sys.argv[1:]:
    try: info(m)
    except Exception as e: print(m,'ERR',e)
