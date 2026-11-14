import sys, wave, numpy as np
from scipy.signal import butter, sosfilt
SR=48000
T=[0,6.6,14.2,21.0,30.0,36.6,45.0,52.0,59.0]
DUR=T[-1]; N=int(DUR*SR)
rng=np.random.default_rng(17)
mus=np.zeros(N,np.float32); fx=np.zeros(N,np.float32)
def put(buf,sig,start,g_db):
    g=10**(g_db/20); s=int(start*SR)
    if s>=N: return
    e=min(N,s+len(sig)); buf[s:e]+=sig[:e-s]*g
def env_exp(n,k): return np.exp(-np.arange(n)/SR*k).astype(np.float32)
def kick():
    n=int(.32*SR); t=np.arange(n)/SR
    f=48+90*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-t*9); x[:96]*=np.linspace(0,1,96); return x.astype(np.float32)
def hat():
    n=int(.06*SR); x=rng.standard_normal(n).astype(np.float32)
    x=sosfilt(butter(2,7000,btype='high',fs=SR,output='sos'),x)*env_exp(n,70); return x.astype(np.float32)
def bass(freq,dur):
    n=int(dur*SR); t=np.arange(n)/SR
    x=np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*2*freq*t)
    a=np.minimum(1,t/.01)*np.exp(-t*2.2); return (x*a).astype(np.float32)
def pad(freqs,dur):
    n=int(dur*SR); t=np.arange(n)/SR; x=np.zeros(n)
    for f in freqs:
        for d in (-.6,.6): x+=np.sin(2*np.pi*(f+d)*t)
    x=sosfilt(butter(2,1800,fs=SR,output='sos'),x)
    a=np.minimum(1,t/.4)*np.minimum(1,(dur-t)/.4); return (x*a/len(freqs)/2).astype(np.float32)
def whoosh(dur=.5):
    n=int(dur*SR); x=rng.standard_normal(n).astype(np.float32); out=np.zeros(n,np.float32); zi=np.zeros((2,2))
    for i in range(0,n,512):
        fc=400+3600*np.sin(np.pi*i/n)**1.5
        y,zi=sosfilt(butter(2,[fc*.6,fc*1.6],btype='band',fs=SR,output='sos'),x[i:i+512],zi=zi); out[i:i+512]=y
    out*=np.sin(np.pi*np.linspace(0,1,n))**2.2; return out/(np.abs(out).max()+1e-9)
def impact():
    n=int(.9*SR); t=np.arange(n)/SR
    f=40+70*np.exp(-t*18); x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*4.5)
    nz=sosfilt(butter(2,2500,fs=SR,output='sos'),rng.standard_normal(n))*np.exp(-t*12)*.5
    y=x+nz; return (y/np.abs(y).max()).astype(np.float32)
def pop():
    n=int(.12*SR); t=np.arange(n)/SR; f=900*np.exp(-t*18)+300
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*35); return x.astype(np.float32)
def tick():
    n=int(.025*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*2400*t)*np.exp(-t*220)).astype(np.float32)
bpm=104; beat=60/bpm
roots=[55.0,55.0,43.65,49.0]
chords=[[220,261.6,329.6],[220,261.6,329.6],[174.6,220,261.6],[196,246.9,293.7]]
b=0; t=0.0
while t<DUR-.3:
    bar=int(b//4)%4
    if t>=0.4:
        put(mus,kick(),t,-6 if b%2==0 else -9)
        put(mus,hat(),t+beat/2,-18)
        if b%4==0: put(mus,bass(roots[bar],beat*3.6),t,-10)
        if b%4==0: put(mus,pad(chords[bar],beat*4),t,-21)
    b+=1; t=b*beat
for x in T[1:-1]: put(fx,whoosh(.5),x-.3,-12)
put(fx,impact(),0.35,-4)
for i in range(7): put(fx,pop(),T[0]+.4+i*.07,-16)
put(fx,whoosh(.4),T[0]+3.15,-12); put(fx,impact(),T[0]+3.55,-1)
put(fx,whoosh(.5),T[1]+.2,-14); put(fx,impact(),T[1]+.85,-5)
put(fx,whoosh(.3),T[1]+2.0,-12); put(fx,pop(),T[1]+2.25,-8)
for k in range(25): put(fx,tick(),T[2]+1.0+k*2.4/24,-16)
put(fx,impact()[:int(.5*SR)],T[2]+3.4,-7)
put(fx,whoosh(.3),T[3]+1.8,-12); put(fx,pop(),T[3]+2.05,-9); put(fx,whoosh(.4),T[3]+2.1,-15); put(fx,pop(),T[3]+2.95,-7); put(fx,impact(),T[3]+3.75,-5)
for i in range(4): put(fx,pop(),T[4]+.6+i*1.1,-9)
put(fx,whoosh(.35),T[5]+1.5,-13); put(fx,whoosh(.35),T[5]+2.7,-13)
for i in range(4): put(fx,pop(),T[6]+1.4+i*.6,-7)
put(fx,impact(),T[6]+3.9,-5)
put(fx,impact()[:int(.5*SR)],T[7]+.15,-9); put(fx,pop(),T[7]+1.8,-6)
fade=np.ones(N,np.float32); fl=int(1.6*SR); fade[-fl:]=np.linspace(1,0,fl)
mix=(mus*.55+fx)*fade
mix=mix/np.abs(mix).max()*.89
st=np.stack([mix,mix],1)
w=wave.open(sys.argv[1],'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
print('ok',DUR)
