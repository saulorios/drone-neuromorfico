#!/usr/bin/env python3
"""Figura de diagnostico: por que o grampo de conformidade nao segura os trilhos."""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_conformidade import RAW, OUT, col, val, VQUEDA

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CRIT, INK, MUTED, SURF = "#d03b3b", "#0b0b0b", "#6b6b6b", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.18, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9c9c6", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURF, "axes.facecolor": SURF})

S = 'v(mem) v(out) v(n1) i(vdd1) i(vdd2) v(sp1) v(sn1)'.split()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8))

# --- painel 1: sp1/sn1 saindo dos trilhos, IB = 10 nA
d = np.loadtxt(f"{RAW}/v1_10n.txt")
t = d[:, 0]; k = (t > 0.040) & (t < 0.070)
tt = (t[k]-t[k][0])*1e3
ax1.axhspan(0, 1.8, color=AQUA, alpha=0.07, zorder=0)
ax1.axhline(1.8, color=INK, ls=":", lw=1.2); ax1.axhline(0, color=INK, ls=":", lw=1.2)
ax1.text(0.15, 1.86, "trilho superior — VDD = 1,8 V", fontsize=8, color=INK)
ax1.text(0.15, -0.30, "trilho inferior — 0 V", fontsize=8, color=INK)
ax1.plot(tt, col(d, S, "v(sp1)")[k], lw=2, color=BLUE, label="V(sp1) — source de M1p")
ax1.plot(tt, col(d, S, "v(sn1)")[k], lw=2, color=ORANGE, label="V(sn1) — source de M1n")
ax1.axhline(2.1, color=CRIT, ls="--", lw=1.3)
ax1.axhline(-0.3, color=CRIT, ls="--", lw=1.3)
ax1.text(29.5, 2.16, "previsto: VDD + IB·R = 2,1 V", fontsize=8, color=CRIT, ha="right")
ax1.text(29.5, -0.52, "previsto: −IB·R = −0,3 V", fontsize=8, color=CRIT, ha="right")
ax1.set_ylim(-0.75, 2.45); ax1.set_xlim(0, 30)
ax1.set_xlabel("tempo (ms)"); ax1.set_ylabel("tensão (V)")
ax1.set_title("1 · Os nós de source continuam saindo dos trilhos\n     (IB = 10 nA, R = 30 MΩ)",
              loc="left", fontweight="bold", fontsize=11)
ax1.legend(fontsize=8.5, loc="center right", framealpha=0.96, edgecolor="#dcdcd8")

# --- painel 2: o resistor entrega mais corrente que a fonte
IBs = ["1n", "10n", "100n", "1u"]
med, pico = [], []
for ib in IBs:
    dd = np.loadtxt(f"{RAW}/v1_{ib}.txt"); tt2 = dd[:, 0]
    kk = tt2 >= tt2[0]+0.2*(tt2[-1]-tt2[0]); tw = tt2[kk]
    iR = np.abs((1.8 - col(dd, S, "v(sp1)")[kk]) / (VQUEDA/val(ib)))
    med.append(np.trapezoid(iR, tw)/(tw[-1]-tw[0]) / val(ib))
    pico.append(iR.max()/val(ib))
x = np.arange(len(IBs))
ax2.axhline(1.0, color=CRIT, ls="--", lw=1.5)
ax2.text(-0.42, 1.10, "a própria fonte de corrente (1×)", fontsize=8.5, color=CRIT, ha="left")
ax2.bar(x-0.19, med,  0.36, color=BLUE,   label="média no ciclo", zorder=3)
ax2.bar(x+0.19, pico, 0.36, color=ORANGE, label="pico", zorder=3)
for xi, v in zip(x-0.19, med):  ax2.text(xi, v+0.07, f"{v:.2f}×", ha="center", fontsize=8)
for xi, v in zip(x+0.19, pico): ax2.text(xi, v+0.07, f"{v:.2f}×", ha="center", fontsize=8)
ax2.set_xticks(x); ax2.set_xticklabels([f"IB = {i}" for i in IBs])
ax2.set_ylabel("corrente pelo resistor ÷ IB")
ax2.set_ylim(0, 4.0)
ax2.set_title("2 · O resistor de conformidade entrega até 3,4× a\n     corrente da fonte — a limitação deixa de existir",
              loc="left", fontweight="bold", fontsize=11)
ax2.legend(fontsize=8.5, loc="upper right", framealpha=0.96, edgecolor="#dcdcd8")

fig.suptitle("Validação do testbench REPROVA: o resistor em paralelo não grampeia nos trilhos",
             fontsize=13, fontweight="bold", y=1.005)
fig.text(0.5, -0.05, "ngspice 41 · modelos nível 1 · Iin = 10 pA · R = 0,3 V / IB",
         ha="center", fontsize=7.5, color=MUTED, style="italic")
plt.tight_layout()
p = f"{OUT}/validacao_testbench.png"
plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
print("figura salva:", p)
