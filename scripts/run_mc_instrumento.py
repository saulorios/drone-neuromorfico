"""Etapa 2, rodada 1 — validacao do instrumento estatistico (V0 a V5).

Gera e roda os netlists. Nao interpreta: so mede.
Caminhos relativos a ROOT; binario do ngspice em NGSPICE_BIN.
"""
import os
import sys
import concurrent.futures as cf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mc_lib import ROOT, run

TAG = os.environ.get("RUN_TAG", "2026-09-08_etapa2_instrumento")
RAW = f"resultados/{TAG}/raw"
os.makedirs(os.path.join(ROOT, RAW), exist_ok=True)

TOL = """.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1"""

# ---------------------------------------------------------------- neuronio
def neuronio(nome, canto, seed):
    """Neuronio nominal da etapa 1, com canto e semente parametrizados.

    SEMENTE: `.option seed=N`, NUNCA `set rndseed` dentro do `.control`.
    Os `.model` com AGAUSS sao avaliados na leitura do netlist, ANTES do
    `.control` executar — um `set rndseed` la chega tarde e o sorteio fica
    solto. Medido em 2026-09-08: com `set rndseed=1` o ponto de operacao DC
    mudou entre execucoes (v(rp1) 0,84352 -> 0,85300 V); com `.option seed`
    e' identico bit a bit, inclusive entre tsteps diferentes.
    """
    seedopt = f".option seed={seed}\n" if seed is not None else ""
    return f"""* {nome} - neuronio axon-hillock, sky130, canto {canto}, 27 C, rndseed={seed}
.lib spice/models/sky130/sky130A/libs.tech/ngspice/sky130.lib.spice {canto}
.temp 27

Vdd1 vdd1 0 1.8
Vdd2 vdd2 0 1.8
Vddr vddr 0 1.8

* --- ramos de referencia do espelho ---
Iref1 rp1 0 DC 10n
XMref1 rp1 rp1 vddr vddr sky130_fd_pr__pfet_01v8 W=0.5 L=10
Iref2 rp2 0 DC 3u
XMref2 rp2 rp2 vddr vddr sky130_fd_pr__pfet_01v8 W=5   L=1

* --- neuronio ---
Iin 0 mem DC 10p
Cmem mem 0 100f
XMbp1 sp1 rp1 vdd1 vdd1 sky130_fd_pr__pfet_01v8 W=0.5 L=10
XM1p  n1  mem sp1  vdd1 sky130_fd_pr__pfet_01v8 W=2   L=0.5
XM1n  n1  mem 0    0    sky130_fd_pr__nfet_01v8 W=1   L=0.5
XMbp2 sp2 rp2 vdd2 vdd2 sky130_fd_pr__pfet_01v8 W=5   L=1
XM2p  out n1  sp2  vdd2 sky130_fd_pr__pfet_01v8 W=4   L=0.5
XM2n  out n1  0    0    sky130_fd_pr__nfet_01v8 W=2   L=0.5
Cfb out mem 20f
XMrst mem out 0 0 sky130_fd_pr__nfet_01v8 W=0.5 L=2
Cload out 0 5f

{seedopt}{TOL}
.nodeset v(rp1)=1.1 v(rp2)=1.05
.ic v(mem)=0 v(out)=0
.control
set filetype=ascii
tran 0.5u 150m 0 0.5u uic
wrdata {RAW}/{nome}.txt v(mem) v(out) v(n1) i(vdd1) i(vdd2)
.endc
.end
"""

# ---------------------------------------------------------------- arrays DC
def arrays(nome, canto, seed, vgs):
    """Arrays de dispositivos IDENTICOS, mesma polarizacao, ponto de operacao DC.

    A = nfet W=1 L=0.5   (0,5 um2)  -> geometria do M1n
    B = pfet W=5 L=1     (5   um2)  -> geometria de Mbp2 E Mref2 (par do espelho)
    C = nfet W=4 L=0.5   (2   um2)  -> 4x a area de A, para a lei de Pelgrom
    """
    N = 100
    seedopt = f".option seed={seed}" if seed is not None else "* sem semente fixa"
    L = [f"* {nome} - arrays de dispositivos identicos, canto {canto}, vgs={vgs}, rndseed={seed}",
         f".lib spice/models/sky130/sky130A/libs.tech/ngspice/sky130.lib.spice {canto}",
         ".temp 27", "",
         f"Vg  g  0 {vgs}", "Vd  d  0 1.8",
         f"Vgp gp 0 {1.8 - vgs}", "Vdp dp 0 0", "Vsp sp 0 1.8", ""]
    for i in range(N):
        L.append(f"Vma{i} da{i} d 0")
        L.append(f"XA{i} da{i} g 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.5")
    for i in range(N):
        L.append(f"Vmb{i} db{i} dp 0")
        L.append(f"XB{i} db{i} gp sp sp sky130_fd_pr__pfet_01v8 W=5 L=1")
    for i in range(N):
        L.append(f"Vmc{i} dc{i} d 0")
        L.append(f"XC{i} dc{i} g 0 0 sky130_fd_pr__nfet_01v8 W=4 L=0.5")
    L += ["", seedopt, TOL, ".control", "set filetype=ascii", "op",
          "let out = vector(0)"]
    cols = " ".join([f"i(Vma{i})" for i in range(N)] +
                    [f"i(Vmb{i})" for i in range(N)] +
                    [f"i(Vmc{i})" for i in range(N)])
    L += [f"wrdata {RAW}/{nome}.txt {cols}", ".endc", ".end", ""]
    return "\n".join(L)


def write(nome, texto):
    with open(os.path.join(ROOT, RAW, nome + ".cir"), "w") as fh:
        fh.write(texto)
    return f"{RAW}/{nome}.cir"


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = []

    if which in ("all", "v0"):
        for k in range(1, 7):
            jobs.append(write(f"v0_tt_seed{k}", neuronio(f"v0_tt_seed{k}", "tt", k)))

    if which in ("all", "v1"):
        # V1/V3: mismatch LIGADO, dois pontos de polarizacao para extrair gm
        for vgs, tag in ((1.20, "a"), (1.25, "b")):
            jobs.append(write(f"v1_mm_vgs{tag}",
                              arrays(f"v1_mm_vgs{tag}", "tt_mm", 1, vgs)))
        # controle: mesmos arrays com mismatch DESLIGADO
        jobs.append(write("v1_tt_vgsa", arrays("v1_tt_vgsa", "tt", 1, 1.20)))

    if which in ("all", "v2"):
        # sem rndseed, duas vezes; e com sementes explicitas diferentes
        jobs.append(write("v2_noseed_r1", arrays("v2_noseed_r1", "tt_mm", None, 1.20)))
        jobs.append(write("v2_noseed_r2", arrays("v2_noseed_r2", "tt_mm", None, 1.20)))
        jobs.append(write("v2_seed7", arrays("v2_seed7", "tt_mm", 7, 1.20)))

    if which in ("all", "v4"):
        for k in range(1, 13):
            jobs.append(write(f"v4_mm_seed{k}", neuronio(f"v4_mm_seed{k}", "tt_mm", k)))

    if which in ("all", "conv"):
        # convergencia com o sorteio FIXO: so o tstep muda
        for k in (1, 4):
            for ts in ("0.5u", "0.125u"):
                nome = f"conv_s{k}_ts{ts.replace('.', 'p')}"
                t = neuronio(nome, "tt_mm", k).replace(
                    "tran 0.5u 150m 0 0.5u uic", f"tran {ts} 150m 0 {ts} uic")
                jobs.append(write(nome, t))

    print(f"{len(jobs)} netlists")
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for cir, (ok, err) in zip(jobs, ex.map(lambda c: run(c), jobs)):
            print(f"{'ok ' if ok else 'FALHOU'} {cir}" + (f"\n    {err}" if err else ""))


if __name__ == "__main__":
    main()
