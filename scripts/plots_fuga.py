#!/usr/bin/env python3
"""Fuga no no mem em funcao da tensao de membrana, por ponto de operacao DC."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resultados", "2026-09-07_fuga_mem")
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

d = np.loadtxt(f"{OUT}/raw/fuga_mem.txt")
v, iv, out = d[:, 0], d[:, 1], d[:, 3]
m = out < 0.9
v, L = v[m], -iv[m]*1e15          # fA, positivo = saindo de mem

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

# --- 1: a curva inteira, escala symlog para ver as duas ordens de grandeza
ax1.axhline(0, color=INK, lw=1)
ax1.axvline(0, color=MUTED, ls=":", lw=1.4)
ax1.plot(v, L, lw=2.6, color=BLUE)
ax1.set_yscale("symlog", linthresh=10)
ax1.axhspan(55.4, 62.1, color=AQUA, alpha=0.16, zorder=0)
ax1.text(0.44, 130, "patamar: 55 a 62 fA\nFUGA (contra a integração)", fontsize=8.3,
         color="#0e7a55", ha="right", va="bottom", fontweight="bold")
ax1.text(-0.132, -900, "INJEÇÃO (a favor)\n+3,7 pA em −0,127 V\njunção do dreno do Mrst\nem condução direta",
         fontsize=8.3, color=ORANGE, ha="left", va="center", fontweight="bold")
ax1.text(0.008, -2600, "muda de sinal\naqui", fontsize=8.3, color=INK, ha="left")
ax1.set_xlabel("V(mem)  (V)"); ax1.set_ylabel("corrente saindo de mem (fA)  ·  escala symlog")
ax1.set_xlim(-0.14, 0.46); ax1.set_ylim(-6000, 600)
ax1.set_title("1 · A fuga não é um número: muda de SINAL em mem = 0",
              loc="left", fontweight="bold", fontsize=11.5)

# --- 2: zoom na regiao util, com a forma prevista
ax2.axhspan(55.4, 62.1, color=AQUA, alpha=0.13, zorder=0)
ax2.plot(v, L, lw=2.6, color=BLUE, label="medido (DC)")
ax2.axhline(25.3, color=CRIT, ls="--", lw=1.6, label="25,3 fA inferido da f–I")
ax2.axhline(56.0, color=AQUA, ls=":", lw=1.8, label="56 fA — média na rampa positiva")
VT = 25.852
vv = np.linspace(0.001, 0.45, 200)
ax2.plot(vv, 62.1*(1-np.exp(-vv*1e3/VT)), lw=1.6, color=MUTED, ls="-.",
         label="forma prevista: 1 − e^(−Vds/V_T)")
ax2.plot([0], [0], "o", color=CRIT, ms=10, markeredgecolor=SURF, markeredgewidth=2, zorder=6)
ax2.annotate("zero exato em mem = 0\n(previsto)", xy=(0, 0), xytext=(0.055, 12),
             fontsize=8.3, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax2.set_xlabel("V(mem)  (V)"); ax2.set_ylabel("fuga saindo de mem (fA)")
ax2.set_xlim(-0.01, 0.46); ax2.set_ylim(-3, 78)
ax2.set_title("2 · A forma prevista bate; o patamar é 2,2× o inferido",
              loc="left", fontweight="bold", fontsize=11.5)
ax2.legend(fontsize=8.3, loc="lower right", framealpha=0.96, edgecolor="#dcdcd8")

fig.suptitle("Fuga no nó mem medida diretamente — os 25,3 fA não se confirmam",
             fontsize=13.5, fontweight="bold", y=1.0)
fig.text(0.5, -0.045,
         "ngspice 42 · sky130A tt, .temp 27 · ponto de operação DC com mem forçado · "
         "circuito completo no estado de integração (out baixo até o disparo DC em 0,45 V)",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
plt.tight_layout()
p = f"{OUT}/fuga_mem.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
