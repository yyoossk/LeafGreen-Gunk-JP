import json,sys,difflib
r=json.load(open(f'/tmp/walkst/{sys.argv[1]}_recs.json'))
e=[x[0] for x in r['en']]; j=[x[0] for x in r['jp']]
for op,a1,a2,b1,b2 in difflib.SequenceMatcher(None,e,j).get_opcodes():
    if op!='equal': print(op,'EN',e[a1:a2],'JP',j[b1:b2])
