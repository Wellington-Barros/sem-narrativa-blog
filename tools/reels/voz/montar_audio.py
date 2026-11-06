import wave, numpy as np, json
SR=48000
SENT={1:[(4.61,8.11),(8.84,11.68),(12.08,15.67),(16.48,17.75)],
      2:[(3.11,9.69),(11.21,16.99),(17.84,22.22)],
      3:[(2.66,10.05),(10.79,19.44)],
      4:[(2.05,7.00),(7.80,15.34),(16.10,19.87),(20.23,22.20)],
      5:[(2.17,6.42),(7.04,13.64),(14.23,17.29)],
      6:[(2.03,7.75),(8.66,13.28),(14.38,18.59)],
      7:[(2.56,9.10),(9.91,14.62),(15.43,19.71)],
      8:[(3.04,4.47),(5.07,7.83),(8.44,14.70),(15.29,18.45)],
      9:[(2.23,4.54),(11.51,13.93),(15.09,17.06)]}
segs=json.load(open('segs.json'))
def load(i):
    w=wave.open(f'raw{i}.wav'); return np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
def fade(a,n=480):
    a=a.copy(); n=min(n,len(a)//2)
    r=np.linspace(0,1,n); a[:n]*=r; a[-n:]*=r[::-1]; return a
PRE,POST=0.07,0.16
CAP_IN,CAP_SENT=0.26,0.38
out={}
for i,sents in SENT.items():
    x=load(i)
    runs=[r for r in segs[str(i)] if r[1]-r[0]>=0.18]
    pieces=[]; cues=[]; t=0.0
    for si,(a,b) in enumerate(sents):
        rr=[r for r in runs if r[0]>=a-0.05 and r[1]<=b+0.05]
        if si>0: 
            g=CAP_SENT; pieces.append(np.zeros(int(g*SR),np.float32)); t+=g
        cs=t
        for k,(ra,rb) in enumerate(rr):
            if k>0:
                gap=ra-rr[k-1][1]
                g=min(gap,CAP_IN)
                pieces.append(np.zeros(int(g*SR),np.float32)); t+=g
            s0=max(0,ra-(PRE if k==0 else 0.04)); s1=rb+(POST if k==len(rr)-1 else 0.05)
            seg=fade(x[int(s0*SR):int(s1*SR)])
            pieces.append(seg); t+=len(seg)/SR
        cues.append([round(cs,3),round(t,3)])
    y=np.concatenate(pieces)
    w=wave.open(f'proc/cut{i}.wav','w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y,-1,1)*32767).astype(np.int16).tobytes()); w.close()
    out[i]={'dur':round(len(y)/SR,3),'cues':cues}
    print(i, out[i]['dur'], cues)
print('total', round(sum(v['dur'] for v in out.values()),2))
json.dump(out,open('proc/cues_raw.json','w'))
