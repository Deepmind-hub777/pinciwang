import json
L=json.load(open('levels_out.json'))
FIX={'了':'le','卓':'zhuó','只':'zhǐ','罗':'luó'}
for l in L:
    for a in l['a']:
        if a['c'] in FIX: a['py']=FIX[a['c']]
json.dump(L,open('levels_out.json','w'),ensure_ascii=False,separators=(',',':'))
