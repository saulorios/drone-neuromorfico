# Etapa 1 · Validação do PDK SkyWater 130 nm — a armadilha do W/L

Data: 2026-09-07 · **ngspice 42** · **sky130A** via volare, canto `tt`, 27 °C
Previsões pré-registradas em `previsao_pre_registrada.md`, commitadas **antes** desta medida
(commit `a0ffaf6`).

**Pergunta desta rodada:** W e L nos subcircuitos do sky130 são número puro em µm — a
armadilha existe, e o que acontece quando se erra?

**Resposta: a armadilha existe, mas NÃO é silenciosa.** Escrever `W=1u L=0.15u` aborta a
simulação com erro explícito. Isso refuta a parte central da minha Previsão A.

---

## A · A instalação — só o subconjunto do ngspice

Medido antes de baixar, como manda o plano. Os assets do volare são separados por
biblioteca:

| asset | tamanho | baixado? |
|---|---|---|
| `common.tar.zst` (contém `libs.tech/`, e nele `libs.tech/ngspice/`) | 16,6 MB | **sim** |
| `sky130_fd_pr.tar.zst` (contém `libs.ref/sky130_fd_pr/spice/`) | 14,0 MB | **sim** |
| `sky130_fd_sc_hd.tar.zst` (células padrão) | 166,7 MB | não |
| `sky130_fd_io.tar.zst` | 50,7 MB | não |
| `sky130_sram_macros.tar.zst` | 30,3 MB | não |
| `sky130_fd_sc_hvl.tar.zst` | 54,2 MB | não |

**Baixados 30,6 MB comprimidos**, contra ~380 MB do conjunto completo. Extraídos, vieram
`sky130A` e `sky130B` a 127 MB cada; **`sky130B` (variante ReRAM) foi removido** — não é
usado e o disco está a 96%.

**Ocupação final: 127 MB** em `spice/models/sky130/sky130A/`. Fora do controle de versão
(`.gitignore` já previa `spice/models/sky130*/`).

## B · A armadilha do W/L — Previsão A, refutada em parte

Quatro variantes do mesmo transistor isolado (`Vgs = Vds = 1,8 V`, bulk no terra):

| variante | escrito | `.option scale=1u` | resultado |
|---|---|---|---|
| A | `W=1 L=0.15` | sim | **501,05 µA** |
| B | `W=1u L=0.15u` | sim | **aborta** |
| C | `W=1 L=0.15` | não | **501,05 µA** — idêntico a A |
| D | `W=1u L=0.15u` | não | **aborta** |

Erro exato das variantes B e D:

```
Error on line:
  m.xm1.msky130_fd_pr__nfet_01v8 d g 0 b xm1:sky130_fd_pr__nfet_01v8__model
  l= 1.500000000000000e-07  w= 1.000000000000000e-06  ...
could not find a valid modelname
    Simulation interrupted due to error!
```

**O mecanismo.** O `.subckt` do `sky130_fd_pr__nfet_01v8` declara
`.param l = 1 w = 1` e repassa `l={l} w={w}` ao dispositivo BSIM4 interno, que é binado por
`lmin/lmax/wmin/wmax`. Escrever `1u` entrega `1e-06` ao seletor de bin, que não encontra bin
algum e **aborta**. Não há valor devolvido, não há *clamp*, não há resultado errado.

**Minha Previsão A dizia:** *"Espero que o ngspice não emita erro — apenas devolva corrente
absurdamente baixa, da ordem de 10⁻⁶ do valor correto, ou que o modelo faça clamp
silencioso."* **Errado.** A falha é `fail-stop`, não `fail-silent`. Isso é uma boa notícia
para o projeto: a armadilha não pode contaminar resultado nenhum em silêncio — ou o netlist
está certo, ou não roda.

**Descoberta lateral, que a pergunta não previa: `.option scale=1u` é irrelevante por esta
via.** As variantes A e C dão exatamente o mesmo valor. O `scale` está definido em
`libs.tech/ngspice/all.spice`, mas **não** na cadeia do `sky130.lib.spice` → `corners/tt.spice`,
que é o ponto de entrada padrão via `.lib`. Com números puros, funciona com ou sem ele.
Registrado no `CLAUDE.md` §7 para não ser reintroduzido "por precaução".

## C · Curva I–V — Previsão B, confirmada

`Vds = 1,8 V`, varredura de `Vgs` de 0 a 1,8 V em 20 mV, canto `tt`, 27 °C.

| dispositivo | Id em Vgs = 1,8 V |
|---|---|
| W = 0,42 L = 0,15 (mínimo do processo) | 196,52 µA |
| **W = 1 L = 0,15** | **501,05 µA** |
| W = 2 L = 0,15 | 1030,63 µA |
| W = 1 L = 0,5 | 225,51 µA |
| W = 0,5 L = 2 (`Mrst` do neurônio) | 33,62 µA |

**Previsão B: 400 a 700 µA, centrada em ~550 µA. Medido: 501,05 µA.** Dentro da janela, 9%
abaixo do centro. Densidade de 501 µA por µm de largura, coerente com o dispositivo de
1,8 V neste nó.

**Confirmação independente de que `W=1` significa 1 µm** — a escala com a largura:

| razão | esperado (geométrico) | medido | desvio |
|---|---|---|---|
| Id(W=2) / Id(W=1) | 2,000 | **2,057** | +2,9% |
| Id(W=1) / Id(W=0,42) | 2,381 | **2,550** | +7,1% |

Os desvios são do sinal certo e da ordem certa para efeito de canal estreito, mais
pronunciado no dispositivo de largura mínima. Se a interpretação de unidade estivesse
errada, a corrente estaria fora por seis ordens de grandeza, não por 3–7%.

## D · Sub-limiar — minha previsão da zona morta está errada por 8,5×

Medido em `Vgs = 0`, `Vds = 1,8 V`:

| dispositivo | Id em Vgs = 0 |
|---|---|
| **W = 0,5 L = 2 (`Mrst`)** | **84,72 fA** |
| W = 1 L = 0,15 | 246,39 fA |

Inclinação sub-limiar de `Mrst`: **91,3 mV/década**.

**Minha previsão pré-registrada: fuga total no nó `mem` de 0,1 a 10 fA.**
**Medido para o `Mrst` sozinho: 84,7 fA — 8,5× acima do topo da faixa prevista.**

O cálculo que fiz subestimou porque usei `V_th` de canal longo entre 0,5 e 0,7 V; a
inclinação medida de 91,3 mV/década implica `n` ≈ 1,53, maior que o 1,3 que assumi, e o
`V_th` efetivo do `Mrst` é menor do que supus.

**Ressalva que atenua, com a procedência do número:** a medida é em `Vds = 1,8 V`. No
circuito, o dreno de `Mrst` é o nó `mem`. A faixa de operação de `mem` de que disponho é
**−0,114 a 0,562 V**, medida em `resultados/2026-09-07_fi_espelho/`, no ponto nominal
(`IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA) — **com modelos nível 1**, não com o sky130.
**O neurônio ainda não foi migrado**, então essa faixa é o melhor palpite disponível e não
uma condição de operação medida no PDK. Se ela se mantiver, `Vds` menor significa menos
DIBL e fuga real **menor** que 84,7 fA, fazendo do valor medido um **limite superior**. Se a
migração mudar a faixa de operação da membrana, esta ressalva precisa ser refeita.

### O que isso faz com a previsão de zona morta

**A 27 °C — a conclusão qualitativa sobrevive, mas por margem bem menor que eu disse.**
84,7 fA contra a menor corrente da faixa útil (1 pA = 1000 fA) é **8,5% do sinal**, não os
0,01–1% que previ. Isso não é uma zona morta dura, mas é um efeito mensurável de poucos por
cento na frequência no extremo inferior da faixa. A zona morta implícita esperada passa de
"< 10 fA" para "da ordem de 85 fA" — ainda 12× abaixo do menor ponto de teste.

**A 125 °C — pior do que eu previ.** Com a fuga dobrando a cada ~8–10 °C, de 27 a 125 °C são
10 a 12 duplicações, fator 10³ a 4×10³: **85 pA a 340 pA**. Isso está **acima de toda a faixa
útil decidida (1 a 50 pA)**. No canto quente o neurônio seria dominado pela fuga do reset, e
provavelmente não dispararia em ponto algum da faixa.

**Isto é matéria da etapa 3 (cantos), não desta rodada.** Fica registrado como previsão nova,
a ser testada lá.

---

## E · Estado das previsões pré-registradas

| Previsão | Veredito |
|---|---|
| A — a armadilha do W/L existe | **confirmada** |
| A — e é silenciosa (sem erro, corrente ~10⁻⁶ do correto) | **REFUTADA** — é erro fatal, a simulação aborta |
| B — Id de 400 a 700 µA para W=1 L=0,15 | **confirmada** — 501,05 µA |
| Zona morta: fuga de 0,1 a 10 fA a 27 °C | **REFUTADA** — 84,7 fA, 8,5× acima do topo |
| Zona morta: não detectável a 27 °C | **sobrevive**, com margem menor (85 fA vs 1 pA) |
| Zona morta: 1 a 10 pA a 125 °C | **provavelmente subestimada** — projeção agora dá 85 a 340 pA |

Duas de seis refutadas, uma revisada. As duas refutações são do mesmo tipo: subestimei a
severidade em ambas as direções — a armadilha é mais barulhenta que eu esperava, e a fuga é
maior.

## F · Pendências

1. **Nada do neurônio foi migrado ainda.** Esta rodada validou um transistor isolado, que era
   a pré-condição. O netlist do neurônio continua em nível 1.
2. **Só o canto `tt` a 27 °C foi exercitado.** Os outros cantos e temperaturas estão no
   PDK e não foram tocados.
3. **A fuga foi medida em `Vds` = 1,8 V**, acima da condição de operação. É limite superior.
4. **A projeção para 125 °C é extrapolação**, com a regra de duplicação por 8–10 °C, e não
   medida — o PDK tem os modelos de temperatura e pode responder direto. Etapa 3.
5. **`sky130B` foi removido.** Se a variante ReRAM for necessária algum dia, refazer o
   download.

## Arquivos

- `validacao_pdk.png` — a figura (2 painéis)
- `previsao_pre_registrada.md` — as previsões, commitadas antes da medida
- `raw/` — netlists e a varredura I–V
- `../../scripts/plots_pdk_iv.py` — figura
