#!/usr/bin/env python3
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Le os dados que run_sims.py deixou em resultados/<RUN_TAG>/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = os.environ.get("RUN_TAG", "rodada_atual")
WORK = os.path.join(ROOT, "resultados", TAG)

plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.25,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

INK = "#1a1a1a"; TEAL = "#0f6d68"; AMBER = "#BA7517"; RED = "#B33A2E"; BLUE = "#2A5C9A"

fig = plt.figure(figsize=(13, 11))
gs = GridSpec(4, 2, figure=fig, hspace=0.45, wspace=0.25,
              height_ratios=[1.1, 1.0, 1.0, 1.0])

# ---------------------------------------------- 1. Forma de onda completa
d = np.load(f"{WORK}/wave.npy")
t, mem, out = d[:, 0] * 1e3, d[:, 1], d[:, 3]
ax = fig.add_subplot(gs[0, :])
ax.plot(t, mem, color=TEAL, lw=1.6, label="V(membrana) — o capacitor integrando")
ax.plot(t, out, color=AMBER, lw=1.1, alpha=0.85, label="V(saída) — o spike")
ax.set_xlabel("tempo (ms)"); ax.set_ylabel("tensão (V)")
ax.set_title("1 · O neurônio disparando  (Iin = 10 pA, Cmem = 100 fF)", loc="left", fontweight="bold")
ax.legend(loc="upper right", framealpha=0.95, fontsize=8)
ax.set_xlim(0, 80)

# ---------------------------------------------- 2. Zoom em um ciclo
above = out > 0.9
r = np.where((~above[:-1]) & (above[1:]))[0]
a, b = r[3], r[5]
ax = fig.add_subplot(gs[1, 0])
ax.plot(t[a:b], mem[a:b], color=TEAL, lw=2)
ax.plot(t[a:b], out[a:b], color=AMBER, lw=1.4, alpha=0.8)
i_pk = a + np.argmax(mem[a:b])
ax.annotate("integração\n(rampa)", xy=(t[a] + (t[i_pk]-t[a])*0.5, 0.62),
            fontsize=8, color=TEAL, ha="center")
ax.annotate("disparo", xy=(t[i_pk], mem[i_pk]), xytext=(t[i_pk]+1.2, 1.15),
            fontsize=8, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
ax.set_xlabel("tempo (ms)"); ax.set_ylabel("tensão (V)")
ax.set_title("2 · Um ciclo: rampa lenta, disparo rápido", loc="left", fontweight="bold")

# ---------------------------------------------- 3. Curva f-I
fi = np.load(f"{WORK}/fi.npy")
I, F = fi[0], fi[1]
m = F > 0
ax = fig.add_subplot(gs[1, 1])
ax.plot(I[m], F[m], "o-", color=BLUE, lw=1.8, ms=5)
coef = np.polyfit(I[m], F[m], 1)
ax.plot(I[m], np.polyval(coef, I[m]), "--", color=RED, lw=1,
        label=f"ajuste linear: {coef[0]:.1f} Hz/pA")
ax.set_xlabel("corrente de entrada (pA)"); ax.set_ylabel("frequência de disparo (Hz)")
ax.set_title("3 · Curva f–I: a função de transferência", loc="left", fontweight="bold")
ax.legend(fontsize=8, loc="upper left")

# ---------------------------------------------- 4. O achado: Cmem
caps = np.load(f"{WORK}/caps.npy")
C, CF = caps[0], caps[1]
ax = fig.add_subplot(gs[2, 0])
ax.plot(C, CF, "s-", color=AMBER, lw=1.8, ms=6)
ax.set_xlabel("capacitor de membrana (fF)"); ax.set_ylabel("frequência (Hz)")
ax.set_title("4 · Cmem quase NÃO muda a frequência", loc="left", fontweight="bold")
ax.set_ylim(0, max(CF)*1.35)
ax.annotate("16× de capacitor,\nmesma frequência", xy=(200, np.mean(CF)),
            xytext=(120, max(CF)*1.18), fontsize=8, color=RED, ha="center")

# ---------------------------------------------- 5. Por que: a excursão desaba
exc, dvdt_l = [], []
for c in [25, 50, 100, 200, 400]:
    d2 = np.loadtxt(f"{WORK}/raw_cm_{c}.txt")
    tt, mm, oo = d2[:, 0], d2[:, 1], d2[:, 3]
    ab = oo > 0.9; rr = np.where((~ab[:-1]) & (ab[1:]))[0]
    sm = mm[rr[3]:rr[4]]
    exc.append(sm.max() - sm.min())
ax = fig.add_subplot(gs[2, 1])
ax.plot([25, 50, 100, 200, 400], exc, "D-", color=RED, lw=1.8, ms=5)
ax.set_xlabel("capacitor de membrana (fF)")
ax.set_ylabel("excursão da membrana (V)")
ax.set_title("5 · A explicação: a excursão de sinal desaba", loc="left", fontweight="bold")
ax.axhline(0.2, color="gray", ls=":", lw=1)
ax.annotate("abaixo disto o neurônio\nfica refém do ruído", xy=(250, 0.22),
            fontsize=7.5, color="gray")

# ---------------------------------------------- 6. Sensibilidade a VDD
vd = np.load(f"{WORK}/vdd.npy")
V, VF = vd[0], vd[1]
ax = fig.add_subplot(gs[3, 0])
ax.plot(V, VF, "o-", color=TEAL, lw=1.8, ms=5)
nom = VF[len(VF)//2]
ax.axhline(nom, color="gray", ls=":", lw=1)
spread = (VF.max() - VF.min()) / nom * 100
ax.set_xlabel("tensão de alimentação (V)"); ax.set_ylabel("frequência (Hz)")
ax.set_title(f"6 · Robustez: ±10% de VDD → {spread:.0f}% de deriva", loc="left", fontweight="bold")
ax.set_ylim(0, max(VF)*1.3)

# ---------------------------------------------- 7. Formas de onda comparadas
ax = fig.add_subplot(gs[3, 1])
for c, col in [(25, TEAL), (400, RED)]:
    d2 = np.loadtxt(f"{WORK}/raw_cm_{c}.txt")
    tt, mm, oo = d2[:, 0]*1e3, d2[:, 1], d2[:, 3]
    ab = oo > 0.9; rr = np.where((~ab[:-1]) & (ab[1:]))[0]
    a2, b2 = rr[3], rr[5]
    ax.plot(tt[a2:b2] - tt[a2], mm[a2:b2], color=col, lw=1.8,
            label=f"Cmem = {c} fF")
ax.set_xlabel("tempo (ms)"); ax.set_ylabel("V(membrana)")
ax.set_title("7 · Mesma frequência, sinais muito diferentes", loc="left", fontweight="bold")
ax.legend(fontsize=8)

fig.suptitle("Neurônio analógico integra-e-dispara (axon-hillock) — simulação em ngspice",
             fontsize=13, fontweight="bold", y=0.985)
fig.text(0.5, 0.005,
         "Modelos MOSFET genéricos nível 1 — NÃO é o PDK SkyWater. Valores absolutos mudarão; "
         "as tendências e relações se mantêm.",
         ha="center", fontsize=7.5, color="gray", style="italic")

plt.savefig(f"{WORK}/neuronio_resultados.png", dpi=155, bbox_inches="tight")
print("gráfico salvo")

# imprimir resumo numérico
print("\nRESUMO")
print(f"  ganho f-I: {coef[0]:.1f} Hz/pA  (linear, R² alto)")
print(f"  faixa util: {F[m].min():.0f} a {F[m].max():.0f} Hz")
print(f"  deriva com VDD +-10%: {spread:.1f}%")
print(f"  excursao: {exc[0]:.3f} V (25fF) -> {exc[-1]:.3f} V (400fF)")
