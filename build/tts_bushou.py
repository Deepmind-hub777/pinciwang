import json,asyncio,os,subprocess
import edge_tts
VOICE="zh-CN-XiaoxiaoNeural"
jobs=json.load(open('bushou/audio_jobs.json'))
os.makedirs('/tmp/tts',exist_ok=True)
async def one(sem,c,py,text,fn):
    out='../audio/zi/'+fn
    if os.path.exists(out): return
    tmp='/tmp/tts/'+fn
    async with sem:
        for k in range(6):
            try: await edge_tts.Communicate(text,VOICE,rate="-10%").save(tmp); break
            except Exception: await asyncio.sleep(3)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-af',
      'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.08',
      '-ac','1','-ar','24000','-b:a','32k',out],check=True)
async def vo():
    lines={'changjianbushou':'常见部首！','shaojianbushou':'少见部首！','yihunbushou':'易混部首！','dadui':'答对了！','zailaiyici':'再看看~'}
    for k,t in lines.items():
        out='../audio/vo/'+k+'.mp3'
        if os.path.exists(out): continue
        tmp='/tmp/tts/vo_'+k+'.mp3'
        await edge_tts.Communicate(t,"zh-CN-XiaoyiNeural",rate="+0%").save(tmp)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
          '-ac','1','-ar','24000','-b:a','40k',out],check=True)
async def main():
    await vo()
    sem=asyncio.Semaphore(10)
    await asyncio.gather(*[one(sem,*j) for j in jobs])
    miss=[j for j in jobs if not os.path.exists('../audio/zi/'+j[3])]
    print('done; missing',len(miss))
asyncio.run(main())
