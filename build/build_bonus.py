import json, gen
COMP={'亻':'单人旁','氵':'三点水','扌':'提手旁','忄':'竖心旁','艹':'草字头','宀':'宝盖头','冖':'秃宝盖','亠':'京字头','勹':'包字框','冂':'同字框','匚':'三框儿','厶':'私字儿','攵':'反文旁','礻':'示字旁','衤':'衣字旁','灬':'四点底','讠':'言字旁','饣':'食字旁','纟':'绞丝旁','钅':'金字旁','阝':'耳刀旁','刂':'立刀旁','卩':'单耳刀','廴':'建之旁','辶':'走之底','疒':'病字旁','罒':'四字头','癶':'登字头','彡':'三撇儿','夂':'折文','廾':'弄字底','冫':'两点水','囗':'方框','凵':'凶字框','爫':'爪字头','耂':'老字头','犭':'反犬旁','彳':'双人旁','龹':'卷字头','㔾':'卷字底','丬':'将字旁','覀':'西字头','虍':'虎字头','⺮':'竹字头','彐':'横山','丷':'倒八','屮':'屮字'}
COMP={k:v for k,v in COMP.items() if k in gen.G}
main=json.load(open('main_levels.json'))
cands=[l['t'] for l in main if len(l['t'])==1]
out=[]
for c in cands:
    N=len(gen.G[c]['medians']); found=[]
    for T,nm in COMP.items():
        if len(gen.G[T]['medians'])>=N: continue
        r=gen.match(T,c,thr=0.2,maxnodes=20000)
        good=[]
        for _,k in r:
            j=gen.judge(T,c,k)
            if j and j[0]<0.045 and j[1]<0.1: good.append((j[0],k))
        if good:
            good.sort(); found.append((good[0][0],T,[k for _,k in good][:6]))
    if len(found)>=3: out.append((c,found))
print('bonus candidates',len(out))
# prefer variety: sort by number of components desc, then strokes
out.sort(key=lambda x:(-len(x[1]),len(gen.G[x[0]]['medians'])))
sel=out[:90]
sel.sort(key=lambda x:(len(x[1]),len(gen.G[x[0]]['medians'])))
levels=[]
for i,(c,found) in enumerate(sel):
    A=[{'c':T,'k':[list(map(int,k)) for k in ks],'nm':COMP[T],'py':(gen.D.get(T,{}).get('pinyin') or [''])[0],'au':'bu/%04x'%ord(T)} for sc,T,ks in sorted(found)[:8]]
    levels.append({'n':i+1,'t':c,'ch':[{'c':c,'st':gen.G[c]['strokes']}],'a':A})
json.dump(levels,open('bonus_levels.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump(COMP,open('comp_names.json','w'),ensure_ascii=False)
print('bonus levels',len(levels),' '.join(l['t']+str(len(l['a'])) for l in levels[:30]))
