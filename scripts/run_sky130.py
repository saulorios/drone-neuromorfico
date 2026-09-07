#!/usr/bin/env python3
"""
Neuronio axon-hillock migrado para o PDK SkyWater 130 nm.

Mesma topologia e MESMAS dimensoes da versao nivel 1 (ver
resultados/2026-09-07_migracao_sky130/previsao_pre_registrada.md): a pergunta e
uma comparacao, entao so o modelo do dispositivo muda.

W e L sao numero puro em micrometros (CLAUDE.md §7). Cmem e Cfb ideais.
"""
import os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NG = os.environ.get("NGSPICE_BIN", "ngspice")
OUT_REL = os.path.join("resultados", "2026-09-07_migracao_sky130")
RAW_REL = os.path.join(OUT_REL, "raw")
LIB_REL = os.path.join("spice", "models", "sky130", "sky130A",
                       "libs.tech", "ngspice", "sky130.lib.spice")
OUT, RAW = os.path.join(ROOT, OUT_REL), os.path.join(ROOT, RAW_REL)
os.makedirs(RAW, exist_ok=True)

SALVAR = ["v(mem)", "v(out)", "v(n1)", "v(sp1)", "v(sp2)", "v(rp1)", "v(rp2)",
          "i(vdd1)", "i(vdd2)", "i(vddr)"]

NPRE, PPRE = "sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"


def ngspice_version():
    r = subprocess.run([NG, "--version"], capture_output=True, text=True)
    for ln in (r.stdout + r.stderr).splitlines():
        if "ngspice-" in ln:
            return ln.split("ngspice-")[1].split(":")[0].strip()
    return "desconhecida"


def netlist(name, ib1, ib2, iin, tstop, tstep, corner="tt", temp=27,
            ns_rp1=1.10, ns_rp2=1.05):
    return f"""* {name} - neuronio axon-hillock, sky130, canto {corner}, {temp} C
.lib {LIB_REL} {corner}
.temp {temp}

Vdd1 vdd1 0 1.8
Vdd2 vdd2 0 1.8
Vddr vddr 0 1.8

* --- ramos de referencia do espelho (fora do orcamento por neuronio) ---
Iref1 rp1 0 DC {ib1}
XMref1 rp1 rp1 vddr vddr {PPRE} W=0.5 L=10
Iref2 rp2 0 DC {ib2}
XMref2 rp2 rp2 vddr vddr {PPRE} W=5   L=1

* --- neuronio: 7 transistores + 2 espelhos de saida ---
Iin 0 mem DC {iin}
Cmem mem 0 100f
XMbp1 sp1 rp1 vdd1 vdd1 {PPRE} W=0.5 L=10
XM1p  n1  mem sp1  vdd1 {PPRE} W=2   L=0.5
XM1n  n1  mem 0    0    {NPRE} W=1   L=0.5
XMbp2 sp2 rp2 vdd2 vdd2 {PPRE} W=5   L=1
XM2p  out n1  sp2  vdd2 {PPRE} W=4   L=0.5
XM2n  out n1  0    0    {NPRE} W=2   L=0.5
Cfb out mem 20f
XMrst mem out 0 0 {NPRE} W=0.5 L=2
Cload out 0 5f

.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1
.nodeset v(rp1)={ns_rp1} v(rp2)={ns_rp2}
.ic v(mem)=0 v(out)=0
.control
set filetype=ascii
tran {tstep} {tstop} 0 {tstep} uic
wrdata {RAW_REL}/{name}.txt {' '.join(SALVAR)}
.endc
.end
"""


def run(name, ib1="10n", ib2="3u", iin="10p", tstop="150m", tstep="0.5u", **kw):
    open(f"{RAW}/{name}.cir", "w").write(
        netlist(name, ib1, ib2, iin, tstop, tstep, **kw))
    r = subprocess.run([NG, "-b", os.path.join(RAW_REL, f"{name}.cir")],
                       cwd=ROOT, capture_output=True, text=True, timeout=7200)
    f = f"{RAW}/{name}.txt"
    saida = (r.stdout or "") + (r.stderr or "")
    if not os.path.exists(f):
        linhas = [l for l in saida.splitlines()
                  if not (".cm" in l and "loaded" in l) and l.strip()]
        return None, "\n".join(linhas[-8:])
    return np.loadtxt(f), saida


def col(d, nome):
    return d[:, 2*SALVAR.index(nome) + 1]


def analyse(d, vdd=1.8, discard=0.20):
    t = d[:, 0]
    k = t >= t[0] + discard*(t[-1]-t[0])
    tw = t[k]
    g = lambda n: col(d, n)[k]
    out = g("v(out)")
    above = out > 0.5*vdd
    rises = np.where((~above[:-1]) & (above[1:]))[0]
    if len(rises) >= 3:
        # potencia sobre numero INTEIRO de ciclos (CLAUDE.md §7)
        a, b = rises[0], rises[-1]
        ts = tw[a:b+1]; span = ts[-1]-ts[0]
        pw = lambda n: np.trapezoid(np.abs(g(n)[a:b+1]), ts)/span*vdd
        p1, p2, pr = pw("i(vdd1)"), pw("i(vdd2)"), pw("i(vddr)")
        isi = np.diff(tw[rises]); f = 1/isi.mean(); cv = isi.std(ddof=1)/isi.mean()*100
    else:
        span = tw[-1]-tw[0]
        pw = lambda n: np.trapezoid(np.abs(g(n)), tw)/span*vdd
        p1, p2, pr = pw("i(vdd1)"), pw("i(vdd2)"), pw("i(vddr)")
        f, cv = 0.0, float("nan")
    return dict(f=f, cv=cv, nspk=len(rises), p1=p1, p2=p2, ptot=p1+p2, pref=pr,
                outmax=out.max(), pulso=out.max()/vdd*100,
                trilhos={n: (g(n).min(), g(n).max())
                         for n in ["v(mem)","v(n1)","v(sp1)","v(sp2)","v(rp1)","v(rp2)"]})
