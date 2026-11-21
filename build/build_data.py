import json, os, gen
from pypinyin import pinyin, Style
cur=json.load(open('levels_out.json'))          # existing 130 levels (keep n, answers, pinyin, au)
mc=json.load(open('more_cache.json'))
res=mc['res']
FIX={'肋':'lèi','茸':'róng','勒':'lè','了':'le','卓':'zhuó','只':'zhǐ','罗':'luó','卜':'bǔ','子':'zǐ'}
def py_of(c):
    if c in FIX: return FIX[c]
    mm=[p for p in (gen.D.get(c,{}).get('pinyin') or []) if any(ord(x)>127 for x in p)]
    d=pinyin(c,style=Style.TONE)[0][0]
    if d in mm or not mm: return d
    return mm[0]
from tts import pinyin_to_num
def au_of(c,py): return 'zi/%04x_%s'%(ord(c),pinyin_to_num(py))
def make_level(n,c,sols,cap):
    N=len(gen.G[c]['strokes'])
    A=[{'c':T,'k':[list(map(int,k)) for k in ks][:8],'sc':sc} for sc,T,ks in sols]
    A=sorted(A,key=lambda a:a['sc'])[:cap-1]
    A.append({'c':c,'k':[list(range(N))],'sc':0})
    A.sort(key=lambda a:(a['sc']==0,len(gen.G[a['c']]['medians'])))
    for a in A:
        a.pop('sc'); a['py']=py_of(a['c']); a['au']=au_of(a['c'],a['py'])
    return {'n':n,'t':c,'ch':[{'c':c,'st':gen.G[c]['strokes']}],'a':A}
main=[]
for l in cur:
    for a in l['a']: a['au']='zi/'+a['au'] if not a['au'].startswith('zi/') else a['au']
    main.append(l)
n=len(main)
for c in mc['order']:
    s=res.get(c)
    if not s or len(s)<2: continue
    n+=1; main.append(make_level(n,c,s,min(18,max(4,6+n//40))))
fill=[c for c in mc['filler'] if res.get(c) and len(res[c])>=4]
fill.sort(key=lambda c:len(gen.G[c]['medians']))
for c in fill:
    if len(main)>=900: break
    n+=1; main.append(make_level(n,c,res[c],18))
print('main levels',len(main))
json.dump(main,open('main_levels.json','w'),ensure_ascii=False,separators=(',',':'))
