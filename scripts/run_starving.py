#!/usr/bin/env python3
"""
Etapa 0-b: o primeiro inversor com fome de corrente ("current-starved").

Pergunta: limitar a corrente do primeiro inversor derruba o consumo para
<= 100 nW sem destruir a curva f-I?

Nao altera Cmem, Cfb, Wrst nem dimensao de transistor algum. Duas fontes de
1,8 V independentes, uma por estagio, para medir cada estagio separadamente.
Fontes de polarizacao IDEAIS (nao transistores): os modelos nivel 1 nao tem
conducao sub-limiar e um transistor de polarizacao em nA daria artefato.
"""
import os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NG = os.environ.get("NGSPICE_BIN", "ngspice")
OUT = os.path.join(ROOT, "resultados", "2026-09-06_starving")
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)
MODELS = os.path.join(ROOT, "spice", "models", "generic_l1.mod")

OPTIONS = """.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1"""

# Primeiro inversor: com fome de corrente (sp1/sn1) ou direto nos trilhos.
INV1_STARVED = """Ibp vdd1 sp1 DC {IB}
Ibn sn1 0    DC {IB}
M1p n1  mem sp1 vdd1 PMOS W=2u L=0.5u
M1n n1  mem sn1 0    NMOS W=1u L=0.5u"""

INV1_BASELINE = """M1p n1  mem vdd1 vdd1 PMOS W=2u L=0.5u
M1n n1  mem 0    0    NMOS W=1u L=0.5u"""


def netlist(name, inv1, ib, iin, cmem, cfb, vdd, tstop, tstep):
    body = inv1.replace("{IB}", str(ib))
    return f"""* {name}
Vdd1 vdd1 0 {vdd}
Vdd2 vdd2 0 {vdd}
Iin 0 mem DC {iin}
Cmem mem 0 {cmem}
{body}
M2p out n1  vdd2 vdd2 PMOS W=4u L=0.5u
M2n out n1  0    0    NMOS W=2u L=0.5u
Cfb out mem {cfb}
Mrst mem out 0 0 NMOS W=0.5u L=2u
Cload out 0 5f
.include {MODELS}
{OPTIONS}
.ic v(mem)=0 v(out)=0
.control
set filetype=ascii
tran {tstep} {tstop} 0 {tstep} uic
wrdata {RAW}/{name}.txt v(mem) v(out) v(n1) i(vdd1) i(vdd2)
.endc
.end
"""


def run(name, inv1=INV1_STARVED, ib="1n", iin="10p", cmem="100f", cfb="20f",
        vdd="1.8", tstop="100m", tstep="2u"):
    path = f"{RAW}/{name}.cir"
    open(path, "w").write(netlist(name, inv1, ib, iin, cmem, cfb, vdd, tstop, tstep))
    r = subprocess.run([NG, "-b", path], capture_output=True, text=True, timeout=1800)
    f = f"{RAW}/{name}.txt"
    if not os.path.exists(f):
        return None, (r.stderr or r.stdout)[-800:]
    return np.loadtxt(f), None


def analyse(d, vdd=1.8, discard=0.20):
    """Colunas do wrdata: t,mem, t,out, t,n1, t,i(vdd1), t,i(vdd2)."""
    t   = d[:, 0]
    mem = d[:, 1]
    out = d[:, 3]
    n1  = d[:, 5]
    i1  = d[:, 7]
    i2  = d[:, 9]

    # descarta os primeiros 20% do TEMPO simulado
    t0 = t[0] + discard * (t[-1] - t[0])
    k = t >= t0
    tw, i1w, i2w, outw, n1w, memw = t[k], i1[k], i2[k], out[k], n1[k], mem[k]
    span = tw[-1] - tw[0]

    # corrente media: trapezio sobre |i|, passo variavel
    def avg_abs(i):
        return np.trapezoid(np.abs(i), tw) / span

    a1, a2 = avg_abs(i1w), avg_abs(i2w)

    # disparos: cruzamento ascendente de 0,5*VDD em v(out)
    thr = 0.5 * vdd
    above = outw > thr
    rises = np.where((~above[:-1]) & (above[1:]))[0]
    times = tw[rises]
    if len(times) >= 3:
        isi = np.diff(times)
        freq = 1.0 / isi.mean()
        cv = isi.std(ddof=1) / isi.mean() * 100
    else:
        freq, cv = 0.0, float("nan")

    return dict(
        f=freq, cv=cv, nspk=len(times),
        i1=a1, i2=a2, itot=a1 + a2,
        p1=a1 * vdd, p2=a2 * vdd, ptot=(a1 + a2) * vdd,
        outmax=outw.max(), outmin=outw.min(),
        n1max=n1w.max(), n1min=n1w.min(),
        memmax=memw.max(), memmin=memw.min(),
    )


def show(tag, r):
    print(f"  {tag:>22} | f={r['f']:8.2f} Hz  CV={r['cv']:7.4f}%  "
          f"P1={r['p1']*1e9:10.2f} nW  P2={r['p2']*1e9:10.2f} nW  "
          f"Ptot={r['ptot']*1e9:10.2f} nW  out_max={r['outmax']:.3f} V")


if __name__ == "__main__":
    print("LINHA DE BASE (sem fome de corrente, duas fontes separadas)")
    d, err = run("baseline", inv1=INV1_BASELINE)
    assert d is not None, err
    base = analyse(d)
    show("baseline", base)
    print(f"\n  esperado da revalidacao: f = 160,3 Hz, P total = 12,6 uW (12600 nW)")
    print(f"  obtido:                  f = {base['f']:.1f} Hz, "
          f"P total = {base['ptot']*1e6:.2f} uW")
    np.save(f"{RAW}/baseline.npy", np.array([base['f'], base['ptot']]))

# ============================================================
# Convergencia da MEDIDA DE POTENCIA (Regra 1: a grandeza sob teste
# precisa ser invariante de tstep antes de valer alguma coisa)
# ============================================================
def convergencia_baseline():
    print("\nCONVERGENCIA DA LINHA DE BASE em tstep")
    for ts in ["5u", "2u", "1u", "0.5u"]:
        d, err = run(f"base_ts{ts}", inv1=INV1_BASELINE, tstep=ts)
        if d is None:
            print(f"  tstep={ts}: FALHOU {err[:120]}"); continue
        r = analyse(d)
        print(f"  tstep={ts:>5} | f={r['f']:8.2f} Hz | P1={r['p1']*1e6:7.3f} uW"
              f" | P2={r['p2']*1e6:7.3f} uW | Ptot={r['ptot']*1e6:7.3f} uW")

# ============================================================
# EXPERIMENTO PRINCIPAL: varredura da corrente de polarizacao
# ============================================================
def varredura(tstep="0.5u"):
    print(f"\nVARREDURA DE IB  (tstep={tstep}, Iin=10 pA, tstop=100 ms)")
    print(f"  {'IB':>6} | {'f (Hz)':>9} | {'CV(%)':>8} | {'P1(nW)':>10} | "
          f"{'P2(nW)':>11} | {'Ptot(nW)':>11} | {'out_max':>8} | {'n1 exc':>14}")
    res = {}
    for ib in ["1n", "10n", "100n", "1u"]:
        d, err = run(f"ib_{ib}", ib=ib, tstep=tstep)
        if d is None:
            print(f"  {ib:>6} | FALHOU: {err[:150]}"); continue
        r = analyse(d); res[ib] = r
        print(f"  {ib:>6} | {r['f']:9.2f} | {r['cv']:8.4f} | {r['p1']*1e9:10.2f} | "
              f"{r['p2']*1e9:11.2f} | {r['ptot']*1e9:11.2f} | {r['outmax']:8.3f} | "
              f"{r['n1min']:.2f}-{r['n1max']:.2f} V")
    return res

def convergencia_ponto(ib="10n"):
    """P2 nao era convergente na linha de base. Precisa ser no ponto de teste."""
    print(f"\nCONVERGENCIA NO PONTO IB={ib}")
    for ts in ["1u", "0.5u", "0.25u", "0.1u"]:
        d, err = run(f"conv_{ib}_{ts}", ib=ib, tstep=ts)
        if d is None: print(f"  tstep={ts}: FALHOU"); continue
        r = analyse(d)
        print(f"  tstep={ts:>6} | f={r['f']:8.2f} Hz | P1={r['p1']*1e9:8.2f} nW"
              f" | P2={r['p2']*1e9:8.2f} nW | Ptot={r['ptot']*1e9:8.2f} nW")

def curva_fi(ib="10n", tstep="0.5u"):
    print(f"\nCURVA f-I NO MELHOR PONTO (IB={ib})")
    print(f"  {'Iin':>6} | {'f (Hz)':>9} | {'f/Iin':>9} | {'CV(%)':>8} | {'Ptot(nW)':>9} | {'out_max':>8}")
    pts = []
    for iin, tstop in [("1p","900m"),("3p","400m"),("10p","150m"),("30p","60m"),("100p","30m")]:
        d, err = run(f"fi_{ib}_{iin}", ib=ib, iin=iin, tstop=tstop, tstep=tstep)
        if d is None: print(f"  {iin:>6} | FALHOU: {err[:100]}"); continue
        r = analyse(d); v = float(iin[:-1]); pts.append((v, r['f']))
        print(f"  {iin:>6} | {r['f']:9.2f} | {r['f']/v:9.3f} | {r['cv']:8.4f} |"
              f" {r['ptot']*1e9:9.2f} | {r['outmax']:8.3f}")
    return pts
