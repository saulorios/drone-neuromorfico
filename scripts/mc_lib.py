"""Ferramentas comuns da etapa 2 (Monte Carlo / descasamento).

Caminhos SEMPRE relativos a ROOT. Nenhum caminho absoluto (CLAUDE.md §9).
O binario do ngspice vem de NGSPICE_BIN; nao ha padrao silencioso para a 41,
porque a etapa 2 normaliza contra um nominal medido na 42 (CLAUDE.md §2).
"""
import os
import subprocess
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NGSPICE = os.environ.get("NGSPICE_BIN", "ngspice")


def run(cir_rel):
    """Roda um netlist a partir de ROOT. Devolve (ok, stderr_resumido)."""
    p = subprocess.run([NGSPICE, "-b", cir_rel], cwd=ROOT,
                       capture_output=True, text=True, timeout=1800)
    err = "\n".join(l for l in (p.stdout + p.stderr).splitlines()
                    if any(k in l.lower() for k in
                           ("error", "fatal", "aborted", "too small", "warning: model")))
    return p.returncode == 0, err


def load(txt_rel, ncols):
    """Le a saida de wrdata. ngspice grava (tempo, valor) por variavel.

    Aceita o bruto compactado: os traces de tensao ocupam ~50 MB por corrida e
    sao arquivados em .gz. numpy le .gz direto.
    """
    p = os.path.join(ROOT, txt_rel)
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p += ".gz"
    d = np.loadtxt(p)
    t = d[:, 0]
    return t, {i: d[:, 2 * i + 1] for i in range(ncols)}


def spikes(t, out, t_ini=0.0):
    """Detector de disparo com limiar ADAPTATIVO (CLAUDE.md §7).

    Limiar = 50% da excursao do proprio `out` na janela medida, nunca uma
    fracao de VDD. Devolve os instantes de cruzamento de subida.
    """
    m = t >= t_ini
    tw, ow = t[m], out[m]
    lo, hi = ow.min(), ow.max()
    exc = hi - lo
    if exc < 0.05:          # sem excursao: nao ha o que detectar
        return np.array([]), exc, lo, hi
    thr = lo + 0.5 * exc
    up = np.where((ow[:-1] < thr) & (ow[1:] >= thr))[0]
    # interpolacao linear do instante de cruzamento
    ts = []
    for i in up:
        y0, y1 = ow[i], ow[i + 1]
        ts.append(tw[i] + (thr - y0) / (y1 - y0) * (tw[i + 1] - tw[i]))
    return np.array(ts), exc, lo, hi


def freq(t, out, drop_first=1):
    """Frequencia por ciclos INTEIROS: do primeiro ao ultimo disparo da janela.

    Descarta os `drop_first` primeiros disparos (transitorio de partida).
    Devolve (f_Hz, cv_isi_percent, n_disparos, excursao_out).
    """
    ts, exc, lo, hi = spikes(t, out)
    if len(ts) < drop_first + 3:
        return np.nan, np.nan, len(ts), exc
    ts = ts[drop_first:]
    isi = np.diff(ts)
    f = (len(ts) - 1) / (ts[-1] - ts[0])
    cv = 100.0 * isi.std(ddof=1) / isi.mean()
    return f, cv, len(ts), exc
