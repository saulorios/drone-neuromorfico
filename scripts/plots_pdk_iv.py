#!/usr/bin/env python3
"""Validacao do sky130: curva I-V do nfet_01v8 isolado e a armadilha do W/L."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resultados", "2026-09-07_etapa1_pdk")
BLUE, ORANGE, AQUA, YELL = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

d = np.loadtxt(f"{OUT}/raw/iv_vgs.txt")
vg = d[:, 0]
nomes = ["W=0,42 L=0,15 (mínimo)", "W=1 L=0,15", "W=2 L=0,15",
         "W=1 L=0,5", "W=0,5 L=2  (Mrst)"]
cores = [AQUA, BLUE, ORANGE, YELL, CRIT]
I = [np.abs(d[:, 2*i+1]) for i in range(5)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.0))

# --- 1: Id-Vgs em escala linear (regiao de inversao forte)
for y, n, c in zip(I, nomes, cores):
    ax1.plot(vg, y*1e6, lw=2, color=c, label=n)
ax1.axhspan(400, 700, color=AQUA, alpha=0.10, zorder=0)
ax1.axhline(501.05, color=BLUE, ls=":", lw=1.2)
ax1.plot([1.8], [501.05], "o", color=BLUE, ms=9, markeredgecolor=SURF, markeredgewidth=2, zorder=6)
ax1.annotate("501,0 µA\n(previsto: 400–700 µA)", xy=(1.8, 501), xytext=(0.62, 640),
             fontsize=8.5, color=INK, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=INK, lw=1))
ax1.set_xlabel("Vgs (V)   ·   Vds = 1,8 V"); ax1.set_ylabel("Id (µA)")
ax1.set_title("1 · Inversão forte: a previsão pré-registrada bate",
              loc="left", fontweight="bold", fontsize=11.5)
ax1.legend(fontsize=8, loc="upper left", framealpha=0.96, edgecolor="#dcdcd8")
ax1.set_xlim(0, 1.8)

# --- 2: Id-Vgs em log (sub-limiar) — a previsao da zona morta
for y, n, c in zip(I, nomes, cores):
    ax2.semilogy(vg, np.maximum(y, 1e-18), lw=2, color=c, label=n)
ax2.axhspan(1e-16, 1e-14, color=AQUA, alpha=0.12, zorder=0)
ax2.text(1.76, 3.0e-15, "minha previsão:\n0,1 a 10 fA", fontsize=8, color="#0e7a55",
         ha="right", va="center", fontweight="bold")
ax2.plot([0], [84.7e-15], "o", color=CRIT, ms=10, markeredgecolor=SURF,
         markeredgewidth=2, zorder=6)
ax2.annotate("Mrst com porta em 0 V:\n84,7 fA — 8,5× acima\ndo topo da previsão",
             xy=(0, 84.7e-15), xytext=(0.30, 2.5e-12), fontsize=8.5, color=CRIT,
             fontweight="bold", arrowprops=dict(arrowstyle="->", color=CRIT, lw=1.1))
ax2.axhline(1e-12, color=INK, ls="--", lw=1.3)
ax2.text(1.76, 1.45e-12, "1 pA — a menor corrente de entrada da faixa útil",
         fontsize=8, color=INK, ha="right")
ax2.set_xlabel("Vgs (V)   ·   Vds = 1,8 V"); ax2.set_ylabel("Id (A)")
ax2.set_ylim(1e-16, 3e-3); ax2.set_xlim(0, 1.8)
ax2.set_title("2 · Sub-limiar: a fuga é 8,5× maior que eu previ\n     (91,3 mV/década)",
              loc="left", fontweight="bold", fontsize=11.5)

fig.suptitle("Validação do PDK SkyWater 130 nm — nfet_01v8 isolado, canto tt, 27 °C",
             fontsize=13.5, fontweight="bold", y=1.0)
fig.text(0.5, -0.04,
         "ngspice 42 · sky130A via volare (subconjunto ngspice, 253 MB) · "
         "W e L são número puro em micrômetros; escrever W=1u aborta a simulação",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
plt.tight_layout()
p = f"{OUT}/validacao_pdk.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
