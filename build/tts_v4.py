import json, asyncio, os, subprocess
import edge_tts
VOICE="zh-CN-XiaoxiaoNeural"
OV=json.load(open('tts_override.json'))
COMP=json.load(open('comp_names.json'))
async def synth(text,out,rate="-10%"):
    tmp='/tmp/tts/'+os.path.basename(out)
    for k in range(6):
        try: await edge_tts.Communicate(text,VOICE,rate=rate).save(tmp); break
        except Exception: await asyncio.sleep(3)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-af',
      'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.08',
      '-ac','1','-ar','24000','-b:a','32k',out],check=True)
async def main():
    os.makedirs('/tmp/tts',exist_ok=True)
    jobs=[]
    for c,py,au in json.load(open('newaudio_v4.json')):
        out='../audio/'+au+'.mp3'
        if not os.path.exists(out): jobs.append(synth(OV.get(c,c),out))
    for l in json.load(open('bonus_levels_v4.json')):
        for a in l['a']:
            out='../audio/'+a['au']+'.mp3'
            if not os.path.exists(out): jobs.append(synth(a['nm'],out,rate="-5%"))
    await asyncio.gather(*jobs); print('made',len(jobs))
asyncio.run(main())
