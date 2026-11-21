import sys; sys.argv=['x']
exec(open('verify4.py').read().split("TH=0.6")[0])
import json
V=json.load(open('verify4.json'))
print('乐:',V.get('乐'))
async def run():
    items=[(c,c) for c in '且了北哈大寸弄打某活白草']+[('行','行'),('长','长'),('着','着'),('乐','乐')]
    for c,T in items:
        alts={}
        for r in het(c):
            hs=homs(r,{c})[:3]
            if hs: alts[r]=hs
        await synall([T]+[h for v in alts.values() for h in v])
        out={r:round(min(dist(F(T),F(h)) for h in hs),2) for r,hs in alts.items()}
        print(c,'readings→min dist',out,{r:hs[0] for r,hs in alts.items()})
asyncio.run(run())
