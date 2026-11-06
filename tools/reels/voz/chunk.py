import sys, numpy as np, transcrever as T
def notime(x):
    ck,cv=T.enc.run(None,{'mel':T.logmel(x)})
    sk=np.zeros((T.NL,1,T.NCTX,T.NST),dtype=np.float32); sv=np.zeros_like(sk)
    cur=np.array([[T.SOT,T.LANG,T.TRANSCRIBE,T.NOTS]],dtype=np.int64); off=0; out=[]
    for _ in range(120):
        lg,sk,sv=T.dec.run(None,{'tokens':cur,'in_n_layer_self_k_cache':sk,'in_n_layer_self_v_cache':sv,'n_layer_cross_k':ck,'n_layer_cross_v':cv,'offset':np.array([off],dtype=np.int64)})
        off+=cur.shape[1]; t=int(lg[0,-1].argmax())
        if t==T.EOT: break
        out.append(t); cur=np.array([[t]],dtype=np.int64)
    return b''.join(T.vocab.get(t,b'') for t in out).decode('utf-8','replace').strip()
x=T.load(sys.argv[1])
for a,b in zip(sys.argv[2::2],sys.argv[3::2]):
    a,b=float(a),float(b)
    print(f'{a:6.2f} {b:6.2f} | {notime(x[int(a*16000):int(b*16000)])}',flush=True)
