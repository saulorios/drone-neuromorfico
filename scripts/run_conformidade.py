#!/usr/bin/env python3
"""
Fome de corrente com CONFORMIDADE FINITA.

Correcao do experimento anterior: fontes de corrente ideais tem conformidade
infinita e empurram o no de source alem do trilho ate o diodo de corpo conduzir.
Aqui cada fonte ganha um resistor em paralelo:
    Rp de sp1 para vdd1      Rn de sn1 para 0
dimensionado para ~0,3 V de queda com o transistor cortado, no ponto nominal de
polarizacao:  R = 0,3 V / IB.  (10 nA -> 30 MOhm)

Rp/Rn sao elementos de BANCADA, nao de projeto: nenhum chip teria 30 MOhm de
resistor. Servem so para dar conformidade finita a uma fonte idealizada.
"""
import os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NG = os.environ.get("NGSPICE_BIN", "ngspice")
OUT_REL = os.path.join("resultados", "2026-09-06_starving_conformidade")
RAW_REL = os.path.join(OUT_REL, "raw")
MODELS_REL = os.path.join("spice", "models", "generic_l1.mod")
OUT, RAW = os.path.join(ROOT, OUT_REL), os.path.join(ROOT, RAW_REL)
os.makedirs(RAW, exist_ok=True)

OPTIONS = """.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1"""

VQUEDA = 0.3          # V de queda alvo no resistor de conformidade


def ngspice_version():
    r = subprocess.run([NG, "--version"], capture_output=True, text=True)
    for ln in (r.stdout + r.stderr).splitlines():
        if "ngspice-" in ln:
            return ln.split("ngspice-")[1].split(":")[0].strip()
    return "desconhecida"


def val(x):
    """'10n' -> 1e-8"""
    mult = {"f":1e-15,"p":1e-12,"n":1e-9,"u":1e-6,"m":1e-3}
    return float(x[:-1])*mult[x[-1]] if x[-1] in mult else float(x)


def inv1(ib):
    if ib is None:
        return ("M1p n1  mem vdd1 vdd1 PMOS W=2u L=0.5u\n"
                "M1n n1  mem 0    0    NMOS W=1u L=0.5u")
    R = VQUEDA / val(ib)
    return (f"Ibp vdd1 sp1 DC {ib}\n"
            f"Rp  sp1  vdd1 {R:.6g}\n"
            f"Ibn sn1  0    DC {ib}\n"
            f"Rn  sn1  0    {R:.6g}\n"
            f"M1p n1  mem sp1 vdd1 PMOS W=2u L=0.5u\n"
            f"M1n n1  mem sn1 0    NMOS W=1u L=0.5u")


def inv2(ib2):
    if ib2 is None:
        return ("M2p out n1  vdd2 vdd2 PMOS W=4u L=0.5u\n"
                "M2n out n1  0    0    NMOS W=2u L=0.5u")
    R = VQUEDA / val(ib2)
    return (f"Ibp2 vdd2 sp2 DC {ib2}\n"
            f"Rp2  sp2  vdd2 {R:.6g}\n"
            f"Ibn2 sn2  0    DC {ib2}\n"
            f"Rn2  sn2  0    {R:.6g}\n"
            f"M2p out n1  sp2 vdd2 PMOS W=4u L=0.5u\n"
            f"M2n out n1  sn2 0    NMOS W=2u L=0.5u")


def run(name, ib="10n", ib2=None, iin="10p", tstop="100m", tstep="0.5u", vdd="1.8"):
    salvar = "v(mem) v(out) v(n1) i(vdd1) i(vdd2)"
    if ib is not None:
        salvar += " v(sp1) v(sn1)"
    if ib2 is not None:
        salvar += " v(sp2) v(sn2)"
    net = f"""* {name}
Vdd1 vdd1 0 {vdd}
Vdd2 vdd2 0 {vdd}
Iin 0 mem DC {iin}
Cmem mem 0 100f
{inv1(ib)}
{inv2(ib2)}
Cfb out mem 20f
Mrst mem out 0 0 NMOS W=0.5u L=2u
Cload out 0 5f
.include {MODELS_REL}
{OPTIONS}
.ic v(mem)=0 v(out)=0
.control
set filetype=ascii
tran {tstep} {tstop} 0 {tstep} uic
wrdata {RAW_REL}/{name}.txt {salvar}
.endc
.end
"""
    open(f"{RAW}/{name}.cir", "w").write(net)
    r = subprocess.run([NG, "-b", os.path.join(RAW_REL, f"{name}.cir")],
                       cwd=ROOT, capture_output=True, text=True, timeout=3600)
    f = f"{RAW}/{name}.txt"
    if not os.path.exists(f):
        return None, (r.stderr or r.stdout)[-800:]
    return np.loadtxt(f), salvar.split()


def col(d, salvar, nome):
    """wrdata emite um par (t, valor) por vetor."""
    return d[:, 2*salvar.index(nome) + 1]


def analyse(d, salvar, vdd=1.8, discard=0.20):
    t = d[:, 0]
    k = t >= t[0] + discard*(t[-1]-t[0])
    tw = t[k]; span = tw[-1]-tw[0]
    g = lambda n: col(d, salvar, n)[k]
    out, n1, i1, i2 = g("v(out)"), g("v(n1)"), g("i(vdd1)"), g("i(vdd2)")
    avg = lambda i: np.trapezoid(np.abs(i), tw)/span
    a1, a2 = avg(i1), avg(i2)
    above = out > 0.5*vdd
    rises = np.where((~above[:-1]) & (above[1:]))[0]
    tm = tw[rises]
    if len(tm) >= 3:
        isi = np.diff(tm); f = 1/isi.mean(); cv = isi.std(ddof=1)/isi.mean()*100
    else:
        f, cv = 0.0, float("nan")
    r = dict(f=f, cv=cv, nspk=len(tm), i1=a1, i2=a2,
             p1=a1*vdd, p2=a2*vdd, ptot=(a1+a2)*vdd,
             outmax=out.max(), n1min=n1.min(), n1max=n1.max())
    for nd in ["v(sp1)","v(sn1)","v(sp2)","v(sn2)"]:
        if nd in salvar:
            v = g(nd); r[nd] = (v.min(), v.max())
    return r
