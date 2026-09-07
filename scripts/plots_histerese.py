#!/usr/bin/env python3
"""Janela de histerese medida da forma de onda, e o que ela explica (e nao explica)."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resultados", "2026-09-07_histerese")
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

I  = np.array([1, 3, 10, 30, 100], float)
W  = np.array([0.677818, 0.677081, 0.679244, 0.681015, 0.688321])
Vd = np.array([0.54976, 0.54900, 0.55118, 0.55302, 0.56046])
Vm = np.array([-0.12806, -0.12808, -0.12807, -0.12800, -0.12786])
Cap = np.array([137.94, 132.35, 130.50, 129.99, 129.81])
Cre = np.array([129.66, 129.70, 129.72, 129.73, 129.73])
fm = np.array([13.605, 41.687, 139.582, 418.380, 1387.680])
fp = np.array([13.778, 41.219, 135.581, 403.967, 1342.612])

fig = plt.figure(figsize=(13, 8.8))
gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.26)

# --- 1: a janela e o que seria preciso
ax = fig.add_subplot(gs[0, 0])
rel = (W/W[2]-1)*100
ax.axhspan(0, 4.15, color=CRIT, alpha=0.10, zorder=0)
ax.axhline(4.15, color=CRIT, ls="--", lw=1.6)
ax.text(97, 4.45, "+4,15% — o que seria preciso em 1 pA", fontsize=8.5,
        color=CRIT, ha="right", fontweight="bold")
ax.axhline(0, color=MUTED, lw=1)
ax.plot(I, rel, "o-", color=BLUE, lw=2.2, ms=8, markeredgecolor=SURF, markeredgewidth=2)
ax.plot([1], [rel[0]], "o", color=CRIT, ms=11, markeredgecolor=SURF, markeredgewidth=2, zorder=6)
ax.annotate(f"medido em 1 pA: {rel[0]:+.2f}%\ne no sentido ERRADO",
            xy=(1, rel[0]), xytext=(2.0, -2.6), fontsize=8.6, color=CRIT,
            fontweight="bold", arrowprops=dict(arrowstyle="->", color=CRIT, lw=1.1))
ax.set_xscale("log"); ax.set_ylim(-3.4, 5.4)
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("variação da janela (%, ref. 10 pA)")
ax.set_title("1 · A janela varia 1,5% em dois decades — e cresce com Iin",
             loc="left", fontweight="bold", fontsize=11.5)

# --- 2: os dois niveis
ax = fig.add_subplot(gs[0, 1])
ax.plot(I, Vd, "o-", color=BLUE, lw=2.2, ms=8, markeredgecolor=SURF,
        markeredgewidth=2, label="V de disparo")
ax.plot(I, Vm, "s-", color=ORANGE, lw=2.2, ms=7, markeredgecolor=SURF,
        markeredgewidth=2, label="V mínimo após o reset")
ax.axhline(0, color=MUTED, ls=":", lw=1.2)
ax.fill_between(I, Vm, Vd, color=AQUA, alpha=0.10)
ax.text(9, 0.21, "a janela", fontsize=10, color="#0e7a55", fontweight="bold", ha="center")
ax.annotate("fundo fixo: −0,128 V\nvaria 0,16% em 100×",
            xy=(30, -0.128), xytext=(1.6, -0.075), fontsize=8.4, color=ORANGE,
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1))
ax.set_xscale("log")
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("V(mem)  (V)")
ax.set_title("2 · O fundo é fixo; só o topo se move",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="center right", framealpha=0.96, edgecolor="#dcdcd8")

# --- 3: Ctot aparente vs real
ax = fig.add_subplot(gs[1, 0])
ax.plot(I, Cap, "o-", color=CRIT, lw=2.2, ms=8, markeredgecolor=SURF,
        markeredgewidth=2, label="Ctot aparente = Iin / (dV/dt)")
ax.plot(I, Cre, "s-", color=AQUA, lw=2.2, ms=7, markeredgecolor=SURF,
        markeredgewidth=2, label="Ctot real, descontada a fuga")
ax.annotate("+5,70% — mas é a FUGA,\nnão capacitância\n(previsto +5,74%)",
            xy=(1, 137.94), xytext=(1.45, 133.2), fontsize=8.5, color=CRIT,
            fontweight="bold", arrowprops=dict(arrowstyle="->", color=CRIT, lw=1.1))
ax.text(97, 129.0, "129,71 fF · espalhamento 0,05%", fontsize=8.5,
        color="#0e7a55", ha="right", fontweight="bold")
ax.set_xscale("log")
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("Ctot (fF)")
ax.set_title("3 · A variação de Ctot era a fuga disfarçada",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="upper right", framealpha=0.96, edgecolor="#dcdcd8")

# --- 4: a curvatura continua sem explicacao
ax = fig.add_subplot(gs[1, 1])
ax.plot(I, fm/I, "o-", color=BLUE, lw=2.2, ms=8, markeredgecolor=SURF,
        markeredgewidth=2, label="medido")
ax.plot(I, fp/I, "s--", color=MUTED, lw=1.8, ms=7, markeredgecolor=SURF,
        markeredgewidth=1.6, label="modelo das 3 medidas\n(janela + Ctot + fuga)")
ax.annotate("medido CAI em 1 pA\n(−2,53%)", xy=(1, fm[0]/1), xytext=(1.35, 13.455),
            fontsize=8.5, color=BLUE, fontweight="bold", ha="left",
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.1))
ax.annotate("modelo SOBE (+1,62%)", xy=(1, fp[0]/1), xytext=(2.1, 13.86),
            fontsize=8.5, color=MUTED, fontweight="bold", ha="left",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
ax.set_xscale("log")
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("f / Iin  (Hz/pA)")
ax.set_title("4 · A curvatura continua sem explicação:\n     o modelo erra o SINAL",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.3, loc="lower right", framealpha=0.96, edgecolor="#dcdcd8")

fig.suptitle("A janela de histerese NÃO explica a curvatura da f–I — segunda hipótese derrubada",
             fontsize=13.5, fontweight="bold", y=0.975)
fig.text(0.5, 0.028,
         "ngspice 42 · sky130A tt, .temp 27 · janela medida da forma de onda, não inferida · "
         "Ctot medido pela inclinação da rampa · fuga medida por ponto de operação DC",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
p = f"{OUT}/histerese.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
