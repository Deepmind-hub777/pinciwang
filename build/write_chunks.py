import json, os, glob
os.makedirs('../data',exist_ok=True)
for f in glob.glob('../data/*.js'): os.remove(f)
idx={}
for g in ['main','bonus']:
    L=json.load(open(g+'_levels.json'))
    idx[g]=[[l['n'],l['t'],len(l['a']),sum(len(c['st']) for c in l['ch'])] for l in L]
    for k in range(0,len(L),50):
        with open('../data/%s-%02d.js'%(g,k//50),'w') as fp:
            fp.write('PCW_CHUNK(%s,%d,%s);\n'%(json.dumps(g),k,json.dumps(L[k:k+50],ensure_ascii=False,separators=(',',':'))))
with open('../data/index.js','w') as fp:
    fp.write('/* 关卡索引：[关号, 母字, 隐藏数, 笔画数]。笔画来自 Make Me a Hanzi，隐藏字由 build/ 脚本几何匹配生成 */\nwindow.PCW_INDEX=%s;\n'%json.dumps(idx,ensure_ascii=False,separators=(',',':')))
print({g:len(v) for g,v in idx.items()})
