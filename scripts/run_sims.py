#!/usr/bin/env python3
"""
Bateria de simulacoes do neuronio axon-hillock em ngspice.
Gera dados + graficos.
"""
import os, subprocess, sys, numpy as np

# Caminhos relativos a raiz do projeto (este arquivo vive em scripts/).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ngspice: usa NGSPICE_BIN do ambiente se definido, senao o do PATH.
NG = os.environ.get("NGSPICE_BIN", "ngspice")
ENV = dict(os.environ)
# Saidas brutas vao para resultados/<TAG>/ ; TAG identifica a rodada.
TAG = os.environ.get("RUN_TAG", "rodada_atual")
WORK = os.path.join(ROOT, "resultados", TAG)
os.makedirs(WORK, exist_ok=True)
MODELS_FILE = os.path.join(ROOT, "spice", "models", "generic_l1.mod")

MODELS = open(MODELS_FILE, encoding="utf-8").read()

CORE = """
Vdd vdd 0 {{VDD_V}}
Iin 0 mem DC {{IIN}}
Cmem mem 0 {{CMEM}}
M1p n1  mem vdd vdd PMOS W=2u L=0.5u
M1n n1  mem 0   0   NMOS W=1u L=0.5u
M2p out n1  vdd vdd PMOS W=4u L=0.5u
M2n out n1  0   0   NMOS W=2u L=0.5u
Cfb out mem {{CFB}}
Mrst mem out 0 0 NMOS W=0.5u L=2u
Cload out 0 5f
"""


def run(name, params, tstop, tstep, extra_save="v(mem) v(out)"):
    """Roda uma simulacao transiente e devolve os dados."""
    p = {"VDD_V": "1.8", "CMEM": "100f", "CFB": "20f", "IIN": "10p"}
    p.update(params)
    body = CORE
    for k, v in p.items():
        body = body.replace("{{%s}}" % k, str(v))
    out = f"{WORK}/raw_{name}.txt"
    net = f"""* {name}
{body}
{MODELS}
.ic v(mem)=0 v(out)=0
.control
set filetype=ascii
tran {tstep} {tstop} 0 {tstep} uic
wrdata {out} {extra_save}
.endc
.end
"""
    path = f"{WORK}/cir_{name}.cir"
    open(path, "w").write(net)
    r = subprocess.run([NG, "-b", path], env=ENV, capture_output=True, text=True, timeout=300)
    if not os.path.exists(out):
        return None, r.stderr[-500:]
    return np.loadtxt(out), None


def count_spikes(t, out, thr=0.9):
    """Conta spikes por cruzamento ascendente do limiar."""
    above = out > thr
    rises = np.where((~above[:-1]) & (above[1:]))[0]
    return len(rises), t[rises] if len(rises) else np.array([])


# ============================================================
# EXP 1 - Forma de onda: rampa + disparo
# ============================================================
print("EXP 1: forma de onda ...")
d, err = run("wave", {"IIN": "10p"}, "80m", "2u")
assert d is not None, err
t, mem, out = d[:, 0], d[:, 1], d[:, 3]
n, times = count_spikes(t, out)
print(f"  spikes: {n}")
if n >= 3:
    isi = np.diff(times)
    print(f"  ISI medio: {isi.mean()*1e3:.2f} ms  ->  {1/isi.mean():.1f} Hz")
    print(f"  jitter (desvio do ISI): {isi.std()*1e6:.1f} us")
np.save(f"{WORK}/wave.npy", d)

# ============================================================
# EXP 2 - Curva f-I (frequencia vs corrente de entrada)
# ============================================================
print("EXP 2: curva f-I ...")
currents_pA = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100]
freqs = []
for i in currents_pA:
    tstop = "300m" if i < 5 else ("150m" if i < 20 else "60m")
    d, err = run(f"fi_{i}", {"IIN": f"{i}p"}, tstop, "3u")
    if d is None:
        freqs.append(0.0); continue
    t, out = d[:, 0], d[:, 3]
    n, times = count_spikes(t, out)
    f = 1.0 / np.diff(times).mean() if n >= 3 else 0.0
    freqs.append(f)
    print(f"  Iin={i:4d} pA -> {f:8.1f} Hz  ({n} spikes)")
np.save(f"{WORK}/fi.npy", np.array([currents_pA, freqs]))

# ============================================================
# EXP 3 - Efeito do capacitor de membrana
# ============================================================
print("EXP 3: varredura de Cmem ...")
caps = [25, 50, 100, 200, 400]
cap_freqs = []
for c in caps:
    d, err = run(f"cm_{c}", {"CMEM": f"{c}f", "IIN": "10p"}, "200m", "3u")
    if d is None:
        cap_freqs.append(0.0); continue
    t, out = d[:, 0], d[:, 3]
    n, times = count_spikes(t, out)
    f = 1.0 / np.diff(times).mean() if n >= 3 else 0.0
    cap_freqs.append(f)
    print(f"  Cmem={c:4d} fF -> {f:8.1f} Hz")
np.save(f"{WORK}/caps.npy", np.array([caps, cap_freqs]))

# ============================================================
# EXP 4 - Sensibilidade a VDD (proxy grosseiro de canto de processo)
# ============================================================
print("EXP 4: sensibilidade a VDD ...")
vdds = [1.62, 1.71, 1.80, 1.89, 1.98]
vdd_freqs = []
for v in vdds:
    d, err = run(f"vd_{int(v*100)}", {"VDD_V": v, "IIN": "10p"}, "200m", "3u")
    if d is None:
        vdd_freqs.append(0.0); continue
    t, out = d[:, 0], d[:, 3]
    n, times = count_spikes(t, out, thr=v*0.5)
    f = 1.0 / np.diff(times).mean() if n >= 3 else 0.0
    vdd_freqs.append(f)
    print(f"  VDD={v:.2f} V -> {f:8.1f} Hz")
np.save(f"{WORK}/vdd.npy", np.array([vdds, vdd_freqs]))

print("OK")
