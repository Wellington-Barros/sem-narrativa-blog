import wave, numpy as np
from scipy.signal import butter, sosfilt
import build15 as B
SR=48000
w=wave.open('voz_final.wav'); v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
TL=B.TL; N=int(TL['total']*SR)+SR
mix=np.zeros(N,np.float32); mix[:len(v)]+=v
rng=np.random.default_rng(7)
def whoosh(dur=0.55):
    n=int(dur*SR); x=rng.standard_normal(n).astype(np.float32)
    out=np.zeros(n,np.float32); blk=512; zi=np.zeros((2,2))
    for i in range(0,n,blk):
        f=i/n; fc=400+3600*np.sin(np.pi*f)**1.5
        sos=butter(2,[fc*0.6,fc*1.6],btype='band',fs=SR,output='sos')
        y,zi=sosfilt(sos,x[i:i+blk],zi=zi)
        out[i:i+blk]=y
    env=np.sin(np.pi*np.linspace(0,1,n))**2.2
    out*=env; return out/(np.abs(out).max()+1e-9)
def thump(dur=0.35):
    n=int(dur*SR); t=np.arange(n)/SR
    x=(np.sin(2*np.pi*58*t)+0.5*np.sin(2*np.pi*116*t))*np.exp(-t*14)
    a=int(0.004*SR); x[:a]*=np.linspace(0,1,a)
    return (x/np.abs(x).max()).astype(np.float32)
def add(sig,center,gain_db):
    g=10**(gain_db/20); s=int(center*SR)-len(sig)//2
    if s<0: sig=sig[-s:]; s=0
    mix[s:s+len(sig)]+=sig*g
add(whoosh(0.5),0.12,-24)
for k,sc in enumerate(TL['scenes']):
    if k>0: add(whoosh(),sc['start']-0.08,-22)
th=[B.kw(0,0,'tomado')+0.42, B.kw(3,3,'ainda')+0.32, B.kw(5,0,'0')+0.05, B.kw(5,1,'não')+0.32]
for t in th: add(thump(),t+0.15,-17)
mix=mix[:int(TL['total']*SR)]
pk=np.abs(mix).max(); print('peak dB',round(20*np.log10(pk),2))
if pk>0.89: mix*=0.89/pk
mix*=10**(-2.6/20)
st=np.stack([mix,mix],1)
w=wave.open('mix_final.wav','w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes()); w.close()
print('thumps',[round(x,2) for x in th])
