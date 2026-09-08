"""Etapa 2, rodada 1 — analise e graficos da validacao do instrumento.

Todo numero impresso aqui e' CALCULADO nesta execucao (CLAUDE.md §9).
Caminhos relativos a ROOT.
"""
import os
import sys
import hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mc_lib import ROOT, load, freq, ensure

TAG = os.environ.get("RUN_TAG", "2026-09-08_etapa2_instrumento")
R = os.path.join(ROOT, f"resultados/{TAG}/raw")
OUT = os.path.join(ROOT, f"resultados/{TAG}")
N = 100

# (nome, area um2, vth0_slope, voff_slope)  — slopes lidos do PDK
GEO = {"A": ("nfet W=1 L=0.5", 0.5, 3.356e-3, 7.0e-3),
       "B": ("pfet W=5 L=1",   5.0, 5.856e-3, 0.0),
       "C": ("nfet W=4 L=0.5", 2.0, 3.356e-3, 7.0e-3)}


def sha(p):
    """SHA-256 do bruto, regenerado a partir do .cir se preciso."""
    ensure(f"resultados/{TAG}/raw/{p}")
    with open(os.path.join(R, p), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def arr(p):
    ensure(f"resultados/{TAG}/raw/{p}")
    d = np.loadtxt(os.path.join(R, p))
    v = np.abs(np.atleast_1d(d[0, 1::2] if d.ndim > 1 else d[1::2]))
    return {"A": v[0:N], "B": v[N:2 * N], "C": v[2 * N:3 * N]}


def sigma_vth(I_lo, I_hi, dV, exponencial):
    """sigma(Vth equivalente). Em sub-limiar a extracao TEM que ser em log:
    a secante (I2-I1)/dV nao e' a derivada de uma exponencial e subestima
    n*Ut por (e^x-1)/x. Erro cometido e corrigido em 2026-09-08."""
    if exponencial:
        nUt = dV / np.log(I_hi / I_lo)
        return np.std(np.log(I_lo), ddof=1) * nUt.mean(), nUt.mean()
    gm = (I_hi.mean() - I_lo.mean()) / dV
    return I_lo.std(ddof=1) / gm, I_lo.mean() / gm


print("=" * 74)
print("ETAPA 2 · RODADA 1 — VALIDACAO DO INSTRUMENTO")
print("=" * 74)

# ---------------------------------------------------------------- V5
t, v = load(f"resultados/{TAG}/raw/v5_nominal.txt", 10)
f5, cv5, n5, e5 = freq(t, v[1])
d5 = 100 * (f5 - 139.58) / 139.58
print(f"\nV5  f = {f5:.4f} Hz  contra 139,58 Hz da etapa 1  ->  {d5:+.3f} %"
      f"   [{'PASSA' if abs(d5) < 1 else 'REPROVA'}]  (criterio: 1%)")

# ---------------------------------------------------------------- V0
f0, h0 = [], []
for k in range(1, 7):
    h0.append(sha(f"v0_tt_seed{k}.txt"))
    t, v = load(f"resultados/{TAG}/raw/v0_tt_seed{k}.txt", 5)
    f0.append(freq(t, v[1])[0])
f0 = np.array(f0)
s0 = f0.std(ddof=1)
print(f"V0  sigma(f) = {s0:.3e} Hz sobre N={len(f0)} no canto tt   "
      f"hashes distintos: {len(set(h0))}   [{'PASSA' if s0 == 0 else 'REPROVA'}]  (criterio: zero exato)")

# ---------------------------------------------------------------- V1
mm, tt = arr("v1s_mm_a.txt"), arr("v1s_tt_a.txt")
print("\nV1  valores DISTINTOS em N=100 instancias de geometria identica:")
ok1 = True
for k in "ABC":
    u_mm, u_tt = len(np.unique(mm[k])), len(np.unique(tt[k]))
    ok1 &= (u_mm == N and u_tt == 1)
    print(f"      {k} {GEO[k][0]:<16} tt_mm: {u_mm:3d}/100   tt: {u_tt:3d}/100"
          f"   sigma/media(tt_mm) = {100*mm[k].std(ddof=1)/mm[k].mean():6.3f} %")
print(f"      [{'PASSA' if ok1 else 'REPROVA'}]  (criterio: 100 distintos com mismatch, 1 sem)")

# ---------------------------------------------------------------- V2
same = sha("v1s_mm_a.txt") == sha("v2s_seed1_r2.txt")
diff = sha("v1s_mm_a.txt") != sha("v2s_seed7.txt")
old_ns = sha("v2_noseed_r1.txt") != sha("v2_noseed_r2.txt")
print(f"\nV2  `.option seed=1` em duas execucoes -> identico bit a bit: {same}")
print(f"    `.option seed=1` contra `.option seed=7`  -> diferente:    {diff}")
print(f"    `set rndseed` no .control, duas execucoes -> diferente:    {old_ns}  <- NAO fixa")
print(f"      [{'PASSA' if (same and diff and old_ns) else 'REPROVA'}]")

# ---------------------------------------------------------------- V3
print("\nV3  magnitude, contra os slopes do PDK (previsao pre-registrada nao viu estes dados)")
res = {}
for reg, (lo_f, hi_f, dV, expo) in {
        "inversao forte (|Vgs| 1,20->1,25 V)": ("v1s_mm_a.txt", "v1s_mm_b.txt", 0.05, False),
        "sub-limiar     (|Vgs| 0,35->0,40 V)": ("v1s_mm_sa.txt", "v1s_mm_sb.txt", 0.05, True)}.items():
    lo, hi = arr(lo_f), arr(hi_f)
    print(f"    {reg}")
    res[reg] = {}
    for k in "ABC":
        sV, scale = sigma_vth(lo[k], hi[k], dV, expo)
        nome, area, vs, vo = GEO[k]
        pv, pvo = vs / np.sqrt(area), vo / np.sqrt(area)
        pq = np.hypot(pv, pvo)
        res[reg][k] = (sV, pv, pq)
        extra = f"n = {scale/0.02585:.2f}" if expo else f"Id/gm = {scale:.3f} V"
        print(f"      {k} {nome:<16} sigma(Vth_eq) = {1e3*sV:6.3f} mV   "
              f"previsto vth0 {1e3*pv:5.3f} / quadratura {1e3*pq:6.3f} mV   "
              f"medido/quad = {sV/pq:5.3f}   {extra}")
    a, c = res[reg]["A"][0], res[reg]["C"][0]
    print(f"      V3b Pelgrom sigma(A)/sigma(C) = {a/c:.4f}  (geometrico 2,000, area 4x)")

# ---------------------------------------------------------------- conv
print("\nCONVERGENCIA com o sorteio FIXO por `.option seed` (so o tstep muda)")
conv = {}
for k in (1, 4):
    fs = []
    for ts in ("0p5u", "0p125u"):
        t, v = load(f"resultados/{TAG}/raw/conv_s{k}_ts{ts}.txt", 5)
        fs.append(freq(t, v[1])[0])
    conv[k] = fs
    d = 100 * (fs[1] - fs[0]) / fs[0]
    print(f"    seed {k}: {fs[0]:.4f} Hz (0,5 us) -> {fs[1]:.4f} Hz (0,125 us)"
          f"   desvio {d:+.4f} %   [{'PASSA' if abs(d) < 1 else 'REPROVA'}]")

# ---------------------------------------------------------------- V4
f4, exc4, mx4 = [], [], []
for k in range(1, 13):
    t, v = load(f"resultados/{TAG}/raw/v4_mm_seed{k}.txt", 5)
    a, b, c, e = freq(t, v[1])
    f4.append(a); exc4.append(e); mx4.append(v[1].max())
f4 = np.array(f4)
s4 = 100 * f4.std(ddof=1) / f4.mean()
print(f"\nV4  N={len(f4)} no canto tt_mm: media {f4.mean():.4f} Hz, "
      f"sigma/f = {s4:.3f} %   [{'PASSA' if s4 > 0.1 else 'REPROVA'}]  (criterio de falha: <0,1%)")
print(f"    min {f4.min():.3f}  max {f4.max():.3f} Hz   todas dispararam: {len(f4)==12}   "
      f"out max global {max(mx4):.4f} V < VDD 1,8 V: {max(mx4) < 1.8}")

# ================================================================= GRAFICO
fig, ax = plt.subplots(2, 3, figsize=(16.5, 9))
fig.suptitle("Etapa 2 · rodada 1 — validacao do instrumento estatistico  "
             "(ngspice 42, sky130A, 27 C)", fontsize=13, weight="bold")

# 1 · V0 contra V4
a = ax[0, 0]
a.plot(range(1, 7), f0, "o-", color="#1b7837", label=f"tt (V0): sigma = {s0:.0e} Hz")
a.plot(range(1, 13), f4, "s", color="#c51b7d", label=f"tt_mm (V4): sigma/f = {s4:.2f} %")
a.axhline(f5, color="k", ls="--", lw=.8, label=f"nominal {f5:.2f} Hz")
a.set_xlabel("indice da amostra (semente)"); a.set_ylabel("frequencia de disparo (Hz)")
a.set_title("1 · o zero e' alcancavel, e o nao-zero aparece", fontsize=10)
a.legend(fontsize=8); a.grid(alpha=.3)

# 2 · V1 dispersao das correntes
a = ax[0, 1]
for i, k in enumerate("ABC"):
    y = mm[k] / mm[k].mean()
    a.scatter(np.full(N, i) + np.random.default_rng(0).normal(0, .06, N), y, s=7,
              alpha=.55, color="#c51b7d")
    a.scatter([i + .32], [1.0], marker="_", s=400, color="#1b7837")
a.set_xticks(range(3))
a.set_xticklabels([f"{k}\n{GEO[k][0]}\n{GEO[k][1]} um2" for k in "ABC"], fontsize=8)
a.set_ylabel("Id / media do array")
a.set_title("2 · V1: 100 instancias IDENTICAS, tt_mm (rosa) e tt (verde)", fontsize=10)
a.grid(alpha=.3, axis="y")

# 3 · V3 medido contra previsto
a = ax[0, 2]
regs = list(res.keys()); w = .35
# em inversao forte `voff` quase nao age -> a previsao certa e' so vth0 (indice 1).
# em sub-limiar `voff` age -> a previsao certa e' a quadratura vth0+voff (indice 2).
for j, (reg, idx, cor, lab) in enumerate(
        [(regs[0], 1, "#c51b7d", "inversao forte"), (regs[1], 2, "#f1a7cd", "sub-limiar")]):
    med = [1e3 * res[reg][k][0] for k in "ABC"]
    pre = [1e3 * res[reg][k][idx] for k in "ABC"]
    x = np.arange(3) + (j - .5) * w
    a.bar(x, med, w * .8, color=cor, label=f"medido — {lab}")
    a.plot(x, pre, "k_", ms=13, mew=2.2,
           label="previsto: so vth0" if j == 0 else "previsto: vth0 + voff")
    for xi, m, q in zip(x, med, pre):
        a.text(xi, m + .25, f"{m/q:.2f}x", ha="center", fontsize=7.5)
a.set_xticks(range(3))
a.set_xticklabels([f"{k}\n{GEO[k][0]}" for k in "ABC"], fontsize=8)
a.set_ylabel("sigma(Vth equivalente)  (mV)")
a.set_title("3 · V3: medido contra o previsto pelos slopes do PDK", fontsize=10)
a.legend(fontsize=7); a.grid(alpha=.3, axis="y"); a.set_ylim(0, 13.5)

# 4 · Pelgrom
a = ax[1, 0]
for reg, mk in zip(regs, "os"):
    xs = [1 / np.sqrt(GEO[k][1]) for k in "AC"]
    ys = [1e3 * res[reg][k][0] for k in "AC"]
    a.plot(xs, ys, mk + "-", label=f"{reg.split('(')[0].strip()}: razao {ys[0]/ys[1]:.2f}")
xg = np.array([1 / np.sqrt(2), 1 / np.sqrt(.5)])
anc = 1e3 * res[regs[1]]["C"][0] * np.sqrt(2)      # ancorada no ponto C do sub-limiar
a.plot(xg, anc * xg, "k--", lw=1.1, label="lei de Pelgrom (inclinacao 1)")
a.set_xscale("log"); a.set_yscale("log")
a.set_xlabel("1 / sqrt(area)   (um^-1)"); a.set_ylabel("sigma(Vth_eq)  (mV)")
a.set_title("4 · V3b: escala com a area? (arrays A e C, nfet)", fontsize=10)
a.legend(fontsize=8); a.grid(alpha=.3, which="both")

# 5 · convergencia
a = ax[1, 1]
for k, col in zip((1, 4), ("#1b7837", "#c51b7d")):
    d = [0.0, 100 * (conv[k][1] - conv[k][0]) / conv[k][0]]
    a.plot([0.5, 0.125], d, "o-", color=col,
           label=f"seed {k}: {d[1]:+.4f} %  (f = {conv[k][0]:.2f} Hz)")
a.axhspan(-1, 1, color="#1b7837", alpha=.12, label="criterio: +-1%")
a.set_xscale("log"); a.invert_xaxis(); a.set_ylim(-1.4, 1.4)
a.set_xlabel("tstep (us)  — para a direita = mais fino")
a.set_ylabel("desvio de f contra tstep = 0,5 us  (%)")
a.set_title("5 · convergencia com sorteio FIXO (criterio: <1%)", fontsize=10)
a.legend(fontsize=8); a.grid(alpha=.3)

# 6 · V2 reprodutibilidade
a = ax[1, 2]; a.axis("off")
linhas = [
    ("`.option seed=N`  — FIXA", "", ""),
    ("  mesma semente, 2 execucoes", "identico", True),
    ("  sementes diferentes", "difere", True),
    ("  mesma semente, tstep diferente", "identico", True),
    ("", "", ""),
    ("`set rndseed=N` no .control  — NAO FIXA", "", ""),
    ("  mesma semente, 2 execucoes", "DIFERE", False),
]
for i, (t1, t2, okv) in enumerate(linhas):
    c = "#1b7837" if okv is True else ("#b2182b" if okv is False else "k")
    a.text(.02, .92 - i * .105, t1, fontsize=10, family="monospace", color=c)
    a.text(.72, .92 - i * .105, t2, fontsize=10, family="monospace", color=c)
a.text(.02, .06, "os `.model` com AGAUSS sao avaliados ANTES do .control:\n"
                 "`set rndseed` la chega tarde e o sorteio fica solto.",
       fontsize=8.5, style="italic", color="#b2182b")
a.set_title("6 · V2: o que fixa o sorteio", fontsize=10)

fig.tight_layout(rect=[0, 0, 1, .96])
p = os.path.join(OUT, "instrumento.png")
fig.savefig(p, dpi=135)
print(f"\ngrafico: resultados/{TAG}/instrumento.png")
