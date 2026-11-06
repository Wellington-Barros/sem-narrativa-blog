import json, wave, numpy as np, re

SR = 48000
TL = json.load(open('/home/claude/vox/proc/timeline.json'))
CAP = [
    ["Um banco digital do Paraguai foi tomado pelo banco central.",
     "Milhões de clientes ficaram sem acesso às contas.",
     "E dois dias depois, o presidente anunciou que vai renunciar.",
     "Entenda o que aconteceu."],
    ["No dia 3 de novembro, o banco central do Paraguai tomou o Ueno Bank.",
     "Segundo o banco central, o capital ficou abaixo da metade do mínimo que a lei exige.",
     "Aplicativo, cartões e transferências pararam de funcionar."],
    ["Segundo a Associated Press, cerca de 800 milhões de dólares em dinheiro público estavam no banco.",
     "O Congresso aprovou uma lei para o fundo de garantia pagar os clientes em até 5 dias úteis, começando pelas contas pequenas."],
    ["Parlamentares acusam o presidente Santiago Peña de conflito de interesses.",
     "Ele teve ações de uma empresa ligada ao Ueno e escolheu para o banco central um ex-dirigente da financeira do banco.",
     "Peña diz que vendeu a parte dele em 2025.",
     "A acusação ainda não foi julgada."],
    ["Na quinta-feira, Peña anunciou a renúncia em vídeo.",
     "Pediu desculpas, mas, segundo a Associated Press, não assumiu a responsabilidade pela crise.",
     "Ele diz que vai colaborar com as investigações."],
    ["No mesmo dia, a Câmara votou 78 a 0 pela abertura do impeachment.",
     "Já a renúncia não foi votada, porque faltou quórum no Congresso.",
     "Pelas últimas informações que encontrei, ele segue no cargo."],
    ["Se a renúncia for aceita, o vice, Pedro Alliana, assume sem julgamento no Senado.",
     "Se Peña for removido, perde a proteção de senador vitalício.",
     "Por isso, a diferença entre renunciar e ser removido importa."],
    ["O Senado ainda vai julgar.",
     "Peña pediu mais 72 horas para se defender.",
     "Existem investigações, mas não encontrei acusação formal contra ele na Justiça.",
     "E ainda não se sabe quanto dinheiro será recuperado."],
    ["Leia o artigo completo no link da bio,",
     "em semnarrativa.com.br.",
     "Sem recomendar voto. Só fatos."],
]

w = wave.open('/home/claude/vox/proc/voz_final.wav')
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
n = SR // 100
fr = x[:len(x) // n * n].reshape(-1, n)
db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
voiced = db > -38


def word_times(a, b, text):
    ws = text.split(' ')
    i0, i1 = int(a * 100), int(b * 100)
    v = voiced[i0:i1].astype(float)
    if v.sum() < 5:
        v = np.ones_like(v)
    cum = np.concatenate([[0], np.cumsum(v)]) / v.sum()
    SP = {'3': 'tres', '800': 'oitocentos', '5': 'cinco', '2025': 'dois mil e vinte e cinco', '78': 'setenta e oito',
          '0': 'zero', '72': 'setenta e dois', 'semnarrativa.com.br.': 'sem narrativa ponto com ponto be erre'}
    def sp(q):
        k = q.strip(',.') if q.strip(',.') in SP else q
        return SP.get(k, q)
    wts = np.array([len(re.sub(r'[^\wÀ-ÿ0-9 ]', '', sp(q))) + 1.5 for q in ws], dtype=float)
    starts = np.concatenate([[0], np.cumsum(wts)[:-1]]) / wts.sum()
    out = []
    for q, f in zip(ws, starts):
        k = int(np.searchsorted(cum, f, side='left'))
        k = min(max(k - 1, 0), len(v) - 1)
        out.append([q, round(a + k / 100.0, 3)])
    return out


def chunks(wt, end):
    res = []
    cur = []
    ln = 0
    for i, (q, t) in enumerate(wt):
        cur.append([q, t])
        ln += len(q) + 1
        brk = ln >= 24 or (q[-1] in ',.' and ln >= 12)
        if brk or i == len(wt) - 1:
            res.append(cur)
            cur, ln = [], 0
    if len(res) >= 2 and sum(len(q) + 1 for q, _ in res[-1]) < 9:
        last = res.pop()
        res[-1] += last
    out = []
    for j, c in enumerate(res):
        s = c[0][1] - 0.05
        e = res[j + 1][0][1] - 0.05 if j + 1 < len(res) else end + 0.3
        out.append({'s': round(s, 3), 'e': round(e, 3), 'w': c})
    return out


WT = []
CH = []
for si, sc in enumerate(TL['scenes']):
    wl = []
    for ci, (a, b) in enumerate(sc['cues']):
        wt = word_times(a, b, CAP[si][ci])
        wl.append(wt)
        CH += chunks(wt, b)
    WT.append(wl)

json.dump({'TL': TL, 'WT': WT, 'CH': CH}, open('/home/claude/vox/proc/data15.json', 'w'), ensure_ascii=False)


def kw(si, ci, word):
    for q, t in WT[si][ci]:
        if q.lower().strip(',.').startswith(word.lower()):
            return t
    raise KeyError(word)


if __name__ == '__main__':
    for si in range(9):
        for ci in range(len(WT[si])):
            print(si, ci, ' '.join(f'{q}@{t:.2f}' for q, t in WT[si][ci]))
    print(len(CH), 'chunks')
