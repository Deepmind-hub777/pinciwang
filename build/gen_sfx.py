import numpy as np, subprocess, os
SR=44100
rng=np.random.default_rng(7)
def env(n,a=0.003,dec=0.2):
    t=np.arange(n)/SR; e=np.minimum(1,t/a)*np.exp(-t/dec); return e
def sine(f,dur,dec=0.3,a=0.003,harm=((1,1),)):
    n=int(dur*SR); t=np.arange(n)/SR
    y=sum(g*np.sin(2*np.pi*f*h*t) for h,g in harm); return y*env(n,a,dec)
def bell(f,dur=1.2,dec=0.45):
    return sine(f,dur,dec,harm=((1,1),(2.0,.45),(3.01,.25),(4.2,.12),(5.4,.06)))
def pluck(f,dur=1.6,bright=0.5):
    n=int(dur*SR); N=int(SR/f); buf=rng.uniform(-1,1,N)
    # lowpass initial burst for softer guzheng-like tone
    for _ in range(2): buf=(buf+np.roll(buf,1))/2
    out=np.zeros(n); dec=0.996
    for i in range(n):
        out[i]=buf[i%N]; nxt=(buf[i%N]+buf[(i+1)%N])*0.5*dec; buf[i%N]=nxt
    out*=np.minimum(1,np.arange(n)/(0.002*SR))
    # add slight pitch-bend "揉弦" feel via second partial
    return out
def wood(f,dur=0.08):
    n=int(dur*SR); t=np.arange(n)/SR
    y=np.sin(2*np.pi*f*t)*np.exp(-t/0.018)+0.4*rng.uniform(-1,1,n)*np.exp(-t/0.004)
    return y
def mix(parts,total):
    out=np.zeros(int(total*SR))
    for start,y,g in parts:
        s=int(start*SR); e=min(len(out),s+len(y)); out[s:e]+=g*y[:e-s]
    return out
def save(name,y,br='48k',peak=0.85):
    y=y/ (np.abs(y).max()+1e-9)*peak
    raw='/tmp/%s.raw'%name; (y.astype(np.float32)).tofile(raw)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','f32le','-ar',str(SR),'-ac','1','-i',raw,'-ar','44100','-ac','1','-b:a',br,'../audio/sfx/%s.mp3'%name],check=True)
N={'C5':523.25,'D5':587.33,'E5':659.25,'G5':783.99,'A5':880,'C6':1046.5,'D6':1174.7,'E6':1318.5,'G6':1568,'A6':1760,'C4':261.63,'D4':293.66,'E4':329.63,'G4':392,'A4':440,'C3':130.81,'G3':196,'A3':220,'E3':164.81,'D3':146.83}
save('tap',wood(1100,0.07),peak=0.6)
save('untap',wood(700,0.07),peak=0.5)
save('click',mix([(0,wood(1500,0.05),1),(0.012,wood(900,0.05),.5)],0.08),peak=0.5)
save('correct',mix([(0,bell(N['E6'],1.0,.35),1),(0.09,bell(N['A6'],1.1,.4),.9),(0.0,wood(1400,.06),.4)],1.2))
w=lambda f,d: np.sign(np.sin(2*np.pi*f*np.arange(int(d*SR))/SR))*env(int(d*SR),0.005,0.08)
lp=lambda y,k=6: np.convolve(y,np.ones(k)/k,'same')
save('wrong',lp(mix([(0,w(140,0.16),1),(0.17,w(110,0.22),1)],0.42),12),peak=0.55)
save('dup',mix([(0,wood(620,0.09),1),(0.13,wood(620,0.09),.8)],0.25),peak=0.6)
save('hint',mix([(i*0.07,bell(f,0.7,.25),0.8) for i,f in enumerate([N['C6'],N['D6'],N['E6'],N['G6'],N['A6']])],1.1))
save('coin',mix([(0,sine(2093,0.25,.07,harm=((1,1),(2.7,.3))),1),(0.07,sine(2637,0.4,.12,harm=((1,1),(2.7,.3))),1)],0.5),peak=0.6)
# clear fanfare: guzheng glissando + chord + soft gong
gl=[N[k] for k in ['C4','D4','E4','G4','A4','C5','D5','E5','G5','A5','C6']]
parts=[(i*0.045,pluck(f,1.6),0.55) for i,f in enumerate(gl)]
parts+= [(0.6,pluck(N['C5'],2.2),.8),(0.6,pluck(N['E5'],2.2),.6),(0.6,pluck(N['G5'],2.2),.6),(0.6,pluck(N['C6'],2.2),.5)]
gong=sine(N['C3'],2.5,1.0,a=0.02,harm=((1,1),(1.48,.4),(2.03,.3),(2.76,.2)))
parts+=[(0.6,gong,.35),(0.62,bell(N['G6'],1.4,.5),.35)]
save('clear',mix(parts,2.9),br='56k')
save('gift',mix([(i*0.06,bell(f,0.6,.2),0.7) for i,f in enumerate([N['G5'],N['C6'],N['E6'],N['G6'],N['C6'],N['E6'],N['G6'],N['A6']])]+[(0.5,sine(2093,0.25,.07),.6),(0.58,sine(2637,0.4,.12),.6)],1.2))
save('start',mix([(0,pluck(N['G4'],1.2),1),(0.12,pluck(N['C5'],1.4),1),(0.24,pluck(N['E5'],1.6),.9)],1.6))
# BGM: slow pentatonic guzheng melody over drone, 32s loop
bpm=72; beat=60/bpm
mel=['E5','G5','A5','-','G5','E5','D5','-','C5','D5','E5','G5','E5','-','-','-',
     'A4','C5','D5','-','E5','D5','C5','A4','G4','A4','C5','-','-','-','-','-',
     'E5','G5','A5','C6','A5','G5','E5','-','D5','E5','G5','E5','D5','C5','D5','-',
     'C5','A4','G4','A4','C5','D5','E5','D5','C5','-','-','-','-','-','-','-']
step=beat/2; total=len(mel)*step
parts=[]
for i,k in enumerate(mel):
    if k!='-': parts.append((i*step,pluck(N[k],2.4),0.5))
bass=['C3','A3','E3','G3','C3','A3','D3','G3']
for j,k in enumerate(bass):
    parts.append((j*total/8,pluck(N[k],4.0),0.45)); parts.append((j*total/8+beat*2,pluck(N[k]*1.5,3.0),0.25))
y=mix(parts,total+2.5)
tail=y[int(total*SR):]; y=y[:int(total*SR)]; y[:len(tail)]+=tail   # seamless loop
save('bgm',lp(y,3),br='40k',peak=0.6)
print('ok')
