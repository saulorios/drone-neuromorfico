#!/usr/bin/env python3
"""Varredura de Cmem no sky130: o achado central sobrevive ao PDK?"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resultados", "2026-09-07_cmem_sky130")
BLUE, ORANGE, AQUA, YELL = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

d = np.load(f"{OUT}/raw/sweep.npy")
C, F, CV, W, EXC, PUL, CT = (d[:, i] for i in range(7))
A  = np.array([329.8, 226.3, 139.1, 78.5, 42.0, 21.7])
B  = np.array([159.3, 151.2, 139.6, 126.5, 121.8, 131.4])
L1 = np.array([183.1, 173.8, 160.4, 145.4, 140.0, 151.0])

fig = plt.figure(figsize=(13, 8.9))
gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.38)

# --- 1: a discriminacao
ax = fig.add_subplot(gs[0, :])
ax.axvspan(260, 900, color=CRIT, alpha=0.07, zorder=0)
ax.text(300, 330, "regime degenerado\n(excursão < 0,2 V)", fontsize=8.6, color=CRIT,
        fontweight="bold", va="top")
ax.plot(C, A, "^--", color=CRIT, lw=1.7, ms=8, alpha=0.85, label="Modelo A pré-registrado — f ∝ 1/Ctot")
ax.plot(C, B, "v--", color=MUTED, lw=1.7, ms=8, alpha=0.85, label="Modelo B pré-registrado — forma do nível 1")
ax.plot(C, L1, "s:", color=YELL, lw=1.8, ms=7, label="nível 1 (referência)")
ax.plot(C, F, "o-", color=BLUE, lw=2.8, ms=10, markeredgecolor=SURF,
        markeredgewidth=2.2, zorder=6, label="MEDIDO — sky130")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks(C); ax.set_xticklabels([f"{int(c)}" for c in C])
ax.xaxis.set_minor_locator(plt.NullLocator())
ax.set_xlabel("Cmem (fF)"); ax.set_ylabel("frequência (Hz)")
ax.set_title("1 · O Modelo A vence no regime útil — e o achado central NÃO sobrevive",
             loc="left", fontweight="bold", fontsize=12)
ax.legend(fontsize=8.6, loc="lower left", framealpha=0.96, edgecolor="#dcdcd8", ncol=2)
ax.annotate("3,39× em 8× de Cmem\n(nível 1: 1,26×)", xy=(70, 175), xytext=(28, 62),
            fontsize=9, color=BLUE, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.3))
ax.annotate("a subida existe\ne é MAIOR: ×1,74", xy=(800, 253), xytext=(330, 500),
            fontsize=8.8, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))

# --- 2: os dois regimes
ax = fig.add_subplot(gs[1, 0])
ax.axhline(0.2, color=CRIT, ls="--", lw=1.6)
ax.text(820, 0.225, "0,2 V — fronteira de regime", fontsize=8.5, color=CRIT, fontweight="bold", ha="right")
ax.plot(C, EXC, "o-", color=BLUE, lw=2.2, ms=8, markeredgecolor=SURF,
        markeredgewidth=2, label="excursão da membrana (V)")
ax2 = ax.twinx()
ax2.plot(C, CV, "s-", color=ORANGE, lw=2.2, ms=7, markeredgecolor=SURF,
         markeredgewidth=2, label="CV do ISI (%)")
ax2.set_yscale("log"); ax2.set_ylabel("CV do ISI (%)", color=ORANGE, labelpad=2)
ax2.tick_params(axis="y", colors=ORANGE); ax2.grid(False)
ax.set_xscale("log"); ax.set_xticks(C); ax.set_xticklabels([f"{int(c)}" for c in C])
ax.xaxis.set_minor_locator(plt.NullLocator())
ax.set_xlabel("Cmem (fF)"); ax.set_ylabel("excursão da membrana (V)", color=BLUE)
ax.tick_params(axis="y", colors=BLUE)
ax.set_title("2 · A fronteira: excursão cruza 0,2 V,\n     o CV do ISI salta 26×",
             loc="left", fontweight="bold", fontsize=11.5)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, fontsize=8.3, loc="center left", framealpha=0.96, edgecolor="#dcdcd8")

# --- 3: Ctot medido
ax = fig.add_subplot(gs[1, 1])
prev = C + 29.71
ax.plot(C, prev, "-", color=MUTED, lw=2.4, label="previsto: Cmem + 29,71 fF")
ax.plot(C, CT, "o", color=AQUA, ms=10, markeredgecolor=SURF, markeredgewidth=2,
        zorder=6, label="medido (descontada a fuga)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks(C); ax.set_xticklabels([f"{int(c)}" for c in C])
ax.xaxis.set_minor_locator(plt.NullLocator())
ax.set_xlabel("Cmem (fF)"); ax.set_ylabel("Ctot (fF)")
ax.set_title("3 · O parasita de 9,71 fF é constante do circuito\n     erro ≤ 0,10% no regime útil",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="upper left", framealpha=0.96, edgecolor="#dcdcd8")
for i in range(len(C)):
    e = (CT[i]/prev[i]-1)*100
    ax.annotate(f"{e:+.2f}%", (C[i], CT[i]), textcoords="offset points",
                xytext=(6, -13), fontsize=7.6,
                color=INK if abs(e) < 1 else CRIT)

fig.suptitle("Varredura de Cmem no sky130 — o achado central NÃO sobrevive ao PDK",
             fontsize=13.5, fontweight="bold", y=0.975)
fig.text(0.5, 0.025,
         "ngspice 42 · sky130A tt, .temp 27 · IB1 = 10 nA, IB2 = 3 µA, Iin = 10 pA · "
         "limiar de disparo adaptativo (50% da excursão de out) · Ctot com desconto da fuga",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
p = f"{OUT}/cmem_sky130.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
