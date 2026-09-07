# Curva f–I no ponto do espelho assimétrico — SOBREVIVE

Data: 2026-09-07 · **ngspice 42** (`ngspice --version`) · modelos nível 1
(`generic_l1.mod`), inalterados.
Ponto de operação: **IB1 = 10 nA, IB2 = 3 µA**, `Cmem` = 100 fF, `Cfb` = 20 fF,
`VDD` = 1,8 V, `Wrst` = 0,5 µm, T = 27 °C.
`.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16 trtol=1`
`.nodeset v(rp1)=1.2557 v(rp2)=1.1867` — **obrigatório**, ver seção C.

**Pergunta:** a curva f–I sobrevive em IB1 = 10 nA, IB2 = 3 µA?

**Resposta: SIM.** R² = 0,99999917, expoente log–log 1,0005, sem zona morta. Fecha a
pendência 1 do relatório do espelho. Mas apareceu uma restrição nova: o orçamento de
100 nW só vale para `Iin` ≲ 54 pA — ver seção E.

---

## A · Reprodução do ponto publicado, antes de qualquer coisa

O netlist do Resultado 3 (fome só no PMOS, nos dois estágios) não veio junto — só o
`mirror.cir` da variante simétrica. Foi reconstruído a partir da descrição do relatório e
conferido contra os números publicados antes de ser usado.

| Grandeza | `espelho.md` | Reconstrução | Desvio |
|---|---|---|---|
| Frequência | 138,3 Hz | **138,28 Hz** | **−0,0%** |
| Pulso de saída | 92,2% de VDD | **92,22%** | **+0,0%** |
| P 1º estágio | 1,69 nW | 1,78 nW | +5,1% |
| P 2º estágio | 81,77 nW | 85,67 nW | +4,8% |
| P total | 83,5 nW | 87,45 nW | +4,7% |
| CV do ISI | 0,0050% | 0,0040% | −20% |

Frequência e pulso batem exatamente — o circuito reconstruído é o certo. O desvio de ~5%
na potência vinha da janela de média: ver seção D. Remedida sobre ciclos inteiros, a
potência nominal dá **85,37 nW**, +2,2% do publicado.

**Diferenças de reconstrução assumidas** (não constavam do relatório):
- Espelho 1:1 em ambos os estágios — o transistor de referência tem as mesmas dimensões
  do de saída (W=0,5 µm/L=10 µm no 1º, W=5 µm/L=1 µm no 2º).
- Dois ramos de referência independentes, um por corrente de polarização.
- NMOS de cada inversor ligado direto ao terra (é a definição de "assimétrica").

## B · Verificação de trilhos — todos os 12 pontos passam

| Nó | Faixa em todos os pontos | Veredito |
|---|---|---|
| `v(sp1)` | 0,615 .. 1,800 V | OK |
| `v(sp2)` | 0,866 .. 1,800 V | OK |
| `v(rp1)` | 1,257 .. 1,265 V | OK |
| `v(rp2)` | 1,188 .. 1,192 V | OK |

Nenhum nó de polarização ultrapassa os trilhos em nenhum ponto da varredura. O espelho
resolve o problema que derrubou os dois testbenches anteriores.

`v(mem)` opera de −0,114 a 0,562 V no ponto nominal. O trecho negativo é injeção de carga
por `Cfb` no reset, comportamento do circuito e não do aparato — a membrana não é nó de
polarização e não está sujeita ao critério de trilho.

## C · O `.nodeset` é obrigatório — confirmado, vira convenção

| | Resultado |
|---|---|
| **com** `.nodeset` | roda, f = 138,28 Hz |
| **sem** `.nodeset` | **aborta** |

Erro exato, reproduzido:

```
doAnalyses: TRAN:  Timestep too small; initial timepoint: trouble with node "rp2"
tran simulation(s) aborted
```

Causa: com `uic`, o ngspice pula o ponto de operação DC e parte de 0 V em todo nó não
citado no `.ic`. O nó de referência `rp2` em 0 V põe `Mref2` com Vsg = 1,8 V, passando
corrente muito acima dos 3 µA de projeto; o transitório inicial é violento demais para o
integrador. O `.nodeset` dá o palpite certo e o problema some.

Valores usados, calculados e não arbitrados — para um PMOS em ligação diodo,
`V(rp) = VDD − (|VTO| + Vov)` com `Vov = √(2·IB/(KP·W/L))`:

| ramo | IB | W/L | Vov | `.nodeset` |
|---|---|---|---|---|
| `rp1` | 10 nA | 0,05 | 94 mV | 1,2557 V |
| `rp2` | 3 µA | 5,0 | 163 mV | 1,1867 V |

Confere com a medida: `rp1` estabiliza em 1,257–1,265 V e `rp2` em 1,188–1,192 V.
**Convenção acrescentada ao `CLAUDE.md` §7.**

## D · Convergência — passa com folga de 500×

Exigido: 1% ao dividir `tstep` por 4. Testado sobre 16×.

| tstep | f (Hz) | desvio | P total | pulso |
|---|---|---|---|---|
| 2 µs | 138,279 | — | 87,47 nW | 92,22% |
| 1 µs | 138,279 | −0,000% | 87,31 nW | 92,22% |
| 0,5 µs | 138,279 | −0,001% | 87,45 nW | 92,22% |
| 0,125 µs | 138,277 | **−0,002%** | 87,60 nW | 92,22% |

Frequência invariante em 0,002% sobre 16× de `tstep`; potência em 0,33%. Fecha a
pendência 2 do relatório do espelho.

### Correção de método: a média de potência precisa de ciclos inteiros

A janela de "descartar 20% e integrar o resto" não contém número inteiro de períodos, e a
sobra de ciclo parcial introduz espalhamento da ordem de 1/N. Isso produzia uma curva de
potência não-monotônica (81,7 nW em 7 pA, 87,5 em 10 pA, 83,0 em 15 pA) que não é física.

Remedindo entre o primeiro e o último cruzamento de disparo — número inteiro de ciclos:

| Iin (pA) | 1 | 2 | 3 | 5 | 7 | 10 | 15 | 20 | 30 | 50 | 70 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| janela bruta (nW) | 73,3 | 83,1 | 85,5 | 84,6 | 81,7 | 87,5 | 83,0 | 88,6 | 90,7 | 100,4 | 101,2 | 115,5 |
| **ciclos inteiros (nW)** | **80,5** | **81,5** | **81,9** | **83,2** | **84,2** | **85,4** | **87,6** | **89,1** | **92,5** | **99,1** | **104,2** | **112,4** |

A curva fica monotônica e limpa. **Toda medida de potência deste projeto deve usar ciclos
inteiros.** Registrado no `CLAUDE.md` §7.

## E · A curva f–I

| Iin (pA) | 1 | 2 | 3 | 5 | 7 | 10 | 15 | 20 | 30 | 50 | 70 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f (Hz) | 13,734 | 27,581 | 41,424 | 69,105 | 96,780 | 138,279 | 207,410 | 276,519 | 414,632 | 690,580 | 966,166 | 1378,943 |
| f/Iin (Hz/pA) | 13,734 | 13,790 | 13,808 | 13,821 | 13,826 | 13,828 | 13,827 | 13,826 | 13,821 | 13,812 | 13,802 | 13,789 |
| CV do ISI (%) | 0,0036 | 0,0029 | 0,0037 | 0,0048 | 0,0028 | 0,0040 | 0,0035 | 0,0029 | 0,0030 | 0,0023 | 0,0040 | 0,0043 |
| pulso (% VDD) | 92,15 | 92,16 | 92,17 | 92,19 | 92,20 | 92,22 | 92,25 | 92,27 | 92,30 | 92,35 | 92,39 | 92,45 |

**Ajuste linear com intercepto livre:**

```
f = 13,79354 · Iin + 0,3145 Hz          R² = 0,99999917
```

Zona morta implícita: **−22,8 fA** — negativa, isto é, nenhuma, e 44× abaixo do menor
ponto medido (1 pA). A reta passa pela origem.

**Ajuste log–log:**

```
log f = 1,00054 · log Iin + 1,13952      R² = 0,99999848
```

Expoente **1,0005**, a 0,05% da proporcionalidade exata. Os dois ajustes concordam: a
relação é linear e proporcional, não apenas linear-com-offset.

**Resíduos** (% do valor medido): o maior é **−2,73%**, no ponto de 1 pA. Todos os outros
onze ficam dentro de ±1,17%, e dez dentro de ±0,7%. O padrão é sistemático — negativo nos
extremos, positivo no meio — o que é curvatura residual de terceira ordem, não ruído. Nada
que ameace a linearidade nesta faixa.

A razão f/`Iin` deriva **0,7%** ao longo de dois decades (13,734 a 13,828), contra 5% na
linha de base revalidada (15,3 a 16,04). **A linearidade melhorou com a fome de corrente.**

| | linha de base | com fome assimétrica |
|---|---|---|
| ganho | 16,0 Hz/pA | **13,79 Hz/pA** (−14%) |
| deriva de f/Iin na faixa | 5% | **0,7%** |
| R² | não calculado | **0,99999917** |

### O achado novo: o orçamento de 100 nW não vale em toda a faixa

A potência cresce monotonicamente com `Iin` — de 80,5 nW em 1 pA a 112,4 nW em 100 pA — e
**cruza os 100 nW em `Iin` ≈ 54 pA** (interpolação entre os pontos de 50 e 70 pA), o que
corresponde a f ≈ 745 Hz.

O critério de aceitação foi enunciado no ponto nominal, e nele passa com folga (85,4 nW
contra 100 nW). Mas a faixa útil declarada do neurônio vai a 100 pA, e no terço superior
dela o orçamento estoura. **O critério e a faixa de operação não são compatíveis como
estão** — ou se limita a faixa a ~54 pA, ou se afrouxa o alvo, ou se busca outro ponto de
polarização. Não é decisão minha.

---

## F · Critérios de aceitação

| Critério | Exigido | Obtido | |
|---|---|---|---|
| Potência no ponto nominal | ≤ 100 nW | **85,4 nW** | aprova, folga de 1,17× |
| Potência em toda a faixa 1–100 pA | ≤ 100 nW | 80,5 a **112,4 nW** | **REPROVA acima de ~54 pA** |
| Pulso de saída | ≥ 90% de VDD | 92,15 a 92,45% | aprova em todos os 12 pontos |
| CV do ISI | < 0,1% | 0,0023 a 0,0048% | aprova, folga de 20× |
| f–I linear pela origem | — | R² = 0,99999917, expoente 1,0005 | aprova |
| Convergência | 1% com tstep/4 | 0,002% sobre 16× | aprova |
| Trilhos | nenhuma violação | nenhuma em 12 pontos | aprova |

---

## G · Pendências

1. **O ramo de referência custa 5,42 µW** — 63× o consumo do próprio neurônio. É legítimo
   deixá-lo fora do orçamento porque é compartilhado, mas ninguém disse por quantos. Para
   o total por neurônio ficar em 100 nW seria preciso amortizá-lo por **N ≥ 370 neurônios**
   (5,42 µW / N ≤ 14,6 nW). Abaixo disso o número de 85,4 nW não descreve o chip. É um
   requisito de arquitetura que ainda não estava escrito em lugar nenhum.
2. **O orçamento estoura acima de `Iin` ≈ 54 pA** (seção E). Critério e faixa útil
   incompatíveis como estão.
3. **A vizinhança de IB2 entre 1 e 3 µA continua sem mapear** — pendência 4 do relatório do
   espelho. Fora do escopo desta rodada por instrução explícita.
4. **As dimensões do espelho em nA continuam fictícias no nível 1** (pendência 3 do
   relatório do espelho). W/L = 0,05 com Vov ≈ 94 mV é inversão moderada, que o nível 1
   trata como lei quadrática. O comportamento de limitador está certo; o dimensionamento
   só sai com o PDK.
5. **A potência do ponto nominal difere 2,2% da publicada** (85,37 contra 83,5 nW), com
   frequência e pulso batendo exatamente. Provável diferença residual de reconstrução ou
   de janela de média. Não investigado.
6. **Nível 1, sem sub-limiar, sem descasamento, sem parasitas** — como sempre.

---

## Arquivos

- `fi_espelho.png` — a figura (3 painéis)
- `raw/` — netlists `.cir` de todos os pontos, com caminhos relativos
- `../../scripts/run_fi_espelho.py` — testbench e varredura
- `../../scripts/plots_fi_espelho.py` — figura
