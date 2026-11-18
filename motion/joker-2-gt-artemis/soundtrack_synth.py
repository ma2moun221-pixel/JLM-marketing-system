import numpy as np
from scipy import signal
from scipy.io import wavfile
SR=44100; DUR=15.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def place(x,t,gain=1.0,pan=0.0):
    i=int(t*SR); x=x[:max(0,N-i)]
    L[i:i+len(x)]+=x*gain*(1-max(0,pan)); R[i:i+len(x)]+=x*gain*(1+min(0,pan))
def env(n,a,d):
    t=np.arange(n)/SR; e=np.exp(-t/d); at=int(a*SR)
    if at>0: e[:at]*=np.linspace(0,1,at)
    return e
def bp(x,lo,hi,o=2):
    b,a=signal.butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return signal.lfilter(b,a,x)
def hp(x,f): b,a=signal.butter(2,f/(SR/2),'high'); return signal.lfilter(b,a,x)
def lp(x,f): b,a=signal.butter(2,f/(SR/2),'low'); return signal.lfilter(b,a,x)
def kick(big=False):
    n=int(SR*(0.9 if big else 0.45)); t=np.arange(n)/SR
    f=45+ (170 if big else 130)*np.exp(-t*28)
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*env(n,0.001,0.35 if big else 0.16)
    x=np.tanh(x*(3 if big else 2.2))
    click=hp(rng.normal(0,1,n),3000)*env(n,0,0.004)*0.4
    return x+click
def snare():
    n=int(SR*0.3); t=np.arange(n)/SR
    nz=bp(rng.normal(0,1,n),1200,8000)*env(n,0.001,0.09)
    tone=np.sin(2*np.pi*190*t)*env(n,0,0.05)
    return (nz*0.8+tone*0.5)
def hat(op=False):
    n=int(SR*(0.2 if op else 0.06)); return hp(rng.normal(0,1,n),7000)*env(n,0,0.06 if op else 0.015)*0.5
def sub(t0,dur,f=55):
    n=int(SR*dur); t=np.arange(n)/SR
    x=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*2*t)
    e=np.minimum(1,t/0.01)*np.exp(-t/0.3)
    place(np.tanh(x*e*1.5)*0.55,t0)
def whoosh(t0,dur=0.5,rev=False,g=0.5,pan=0):
    n=int(SR*dur); nz=rng.normal(0,1,n); out=np.zeros(n)
    seg=512
    for s in range(0,n,seg):
        p=s/n; fc=300+ (p if not rev else p)*5000
        lo=max(80,fc*0.5); hi=min(SR/2-100,fc*1.6)
        out[s:s+seg]=bp(nz[s:s+seg] if True else 0,lo,hi,1)
    shape=np.sin(np.pi*np.linspace(0,1,n))**2 if not rev else np.linspace(0,1,n)**3
    place(out*shape,t0,g,pan)
def boom(t0,g=1.0):
    n=int(SR*3.0); t=np.arange(n)/SR
    f=32+60*np.exp(-t*6); x=np.sin(2*np.pi*np.cumsum(f)/SR)
    x=np.tanh(x*2.5)*np.exp(-t/0.9)
    nz=lp(rng.normal(0,1,n),900)*np.exp(-t/0.35)*0.5
    crack=hp(rng.normal(0,1,n),2000)*np.exp(-t/0.03)*0.6
    place((x+nz+crack)*g,t0)
def tick(t0):
    n=int(SR*0.12); t=np.arange(n)/SR
    x=np.sin(2*np.pi*1760*t)*np.exp(-t/0.02)+np.sin(2*np.pi*880*t)*np.exp(-t/0.05)*0.5
    place(x*0.35,t0)
# drone pad (A minor-ish), whole length, low
t=np.arange(N)/SR
pad=np.zeros(N)
for f in [55,82.4,110,130.8,164.8]:
    for d in [-0.3,0.3]:
        pad+=signal.sawtooth(2*np.pi*(f+d)*t)
pad=lp(pad,600)/10
padenv=np.interp(t,[0,1.8,2.0,12.4,12.5,14.2,15],[0.15,0.35,0.25,0.3,0.45,0.35,0])
L+=pad*padenv*0.6; R+=pad*padenv*0.6
# countdown ticks + riser
for i,tt in enumerate([0.2,0.7,1.2]): tick(tt); sub(tt,0.45,55)
n=int(SR*1.9); tr=np.arange(n)/SR
riser=bp(rng.normal(0,1,n),400,9000)*(tr/1.9)**3*0.6+signal.sawtooth(2*np.pi*(110+500*(tr/1.9)**2)*tr)*(tr/1.9)**3*0.08
place(lp(riser,8000),0.1)
whoosh(1.5,0.5,rev=True,g=0.7)
# main impact at 2.0
boom(2.0,1.0)
# groove 2.5 -> 12.5 at 120bpm
beat=0.5
for k in range(int((12.5-2.0)/beat)):
    tb=2.0+k*beat
    if tb>=2.5: place(kick(),tb,0.9)
    if k%2==1: place(snare(),tb,0.55)
    for h in range(2):
        place(hat(h==1 and k%2==1),tb+h*0.25,0.35,pan=0.3 if h else -0.3)
    if k%2==0 and tb>=2.5: sub(tb,0.5,55 if (k//4)%2==0 else 49)
# scene cut whooshes (frames/30)
for fr in [150,225,285,330]:
    whoosh(fr/30-0.25,0.45,g=0.55,pan=rng.uniform(-0.4,0.4)); place(kick(True),fr/30,0.6)
# landing: reverse swell then big boom
whoosh(11.9,0.6,rev=True,g=0.8)
boom(13.1,1.15)   # landing frame ~393
place(snare(),13.1,0.6)
# final shimmer hit at logo
n=int(SR*1.8); ts=np.arange(n)/SR
sh=sum(np.sin(2*np.pi*f*ts) for f in [880,1318.5,1760,2637])*np.exp(-ts/0.6)*0.06
place(sh,13.6)
mix=np.stack([L,R],1)
mix=hp(mix.T,25).T
fade=np.ones(N); fn=int(SR*0.6); fade[-fn:]=np.linspace(1,0,fn)**2
mix*=fade[:,None]
mix=np.tanh(mix/np.max(np.abs(mix))*1.6)/np.tanh(1.6)*0.89
wavfile.write("public/soundtrack.wav",SR,(mix*32767).astype(np.int16))
print("done",mix.shape)
