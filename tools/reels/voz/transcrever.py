import sys, base64, wave, json
import numpy as np
import onnxruntime as ort
from scipy.signal import resample_poly

D = '/home/claude/asr/sherpa-onnx-whisper-turbo/'
so = ort.SessionOptions()
so.intra_op_num_threads = 2
enc = ort.InferenceSession(D + 'turbo-encoder.int8.onnx', so, providers=['CPUExecutionProvider'])
dec = ort.InferenceSession(D + 'turbo-decoder.int8.onnx', so, providers=['CPUExecutionProvider'])
meta = enc.get_modelmeta().custom_metadata_map
codes = meta['all_language_codes'].split(',')
ltoks = [int(x) for x in meta['all_language_tokens'].split(',')]
LANG = ltoks[codes.index('pt')]
SOT, EOT = int(meta['sot']), int(meta['eot'])
TRANSCRIBE, NOTS = int(meta['transcribe']), int(meta['no_timestamps'])
TS0 = NOTS + 1
NL, NCTX, NST = int(meta['n_text_layer']), int(meta['n_text_ctx']), int(meta['n_text_state'])

vocab = {}
for line in open(D + 'turbo-tokens.txt', encoding='utf-8'):
    p = line.rstrip('\n').split(' ')
    if len(p) == 2:
        vocab[int(p[1])] = base64.b64decode(p[0])


def mel_filters(sr=16000, n_fft=400, n_mels=128):
    def hz2mel(f):
        f = np.asanyarray(f, dtype=float)
        m = f / (200.0 / 3)
        ls = np.log(6.4) / 27.0
        return np.where(f >= 1000, 15.0 + np.log(np.maximum(f, 1e-10) / 1000.0) / ls, m)

    def mel2hz(m):
        m = np.asanyarray(m, dtype=float)
        f = m * (200.0 / 3)
        ls = np.log(6.4) / 27.0
        return np.where(m >= 15.0, 1000.0 * np.exp(ls * (m - 15.0)), f)

    fft = np.linspace(0, sr / 2, 1 + n_fft // 2)
    mf = mel2hz(np.linspace(hz2mel(0), hz2mel(sr / 2), n_mels + 2))
    fd = np.diff(mf)
    ramps = mf[:, None] - fft[None, :]
    w = np.zeros((n_mels, len(fft)))
    for i in range(n_mels):
        lo = -ramps[i] / fd[i]
        up = ramps[i + 2] / fd[i + 1]
        w[i] = np.maximum(0, np.minimum(lo, up))
    w *= (2.0 / (mf[2:n_mels + 2] - mf[:n_mels]))[:, None]
    return w


MF = mel_filters()


def load(path):
    w = wave.open(path)
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if w.getnchannels() > 1:
        x = x.reshape(-1, w.getnchannels()).mean(1)
    if sr != 16000:
        g = np.gcd(sr, 16000)
        x = resample_poly(x, 16000 // g, sr // g).astype(np.float32)
    return x


def logmel(x):
    x = np.concatenate([x, np.zeros(16000 * 30, dtype=np.float32)])
    n_fft, hop = 400, 160
    xp = np.pad(x, (n_fft // 2, n_fft // 2), mode='reflect')
    win = np.hanning(n_fft + 1)[:-1]
    nfr = 1 + (len(xp) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(nfr)[:, None]
    spec = np.abs(np.fft.rfft(xp[idx] * win, axis=1)) ** 2
    spec = spec[:-1].T
    m = MF @ spec
    lm = np.log10(np.maximum(m, 1e-10))
    lm = np.maximum(lm, lm.max() - 8.0)
    lm = (lm + 4.0) / 4.0
    return lm[:, :3000].astype(np.float32)[None]


def transcribe(path):
    x = load(path)
    ck, cv = enc.run(None, {'mel': logmel(x)})
    sk = np.zeros((NL, 1, NCTX, NST), dtype=np.float32)
    sv = np.zeros_like(sk)
    toks = [SOT, LANG, TRANSCRIBE]
    out = []
    cur = np.array([toks], dtype=np.int64)
    off = 0
    for _ in range(220):
        logits, sk, sv = dec.run(None, {'tokens': cur, 'in_n_layer_self_k_cache': sk, 'in_n_layer_self_v_cache': sv,
                                        'n_layer_cross_k': ck, 'n_layer_cross_v': cv,
                                        'offset': np.array([off], dtype=np.int64)})
        off += cur.shape[1]
        lg = logits[0, -1].astype(np.float64)
        lg[NOTS] = -1e9
        if not out:
            lg[:TS0] = -1e9
            lg[EOT] = -1e9
        ts_l = np.logaddexp.reduce(lg[TS0:] - lg.max())
        tx_l = (lg[:TS0] - lg.max()).max()
        if out and out[-1] >= TS0:
            if len(out) < 2 or out[-2] >= TS0:
                lg[TS0:] = -1e9
            else:
                lg[:EOT] = -1e9
        tsl = [q for q in out if q >= TS0]
        if tsl:
            lg[TS0:tsl[-1] + (1 if out[-1] < TS0 else 0)] = -1e9
        if ts_l > tx_l and not (out and out[-1] >= TS0 and (len(out) < 2 or out[-2] >= TS0)):
            lg[:TS0] = -1e9
        t = int(lg.argmax())
        if t == EOT:
            break
        out.append(t)
        cur = np.array([[t]], dtype=np.int64)
    segs = []
    start = None
    buf = b''
    for t in out:
        if t >= TS0:
            tt = (t - TS0) * 0.02
            if start is None:
                start = tt
            else:
                segs.append((round(start, 2), round(tt, 2), buf.decode('utf-8', 'replace').strip()))
                start, buf = None, b''
        else:
            buf += vocab.get(t, b'')
    if buf.strip():
        segs.append((start, None, buf.decode('utf-8', 'replace').strip()))
    return segs


if __name__ == '__main__':
    res = {}
    for p in sys.argv[1:]:
        s = transcribe(p)
        res[p] = s
        print('==', p, flush=True)
        for a, b, t in s:
            print(f'  [{a} - {b}] {t}', flush=True)
    json.dump(res, open('/home/claude/asr/transcricao.json', 'w'), ensure_ascii=False, indent=1)
