#!/usr/bin/env python3
"""Curva f-I no ponto de operacao do espelho assimetrico."""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_fi_espelho import RAW, OUT, SALVAR, col

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

I = np.array([1,2,3,5,7,10,15,20,30,50,70,100], float)
F = np.array([13.734,27.581,41.424,69.105,96.780,138.279,
              207.410,276.519,414.632,690.580,966.166,1378.943])
P = np.array([80.50,81.48,81.93,83.24,84.19,85.37,
              87.56,89.14,92.50,99.08,104.22,112.38])
m, c = np.polyfit(I, F, 1); pred = m*I + c
r2 = 1-((F-pred)**2).sum()/((F-F.mean())**2).sum()
lm, lc = np.polyfit(np.log10(I), np.log10(F), 1)

fig = plt.figure(figsize=(13, 8.6))
gs = fig.add_gridspec(2, 2, hspace=0.36, wspace=0.24, height_ratios=[1.15, 1])

# --- 1: curva f-I
ax = fig.add_subplot(gs[0, :])
xs = np.logspace(0, 2, 200)
ax.plot(xs, m*xs+c, "--", color=MUTED, lw=1.4,
        label=f"ajuste linear: f = {m:.3f}·Iin {c:+.3f} Hz   (R² = {r2:.8f})")
ax.plot(I, F, "o", color=BLUE, ms=9, markeredgecolor=SURF, markeredgewidth=2,
        label="medido — 12 pontos, ngspice 42", zorder=5)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("corrente de entrada, Iin (pA)"); ax.set_ylabel("frequência de disparo (Hz)")
ax.set_title("1 · A curva f–I sobrevive: linear, pela origem, expoente 1,0005",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.8, loc="upper left", framealpha=0.96, edgecolor="#dcdcd8")
ax.text(0.985, 0.06,
        f"expoente log–log = {lm:.4f}   (proporcionalidade exata = 1)\n"
        f"zona morta implícita = −22,8 fA   (44× abaixo do menor ponto medido)\n"
        f"ganho = {m:.2f} Hz/pA   (linha de base sem fome de corrente: 16,0)",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color=INK,
        bbox=dict(boxstyle="round,pad=0.5", fc=SURF, ec="#dcdcd8"))

# --- 2: residuos
ax = fig.add_subplot(gs[1, 0])
res = (F-pred)/F*100
ax.axhline(0, color=MUTED, lw=1)
ax.axhspan(-1, 1, color=AQUA, alpha=0.10, zorder=0)
ax.plot(I, res, "o-", color=ORANGE, lw=1.6, ms=7, markeredgecolor=SURF, markeredgewidth=1.8)
ax.annotate("−2,73%\n(o menor ponto, 1 pA)", xy=(1, res[0]), xytext=(2.1, -2.35),
            fontsize=8, color=INK,
            arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax.text(88, 0.62, "±1%", fontsize=8, color=AQUA, ha="right", fontweight="bold")
ax.set_xscale("log")
ax.set_xlabel("corrente de entrada, Iin (pA)"); ax.set_ylabel("resíduo (% do valor medido)")
ax.set_title("2 · Resíduos: só o ponto de 1 pA sai de ±1%",
             loc="left", fontweight="bold", fontsize=11.5)

# --- 3: potencia
ax = fig.add_subplot(gs[1, 1])
ax.axhspan(60, 100, color=AQUA, alpha=0.09, zorder=0)
ax.axhline(100, color=CRIT, ls="--", lw=1.6)
ax.plot(I, P, "o-", color=BLUE, lw=2, ms=7, markeredgecolor=SURF, markeredgewidth=1.8)
ax.axvline(54, color=CRIT, ls=":", lw=1.4)
ax.text(56, 68, "cruza os 100 nW\nem Iin ≈ 54 pA", fontsize=8.5, color=CRIT, ha="left")
ax.text(1.15, 101.5, "critério: ≤ 100 nW", fontsize=8.5, color=CRIT, fontweight="bold")
ax.plot([10], [85.37], "*", color=ORANGE, ms=17, zorder=6, markeredgecolor=SURF,
        markeredgewidth=1.2)
ax.annotate("ponto nominal\n85,4 nW", xy=(10, 85.37), xytext=(1.15, 91.5),
            fontsize=8.5, color=INK,
            arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax.set_xscale("log"); ax.set_ylim(60, 120)
ax.set_xlabel("corrente de entrada, Iin (pA)"); ax.set_ylabel("potência por neurônio (nW)")
ax.set_title("3 · Achado novo: o orçamento estoura acima de ~54 pA",
             loc="left", fontweight="bold", fontsize=11.5)

fig.suptitle("Curva f–I com fome de corrente assimétrica  ·  IB1 = 10 nA, IB2 = 3 µA",
             fontsize=13.5, fontweight="bold", y=0.975)
fig.text(0.5, 0.02,
         "ngspice 42 · modelos nível 1 · potência medida sobre número inteiro de ciclos · "
         "ramo de referência do espelho (5,42 µW) fora do orçamento por neurônio",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
p = f"{OUT}/fi_espelho.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
