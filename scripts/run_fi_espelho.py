#!/usr/bin/env python3
"""
Curva f-I no ponto de operacao do espelho assimetrico: IB1 = 10 nA, IB2 = 3 uA.

Reconstrucao do "Resultado 3" de resultados/2026-09-06_espelho/espelho.md:
fome de corrente so no PMOS, nos DOIS estagios. O NMOS de cada inversor vai
direto ao terra. Espelho do 2o estagio largo (W = 5 um, L = 1 um) para nao
roubar excursao do pulso.

O ramo de referencia fica em alimentacao propria (vddr) e NAO entra no
orcamento por neuronio: num chip real ele e compartilhado entre neuronios.
"""
import os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NG = os.environ.get("NGSPICE_BIN", "ngspice")
OUT_REL = os.path.join("resultados", "2026-09-07_fi_espelho")
RAW_REL = os.path.join(OUT_REL, "raw")
MODELS_REL = os.path.join("spice", "models", "generic_l1.mod")
OUT, RAW = os.path.join(ROOT, OUT_REL), os.path.join(ROOT, RAW_REL)
os.makedirs(RAW, exist_ok=True)

SALVAR = ["v(mem)", "v(out)", "v(n1)", "v(sp1)", "v(sp2)",
          "v(rp1)", "v(rp2)", "i(vdd1)", "i(vdd2)", "i(vddr)"]


def ngspice_version():
    r = subprocess.run([NG, "--version"], capture_output=True, text=True)
    for ln in (r.stdout + r.stderr).splitlines():
        if "ngspice-" in ln:
            return ln.split("ngspice-")[1].split(":")[0].strip()
    return "desconhecida"


def val(x):
    """'10n' -> 1e-8 ; aceita float."""
    if not isinstance(x, str):
        return float(x)
    m = {"f":1e-15,"p":1e-12,"n":1e-9,"u":1e-6,"m":1e-3}
    return float(x[:-1])*m[x[-1]] if x[-1] in m else float(x)


def vgate(ib, wl, vdd=1.8, kp=45e-6, vto=0.45):
    """Tensao do no de referencia do espelho PMOS, para o .nodeset."""
    return vdd - (vto + (2*val(ib)/(kp*wl))**0.5)


def netlist(name, ib1, ib2, iin, tstop, tstep, nodeset=True):
    ns = ""
    if nodeset:
        ns = (f".nodeset v(rp1)={vgate(ib1, 0.5/10):.4f} "
              f"v(rp2)={vgate(ib2, 5.0/1.0):.4f}\n")
    return f"""* {name} - espelho assimetrico (so PMOS) nos dois estagios
Vdd1 vdd1 0 1.8
Vdd2 vdd2 0 1.8
Vddr vddr 0 1.8

* --- ramos de referencia (compartilhados num chip real; fora do orcamento) ---
Iref1 rp1 0 DC {ib1}
Mref1 rp1 rp1 vddr vddr PMOS W=0.5u L=10u
Iref2 rp2 0 DC {ib2}
Mref2 rp2 rp2 vddr vddr PMOS W=5u L=1u

* --- neuronio ---
Iin 0 mem DC {iin}
Cmem mem 0 100f
Mbp1 sp1 rp1 vdd1 vdd1 PMOS W=0.5u L=10u
M1p  n1  mem sp1  vdd1 PMOS W=2u L=0.5u
M1n  n1  mem 0    0    NMOS W=1u L=0.5u
Mbp2 sp2 rp2 vdd2 vdd2 PMOS W=5u L=1u
M2p  out n1  sp2  vdd2 PMOS W=4u L=0.5u
M2n  out n1  0    0    NMOS W=2u L=0.5u
Cfb out mem 20f
Mrst mem out 0 0 NMOS W=0.5u L=2u
Cload out 0 5f

.include {MODELS_REL}
.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1
{ns}.ic v(mem)=0 v(out)=0
.control
set filetype=ascii
tran {tstep} {tstop} 0 {tstep} uic
wrdata {RAW_REL}/{name}.txt {' '.join(SALVAR)}
.endc
.end
"""


def run(name, ib1="10n", ib2="3u", iin="10p", tstop="150m", tstep="0.5u", nodeset=True):
    open(f"{RAW}/{name}.cir", "w").write(
        netlist(name, ib1, ib2, iin, tstop, tstep, nodeset))
    r = subprocess.run([NG, "-b", os.path.join(RAW_REL, f"{name}.cir")],
                       cwd=ROOT, capture_output=True, text=True, timeout=3600)
    f = f"{RAW}/{name}.txt"
    if not os.path.exists(f):
        return None, (r.stderr or r.stdout)[-600:]
    return np.loadtxt(f), (r.stderr or "")


def col(d, nome):
    return d[:, 2*SALVAR.index(nome) + 1]


def analyse(d, vdd=1.8, discard=0.20):
    t = d[:, 0]
    k = t >= t[0] + discard*(t[-1]-t[0])
    tw = t[k]; span = tw[-1]-tw[0]
    g = lambda n: col(d, n)[k]
    out = g("v(out)")
    avg = lambda i: np.trapezoid(np.abs(i), tw)/span
    a1, a2, ar = avg(g("i(vdd1)")), avg(g("i(vdd2)")), avg(g("i(vddr)"))
    above = out > 0.5*vdd
    rises = np.where((~above[:-1]) & (above[1:]))[0]
    tm = tw[rises]
    if len(tm) >= 3:
        isi = np.diff(tm); f = 1/isi.mean(); cv = isi.std(ddof=1)/isi.mean()*100
    else:
        f, cv = 0.0, float("nan")
    return dict(f=f, cv=cv, nspk=len(tm),
                p1=a1*vdd, p2=a2*vdd, ptot=(a1+a2)*vdd, pref=ar*vdd,
                outmax=out.max(), pulso=out.max()/vdd*100,
                trilhos={n: (g(n).min(), g(n).max())
                         for n in ["v(mem)","v(n1)","v(sp1)","v(sp2)","v(rp1)","v(rp2)"]})
