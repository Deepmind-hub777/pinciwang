"""把 extra_v9.json 写进关卡数据：每关新增字段 x=[{c,k,py,au}]（额外字：看得出来的常用字，找到给金币，不计入过关）。
用法：python3 build_v9_apply.py <data目录> <main|qz> [--dry]"""
import json,re,glob,sys,os,collections
import gen
from pyau import py_of, au_of
from v4lib import types
from ids import desc
FQ=json.load(open('charfreq.json'))
EX=json.load(open(os.environ.get('EXF','extra_v10.json')))
D=sys.argv[1]; g=sys.argv[2]; dry='--dry' in sys.argv
AUD=os.path.join(D,'..','audio')
def nai(M):  # ⿸？X 且「？」= 一丿（ナ）：孩子眼里就是「厂」（灰/有/左/右/布/友）
    d=gen.D.get(M) or {}; mt=d.get('matches') or []
    if not (d.get('decomposition') or '').startswith('⿸？'): return None
    S=[i for i,m in enumerate(mt) if m is None or (m and m[0]==0)]; t=types(M)
    if len(S)==2 and t and t[S[0]]+t[S[1]]=='js': return S
def nai2(M):
    S=nai(M)
    if S: return S
    for T,SS in desc(M):
        s2=nai(T) if T in gen.G else None
        if s2 and len(SS)==len(gen.G[T]['strokes']): return [SS[i] for i in s2]
for M in list(EX):
    S=nai2(M)
    if S and not any(sorted(k)==sorted(S) for _,k in EX[M].get('厂',[])): EX[M].setdefault('厂',[]).insert(0,[0.05,S])
PY={}
for f in glob.glob('/workspace/pinciwang/data/main-*.js')+glob.glob('/workspace/hanzi-xueyuan/modules/pinci/data/qz-*.js'):
    for L in json.loads(re.search(r',(\[.*\])\);',open(f).read(),re.S).group(1)):
        for a in L['a']: PY.setdefault(a['c'],(a['py'],a['au']))
before=[];after=[];need=set();per={}
for f in sorted(glob.glob(os.path.join(D,g+'-*.js'))):
    src=open(f).read(); m=re.match(r'PCW_CHUNK\(("[a-z]+"),(\d+),(\[.*\])\);\s*$',src,re.S)
    Ls=json.loads(m.group(3))
    for L in Ls:
        core={a['c'] for a in L['a']}; off=0; X={}
        for ch in L['ch']:
            for T,lst in (EX.get(ch['c']) or {}).items():
                if T in core: continue
                for sc,c in lst: X.setdefault(T,{}).setdefault(tuple(sorted(i+off for i in c)),sc)
            off+=len(ch['st'])
        xs=[]
        for T,ks in X.items():
            kk=[list(k) for k,_ in sorted(ks.items(),key=lambda x:x[1])][:3]
            py,au=PY.get(T) or (py_of(T),None)
            if not au: au=au_of(T,py)
            if not os.path.exists(os.path.join(AUD,au+'.mp3')): need.add((T,py,au))
            xs.append({'c':T,'k':kk,'py':py,'au':au,'_n':len(gen.G[T]['strokes']),'_s':min(ks.values())})
        xs.sort(key=lambda a:(a['_n'],-FQ.get(a['c'],0)))  # 同笔画多个字时，先认更常用的（日先于曰）；再描一次认下一个
        for a in xs: a.pop('_n'); a.pop('_s')
        if xs: L['x']=xs
        else: L.pop('x',None)
        before.append(len(L['a'])); after.append(len(L['a'])+len(xs))
        per[L['n']]=(L['t'],''.join(a['c'] for a in L['a']),''.join(a['c'] for a in xs))
    if not dry: open(f,'w').write('PCW_CHUNK(%s,%s,%s);\n'%(m.group(1),m.group(2),json.dumps(Ls,ensure_ascii=False,separators=(',',':'))))
n=len(before)
print(g,'levels',n,'core',sum(before),'avg',round(sum(before)/n,2),'→ accepted',sum(after),'avg',round(sum(after)/n,2),
      'levels with extras',sum(1 for a,b in zip(before,after) if b>a),'extras',sum(after)-sum(before),'need audio',len(need))
json.dump(sorted(need),open('need_audio_v10_%s.json'%g,'w'),ensure_ascii=False)
json.dump(per,open('per_level_v10_%s.json'%g,'w'),ensure_ascii=False)
