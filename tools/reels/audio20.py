import sys, wave, numpy as np
from scipy.signal import butter, sosfilt
SR=48000; DUR=60.0; N=int(DUR*SR)
rng=np.random.default_rng(20)
mus=np.zeros(N,np.float32); fx=np.zeros(N,np.float32)
def put(buf,sig,start,g_db):
    g=10**(g_db/20); s=int(start*SR)
    if s<0: sig=sig[-s:]; s=0
    if s>=N: return
    e=min(N,s+len(sig)); buf[s:e]+=sig[:e-s]*g
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,hi],btype='band',fs=SR,output='sos'),x)
def lp(x,f,o=2): return sosfilt(butter(o,f,fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,btype='high',fs=SR,output='sos'),x)
def norm(x): return (x/(np.abs(x).max()+1e-9)).astype(np.float32)
def ep(freq,dur):
    n=int(dur*SR); t=np.arange(n)/SR
    m=np.sin(2*np.pi*freq*t)*1.6*np.exp(-t*5)
    x=np.sin(2*np.pi*freq*t+m)+.25*np.sin(2*np.pi*2*freq*t)*np.exp(-t*3)
    a=np.minimum(1,t/.006)*np.exp(-t*1.1)*np.minimum(1,(dur-t)/.08)
    trem=1+.12*np.sin(2*np.pi*4.5*t)
    return (x*a*trem).astype(np.float32)
def kick():
    n=int(.35*SR); t=np.arange(n)/SR; f=45+60*np.exp(-t*30)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)).astype(np.float32)
def snap():
    n=int(.18*SR); t=np.arange(n)/SR
    x=bp(rng.standard_normal(n),1200,5000)*np.exp(-t*30)
    return norm(x)
def hat():
    n=int(.05*SR); t=np.arange(n)/SR; return norm(hp(rng.standard_normal(n),7000)*np.exp(-t*90))
def sub(freq,dur):
    n=int(dur*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*freq*t)*np.minimum(1,t/.02)*np.minimum(1,(dur-t)/.1)).astype(np.float32)
bpm=86; beat=60/bpm; bar=4*beat
chords=[[174.61,220.0,261.63,329.63],[164.81,196.0,246.94,293.66],[146.83,174.61,220.0,261.63],[130.81,164.81,196.0,246.94]]
roots=[43.65,41.2,36.71,32.7]
k=0
while k*bar<DUR:
    t0=k*bar; c=k%4
    for i,f in enumerate(chords[c]): put(mus,ep(f,bar*.98),t0+i*.012,-16)
    put(mus,sub(roots[c]*2,bar*.95),t0,-14)
    if k>=0:
        for b in range(4):
            tb=t0+b*beat
            if b in (0,2): put(mus,kick(),tb,-9)
            if b==2 and k%2==1: put(mus,kick(),tb+beat*.5,-14)
            if b in (1,3): put(mus,snap(),tb,-17)
            for h in range(2): put(mus,hat(),tb+h*beat/2+(0.03 if h else 0),-26 if h else -23)
    if k%2==1:
        mel=[523.25,440.0,392.0,329.63]
        put(mus,ep(mel[c],beat*1.5)*.7,t0+beat*2.5,-20)
    k+=1
crk=np.zeros(N,np.float32)
idx=rng.integers(0,N,int(DUR*14)); crk[idx]=rng.uniform(-1,1,len(idx))
crk=hp(crk,1500); mus+=crk*.25
mus+=lp(rng.standard_normal(N),3000).astype(np.float32)*.004
def scribble(dur,pitch=1.0):
    n=int(dur*SR); t=np.arange(n)/SR
    x=bp(rng.standard_normal(n),1800*pitch,6500*pitch)
    am=.55+.45*np.abs(np.sin(2*np.pi*(9+4*rng.random())*t+rng.random()*3))
    a=np.minimum(1,t/.02)*np.minimum(1,(dur-t)/.03)
    return norm(x*am*a)
def thump(bright=1.0):
    n=int(.35*SR); t=np.arange(n)/SR
    f=110*np.exp(-t*20)+60
    lo=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*14)
    pap=bp(rng.standard_normal(n),600,4000)*np.exp(-t*45)*.7*bright
    return norm(lo+pap)
def rustle(dur,up=True):
    n=int(dur*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    y=np.zeros(n); zi=np.zeros((2,2))
    for i in range(0,n,480):
        u=i/n; fc=(900+3000*u) if up else (3900-3000*u)
        o,zi=sosfilt(butter(2,[fc*.5,fc*1.5],btype='band',fs=SR,output='sos'),x[i:i+480],zi=zi); y[i:i+480]=o
    crackle=(rng.random(n)<.004)*rng.uniform(-1,1,n)
    return norm((y+crackle*2)*np.sin(np.pi*t/dur)**1.2)
def air(dur):
    n=int(dur*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    y=np.zeros(n); zi=np.zeros((2,2))
    for i in range(0,n,480):
        fc=300+2200*np.sin(np.pi*i/n)**2
        o,zi=sosfilt(butter(2,[fc*.6,fc*1.6],btype='band',fs=SR,output='sos'),x[i:i+480],zi=zi); y[i:i+480]=o
    return norm(y*np.sin(np.pi*t/dur)**2)
def pluck(f):
    n=int(.6*SR); t=np.arange(n)/SR
    x=(np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*3*f*t)*np.exp(-t*20))*np.exp(-t*7)
    return norm(x*np.minimum(1,t/.003))
def chime():
    n=int(1.6*SR); t=np.arange(n)/SR; x=0
    for f,g in ((1046.5,1),(1318.5,.6),(1568,.5),(2093,.25)): x=x+g*np.sin(2*np.pi*f*t)*np.exp(-t*(2.5+f/1500))
    return norm(x*np.minimum(1,t/.004))
def tape(dur=.28):
    n=int(dur*SR); t=np.arange(n)/SR
    x=bp(rng.standard_normal(n),2000,8000)*(.6+.4*np.sign(np.sin(2*np.pi*60*t)))
    return norm(x*np.sin(np.pi*t/dur))
put(fx,thump(),0.0,-6)
for t0,d in [(1.35,.36),(1.72,.28),(2.0,.12),(2.12,.14),(2.26,.34)]: put(fx,scribble(d),t0,-9)
put(fx,thump(.4),2.62,-4)
for t0,d in [(5.0,1.2),(13.0,1.2),(21.0,1.0),(29.4,1.2),(37.0,1.2),(45.6,1.0)]:
    put(fx,air(d+.2),t0-.1,-17); put(fx,scribble(d*.8,.7),t0+.1,-22)
put(fx,scribble(.6),6.9,-10)
for t0 in (8.5,9.2,9.9): put(fx,tape(),t0,-15); put(fx,thump(.6),t0+.14,-12)
put(fx,rustle(.4),10.9,-22)
notes=[392.0,440.0,493.88,523.25,587.33]
for i in range(5): put(fx,pluck(notes[i]),15.0+i*.32,-14); put(fx,pluck(notes[i]*2),15.0+i*.32+.9,-24)
for t0 in (17.5,17.85): put(fx,thump(),t0+.15,-8)
put(fx,rustle(.45,True),23.45,-12)
put(fx,air(.9),23.95,-20)
put(fx,thump(),24.82,-7)
put(fx,scribble(.55),26.4,-10)
for i,t0 in enumerate((31.0,32.4,33.8,35.2)): put(fx,thump(),t0+.15,-8); put(fx,rustle(.2),t0,-24)
for t0 in (38.8,40.6,42.6): put(fx,rustle(.3,False),t0-.05,-18); put(fx,thump(.8),t0+.15,-9)
put(fx,scribble(.55),47.3,-10)
for i in range(4): put(fx,scribble(.22,1.1),48.7+i*.35,-9)
put(fx,air(1.8),52.95,-11); put(fx,scribble(1.4,.7),53.1,-20)
put(fx,air(1.5),55.45,-13)
put(fx,chime(),56.9,-12)
duck=np.ones(N,np.float32)
def ramp(a,b,v0,v1):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.linspace(v0,v1,i1-i0)
ramp(53.0,53.8,1,.55); duck[int(53.8*SR):int(55.6*SR)]=.55; ramp(55.6,56.9,.55,1)
fade=np.ones(N,np.float32); fl=int(2.0*SR); fade[-fl:]=np.linspace(1,0,fl)
fade[:int(.02*SR)]=np.linspace(0,1,int(.02*SR))
mix=(mus*duck*.6+fx)*fade
mix=mix/np.abs(mix).max()*.89
L=mix.copy(); R=mix.copy()
st=np.stack([L,R],1)
w=wave.open(sys.argv[1],'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
print('ok')
