#!/usr/bin/env python3
"""Figura do experimento de fome de corrente no primeiro inversor."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "resultados", "2026-09-06_starving")
RAW  = os.path.join(OUT, "raw")

# paleta categorica validada (slots 1-3 da paleta de referencia)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"

plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
})

IB     = np.array([1e-9, 10e-9, 100e-9, 1e-6])
P1     = np.array([1.68, 17.39, 176.24, 1736.49])      # nW
P2     = np.array([235.00, 200.95, 196.36, 196.01])    # nW
FREQ   = np.array([46.70, 46.34, 45.75, 45.72])        # Hz
BASE_P1, BASE_P2, BASE_F = 12702.0, 1290.0, 160.35
ALVO = 100.0

fig = plt.figure(figsize=(12.5, 9.2))
gs = GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.24)

# ---------------------------------------------- 1 · orcamento de potencia
ax = fig.add_subplot(gs[0, :])
ax.axhspan(0.5, ALVO, color=AQUA, alpha=0.07, zorder=0)
ax.axhline(ALVO, color=CRIT, ls="--", lw=1.6, zorder=3)
ax.text(1.3e-9, ALVO*1.18, "critério de aceitação: ≤ 100 nW", color=CRIT,
        fontsize=8.5, fontweight="bold", va="bottom")
for y, c, lab, mk in [(P1, BLUE, "1º inversor (com fome de corrente)", "o"),
                      (P2, ORANGE, "2º inversor (sem limitação)", "s"),
                      (P1+P2, AQUA, "total do neurônio", "D")]:
    ax.plot(IB, y, mk+"-", color=c, lw=2, ms=8, label=lab,
            markeredgecolor=SURF, markeredgewidth=2, zorder=5)
ax.plot([2e-9], [BASE_P1+BASE_P2], "*", color=MUTED, ms=15, zorder=5)
ax.annotate("linha de base\n(sem fome de corrente)\n13 992 nW",
            xy=(2e-9, BASE_P1+BASE_P2), xytext=(3.2e-9, 5200),
            fontsize=8, color=MUTED, ha="left",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
ax.annotate("mínimo: 218 nW\n2,2× acima do alvo", xy=(10e-9, 218.35),
            xytext=(2.4e-8, 700), fontsize=8.5, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1.1))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("corrente de polarização do 1º inversor, IB (A)")
ax.set_ylabel("potência média (nW)")
ax.set_title("1 · O orçamento de potência: o 1º estágio despenca, o 2º vira o piso",
             loc="left", fontweight="bold", fontsize=11)
ax.legend(loc="lower right", fontsize=8.5, framealpha=0.96, edgecolor="#dcdcd8")
ax.set_ylim(0.7, 4e4)

# ---------------------------------------------- 2 · curva f-I
ax = fig.add_subplot(gs[1, 0])
I_s = np.array([1, 3, 10, 30, 100]); F_s = np.array([4.81, 14.21, 46.34, 136.13, 443.34])
I_b = np.array([1, 3, 10, 30, 100]); F_b = 16.0 * I_b
ax.plot(I_b, F_b, "o--", color=MUTED, lw=1.6, ms=6, markeredgecolor=SURF,
        markeredgewidth=1.5, label="linha de base — 16,0 Hz/pA")
ax.plot(I_s, F_s, "o-", color=BLUE, lw=2, ms=8, markeredgecolor=SURF,
        markeredgewidth=2, label="IB = 10 nA — 4,42 Hz/pA")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("corrente de entrada, Iin (pA)"); ax.set_ylabel("frequência de disparo (Hz)")
ax.set_title("2 · A curva f–I continua linear (R² = 0,99996),\n     mas o ganho cai 3,6×",
             loc="left", fontweight="bold", fontsize=11)
ax.legend(fontsize=8.5, loc="upper left", framealpha=0.96, edgecolor="#dcdcd8")

# ---------------------------------------------- 3 · o mecanismo
ax = fig.add_subplot(gs[1, 1])

def transicao(arq, col=5, meia=0.40e-3):
    """Recorta em torno do cruzamento DESCENDENTE de n1 por 1,35 V."""
    d = np.loadtxt(arq)
    t, v = d[:, 0], d[:, col]
    k = t >= t[0] + 0.3*(t[-1]-t[0])          # longe do transiente inicial
    t, v = t[k], v[k]
    desce = np.where((v[:-1] >= 1.35) & (v[1:] < 1.35))[0]
    c = desce[len(desce)//2]                   # uma transicao do meio da corrida
    m = (t >= t[c]-meia) & (t <= t[c]+meia)
    return (t[m]-t[c])*1e6, v[m]

ax.axhspan(0.45, 1.35, color=CRIT, alpha=0.09, zorder=0)
ax.text(385, 0.70, "janela em que os DOIS\ntransistores conduzem",
        color=CRIT, fontsize=8, ha="right", va="center", zorder=4)
xb, yb = transicao(f"{RAW}/base_ts0.5u.txt")
xs, ys = transicao(f"{RAW}/ib_10n.txt")
ax.plot(xb, yb, lw=2, color=MUTED, label="linha de base — 25 µs/ciclo na janela")
ax.plot(xs, ys, lw=2.4, color=BLUE, label="IB = 10 nA — 207 µs/ciclo na janela")
ax.axhline(1.8, color=INK, ls=":", lw=1)
ax.text(392, 1.84, "VDD = 1,8 V (n1 ultrapassa: artefato da fonte ideal)", fontsize=7.5, color=INK, ha="right")
ax.set_xlim(-400, 400); ax.set_ylim(0.55, 2.42)
ax.set_xlabel("tempo relativo ao cruzamento de 1,35 V (µs)")
ax.set_ylabel("V(n1) — entrada do 2º inversor (V)")
ax.set_title("3 · Por que o 2º estágio gasta:\n     a travessia de n1 fica 8,1× mais lenta",
             loc="left", fontweight="bold", fontsize=11)
ax.legend(fontsize=8.2, loc="upper left", framealpha=0.96, edgecolor="#dcdcd8")

fig.suptitle("Fome de corrente no 1º inversor — o consumo cai 64×, mas para em 218 nW",
             fontsize=13.5, fontweight="bold", y=0.975, x=0.5)
fig.text(0.5, 0.012,
         "ngspice 41 · modelos nível 1 · Iin = 10 pA salvo indicação · fontes de polarização IDEAIS "
         "(violam os trilhos: sp1 chega a 2,14 V e sn1 a −0,36 V — ver pendências)",
         ha="center", fontsize=7.5, color=MUTED, style="italic")

p = f"{OUT}/starving_resultados.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
