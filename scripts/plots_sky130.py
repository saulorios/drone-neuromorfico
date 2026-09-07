#!/usr/bin/env python3
"""Migracao do neuronio para o sky130: comparacao com o nivel 1."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resultados", "2026-09-07_migracao_sky130")
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

I = np.array([1,2,3,5,7,10,15,20,30,50,70,100], float)
# sky130 (esta rodada)
F = np.array([13.605,27.667,41.687,69.686,97.660,139.582,
              209.386,279.115,418.372,696.202,973.316,1387.685])
P = np.array([4.30,4.66,5.00,5.35,5.64,6.03,6.71,7.72,8.32,9.81,11.18,13.67])
PU = np.array([88.39,88.47,88.53,88.64,88.73,88.84,89.01,89.14,89.38,89.74,90.03,90.37])
# nivel 1 (rodada anterior)
F1 = np.array([13.734,27.581,41.424,69.105,96.780,138.279,
               207.410,276.519,414.632,690.580,966.166,1378.943])
P1 = np.array([80.50,81.48,81.93,83.24,84.19,85.37,87.56,89.14,92.50,99.08,104.22,112.38])

fig = plt.figure(figsize=(13, 8.8))
gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.25)

# --- 1: f-I sobreposta
ax = fig.add_subplot(gs[0, 0])
ax.plot(I, F1, "s--", color=MUTED, lw=1.5, ms=6, markeredgecolor=SURF,
        markeredgewidth=1.5, label="nível 1 — 13,794 Hz/pA")
ax.plot(I, F, "o-", color=BLUE, lw=2, ms=7, markeredgecolor=SURF,
        markeredgewidth=1.8, label="sky130 tt 27 °C — 13,886 Hz/pA")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("frequência (Hz)")
ax.set_title("1 · A curva f–I é a mesma: ganho difere 0,7%",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="upper left", framealpha=0.96, edgecolor="#dcdcd8")

# --- 2: residuos
ax = fig.add_subplot(gs[0, 1])
m, c = np.polyfit(I, F, 1); res = (F-(m*I+c))/F*100
m1, c1 = np.polyfit(I, F1, 1); res1 = (F1-(m1*I+c1))/F1*100
ax.axhline(0, color=MUTED, lw=1); ax.axhspan(-1, 1, color=AQUA, alpha=0.10, zorder=0)
ax.plot(I, res1, "s--", color=MUTED, lw=1.5, ms=6, label="nível 1 (máx 2,73%)")
ax.plot(I, res, "o-", color=ORANGE, lw=2, ms=7, markeredgecolor=SURF,
        markeredgewidth=1.8, label="sky130 (máx 6,68%)")
ax.annotate("a fuga sub-limiar\naparece aqui: 25 fA",
            xy=(1, res[0]), xytext=(2.4, -5.6), fontsize=8.3, color=CRIT,
            fontweight="bold", arrowprops=dict(arrowstyle="->", color=CRIT, lw=1))
ax.set_xscale("log")
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("resíduo (% do medido)")
ax.set_title("2 · O único desvio real está em 1 pA",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="lower right", framealpha=0.96, edgecolor="#dcdcd8")

# --- 3: consumo
ax = fig.add_subplot(gs[1, 0])
ax.axhline(100, color=CRIT, ls="--", lw=1.6)
ax.text(1.15, 108, "orçamento: 100 nW", fontsize=8.5, color=CRIT, fontweight="bold")
ax.plot(I, P1, "s--", color=MUTED, lw=1.5, ms=6, label="nível 1 — estoura em 54 pA")
ax.plot(I, P, "o-", color=BLUE, lw=2.2, ms=7, markeredgecolor=SURF,
        markeredgewidth=1.8, label="sky130 — 4,3 a 13,7 nW")
ax.axvline(54, color=MUTED, ls=":", lw=1.3)
ax.annotate("o teto de 54 pA era\nartefato do nível 1", xy=(54, 40), xytext=(4.5, 25),
            fontsize=8.5, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("potência por neurônio (nW)")
ax.set_title("3 · Consumo 14× menor — e o teto da faixa some",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="lower right", framealpha=0.96, edgecolor="#dcdcd8")

# --- 4: o preco — o pulso
ax = fig.add_subplot(gs[1, 1])
ax.axhspan(90, 93, color=AQUA, alpha=0.12, zorder=0)
ax.axhline(90, color=CRIT, ls="--", lw=1.6)
ax.text(1.15, 90.35, "critério: ≥ 90% de VDD", fontsize=8.5, color=CRIT, fontweight="bold")
ax.axhline(92.22, color=MUTED, ls=":", lw=1.4)
ax.text(97, 92.42, "nível 1: 92,2%", fontsize=8.3, color=MUTED, ha="right")
ax.plot(I, PU, "o-", color=ORANGE, lw=2.2, ms=7, markeredgecolor=SURF, markeredgewidth=1.8)
ax.plot([10], [88.84], "*", color=CRIT, ms=17, zorder=6,
        markeredgecolor=SURF, markeredgewidth=1.2)
ax.annotate("ponto nominal: 88,84%\nREPROVA", xy=(10, 88.84), xytext=(1.5, 89.6),
            fontsize=8.5, color=CRIT, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=CRIT, lw=1))
ax.set_xscale("log"); ax.set_ylim(88.0, 93)
ax.set_xlabel("Iin (pA)"); ax.set_ylabel("pulso de saída (% de VDD)")
ax.set_title("4 · O preço: o pulso cai abaixo de 90%",
             loc="left", fontweight="bold", fontsize=11.5)

fig.suptitle("Neurônio migrado para o sky130 — mesma f–I, 14× menos consumo, pulso reprovado",
             fontsize=13.5, fontweight="bold", y=0.975)
fig.text(0.5, 0.03,
         "ngspice 42 · sky130A canto tt, .temp 27 · mesmas dimensões do nível 1 · "
         "espelhos verificados: 9,991 nA e 2,984 µA contra 10 nA e 3 µA programados",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
p = f"{OUT}/migracao_sky130.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
