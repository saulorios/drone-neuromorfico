#!/usr/bin/env python3
"""O pulso aciona o estagio seguinte? Estatica do receptor e o piso numerico."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resultados", "2026-09-07_receptor")
R = os.path.join(OUT, "raw")
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

fig = plt.figure(figsize=(13, 8.6))
gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.26)

# --- 1: transferencia DC + estatica
dc = np.loadtxt(f"{R}/estatica_dc.txt")
v, i, outr = dc[:, 0], np.abs(dc[:, 1]), dc[:, 3]
ax = fig.add_subplot(gs[0, 0])
ax.plot(v, outr, lw=2.2, color=BLUE)
ax.axvline(0.730, color=MUTED, ls=":", lw=1.3)
ax.plot([0.0], [1.8], "o", color=AQUA, ms=11, markeredgecolor=SURF, markeredgewidth=2, zorder=6)
ax.plot([1.6243], [0.0], "o", color=ORANGE, ms=11, markeredgecolor=SURF, markeredgewidth=2, zorder=6)
ax.annotate("out baixo = 0,000 mV\n→ outr = 1,800 V", xy=(0, 1.8), xytext=(0.16, 1.30),
            fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax.annotate("out alto = 1,624 V\n→ outr = 0,000 V", xy=(1.6243, 0), xytext=(0.80, 0.42),
            fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax.text(0.745, 0.95, "transição\n0,730 V", fontsize=8, color=MUTED)
ax.set_xlabel("out (V) — entrada do receptor"); ax.set_ylabel("outr (V) — saída do receptor")
ax.set_title("1 · O receptor comuta trilho a trilho\n     margens: 0,894 V alta, 0,730 V baixa",
             loc="left", fontweight="bold", fontsize=11.5)
ax.set_xlim(0, 1.8); ax.set_ylim(-0.1, 1.95)

# --- 2: corrente estatica do receptor
ax = fig.add_subplot(gs[0, 1])
ax.semilogy(v, np.maximum(i, 1e-14), lw=2.2, color=ORANGE)
ax.axhline(33e-12, color=CRIT, ls="--", lw=1.6)
ax.text(1.77, 4.6e-11, "limiar de aprovação: 33 pA", fontsize=8.5, color=CRIT,
        ha="right", fontweight="bold")
for x, y, c in [(0.0, 0.1325e-12, AQUA), (1.6243, 0.2443e-12, ORANGE)]:
    ax.plot([x], [y], "o", color=c, ms=11, markeredgecolor=SURF, markeredgewidth=2, zorder=6)
ax.annotate("0,133 pA\n0,004% do neurônio", xy=(0, 0.1325e-12), xytext=(0.13, 3e-12),
            fontsize=8.5, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax.annotate("0,244 pA\n0,007%", xy=(1.6243, 0.2443e-12), xytext=(1.02, 2.0e-13),
            fontsize=8.5, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax.set_xlabel("out (V)"); ax.set_ylabel("corrente estática do receptor (A)")
ax.set_title("2 · Estática desprezível nos dois estados\n     (pico de 2,9 µA só na transição)",
             loc="left", fontweight="bold", fontsize=11.5)
ax.set_xlim(0, 1.8); ax.set_ylim(1e-13, 1e-5)

# --- 3: formas de onda
tr = np.loadtxt(f"{R}/tran.txt")
t, o, orr = tr[:, 0]*1e3, tr[:, 3], tr[:, 5]
# zoom num unico spike: ele dura ~0,1 us num periodo de 7 ms
j = np.argmax(o > 0.9)
tc = t[j]
k = (t > tc-0.4e-3) & (t < tc+0.8e-3)
tz = (t[k]-tc)*1e3   # us
ax = fig.add_subplot(gs[1, 0])
ax.axhspan(0.0, 0.730, color=AQUA, alpha=0.07, zorder=0)
ax.axhline(0.730, color=MUTED, ls=":", lw=1.2)
ax.text(0.78, 0.79, "transição do receptor: 0,730 V", fontsize=8, color=MUTED, ha="right")
ax.plot(tz, o[k], lw=2.4, color=BLUE, label="out — saída do neurônio")
ax.plot(tz, orr[k], lw=2, color=ORANGE, alpha=0.92, label="outr — saída do receptor")
ax.set_xlabel("tempo relativo ao disparo (µs)"); ax.set_ylabel("tensão (V)")
ax.set_title("3 · O spike, ampliado: o receptor inverte sem hesitar\n     out sobe em 0,09 µs, desce em 0,14 µs",
             loc="left", fontweight="bold", fontsize=11.5)
ax.legend(fontsize=8.5, loc="center right", framealpha=0.96, edgecolor="#dcdcd8")
ax.set_ylim(-0.12, 1.95)

# --- 4: o piso numerico
ax = fig.add_subplot(gs[1, 1])
rot = ["DC\n(sem integração)", "transiente\nvntol=1e-9", "transiente\nvntol=1e-12"]
val = [0.1325, 1607.0, 428.3]
cor = [AQUA, CRIT, ORANGE]
b = ax.bar(range(3), val, 0.55, color=cor, zorder=3)
ax.set_yscale("log")
for x, y in zip(range(3), val):
    ax.text(x, y*1.35, f"{y:,.4g} pA".replace(",", " "), ha="center",
            fontsize=9, fontweight="bold")
ax.axhline(0.1325, color=AQUA, ls="--", lw=1.4)
ax.text(2.42, 0.155, "o valor físico", fontsize=8.5, color="#0e7a55",
        ha="right", fontweight="bold")
ax.set_xticks(range(3)); ax.set_xticklabels(rot, fontsize=8.5)
ax.set_ylabel("corrente estática medida (pA)")
ax.set_ylim(0.05, 1e4)
ax.set_title("4 · O transiente mede o piso do solver, não o circuito\n     12 000× e 3 200× acima do físico",
             loc="left", fontweight="bold", fontsize=11.5)

fig.suptitle("O pulso aciona o estágio seguinte sem criar curto novo — estática de 0,24 pW contra 6,03 nW",
             fontsize=13.5, fontweight="bold", y=0.975)
fig.text(0.5, 0.028,
         "ngspice 42 · sky130A tt, .temp 27 · receptor: inversor 2:1, W=1/W=2, L=0,5 · "
         "corrente estática medida por ponto de operação DC, não por média de transiente",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
p = f"{OUT}/receptor.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
