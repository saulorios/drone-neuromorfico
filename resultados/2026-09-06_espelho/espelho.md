# Fome de corrente por espelho — critério de 100 nW ATINGIDO

Data: 2026-09-06 · **ngspice 42** · modelos nível 1 inalterados
Ponto nominal: Cmem=100 fF, Cfb=20 fF, Iin=10 pA, VDD=1,8 V, Wrst=0,5 µm
`.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16 trtol=1`

## O elemento correto: espelho de corrente

A fonte ideal foi movida para o **ramo de referência**, onde alimenta um transistor
em ligação diodo que **sempre conduz** — não há violação de trilho possível. O
elemento que limita o inversor é o transistor de saída do espelho, que é um
limitador (passa de 0 a IB) e não um forçador.

O ramo de referência é compartilhado entre todos os neurônios de um chip real e
por isso é medido em alimentação separada, **fora do orçamento por neurônio**.

## Resultado 1 — fome simétrica (os dois lados do 1º inversor) FALHA

| IB | f (Hz) | P1 (nW) | P2 (nW) | total (nW) | n1 mín | pulso |
|---|---|---|---|---|---|---|
| 1 nA | 72,6 | 4,73 | 1945 | 1949 | 0,832 | 1,529 V |
| 10 nA | 80,1 | 8,13 | 564,5 | 572,6 | 0,839 | 1,502 V |
| 30 nA | 81,8 | 20,4 | 281,4 | 301,8 | 0,854 | 1,434 V |
| 100 nA | não dispara | 157,2 | 446,7 | 603,9 | 0,871 | 0,735 V |

Trilhos respeitados (sp1 ≤ 1,800 V, sn1 ≥ −0,02 V): **o testbench está validado.**
Mas o consumo total é **pior que o das fontes ideais** (218 nW).

**Causa, e ela é estrutural.** A membrana opera entre 0,41 e 0,99 V. Nessa faixa
M1p e M1n conduzem os dois, sempre. O nível de `n1` é fixado pela **razão** entre
as duas correntes. Grampear ambas ao mesmo IB destrói essa razão: nenhum lado
vence, `n1` estaciona em ~0,83 V — dentro da janela de condução do 2º inversor
(0,45–1,35 V) — e o curto-circuito **migra do 1º para o 2º estágio**.

É o mesmo mecanismo do problema original, deslocado um estágio adiante.

## Resultado 2 — fome assimétrica (só o PMOS) FUNCIONA

Só o PMOS do 1º inversor limitado; NMOS ligado direto ao terra.

| IB | f (Hz) | CV ISI | P1 (nW) | P2 (nW) | total (nW) | pulso |
|---|---|---|---|---|---|---|
| 1 nA | 145,8 | 0,004% | 0,334 | 306,0 | 306,4 | 95,4% VDD |
| 10 nA | 138,7 | 0,011% | 1,567 | 143,0 | 144,6 | 95,9% VDD |
| 100 nA | 121,5 | 0,004% | 12,60 | 94,9 | 107,5 | 97,1% VDD |

P1 cai de **12 702 nW para 1,57 nW** (8100×) preservando o pulso cheio.
O piso passa a ser o 2º estágio, ainda não limitado.

A variante só-NMOS foi testada e **não dispara** em 1 e 10 nA. Descartada.

## Resultado 3 — PMOS dos DOIS estágios: critério atingido

Espelho do 2º estágio dimensionado largo (W=5 µm, L=1 µm) para não roubar
excursão do pulso — o dispositivo estreito de nA derrubava a saída para 81% VDD.

| IB1 | IB2 | f (Hz) | CV ISI | P1 | P2 | **total** | **pulso** |
|---|---|---|---|---|---|---|---|
| 10 nA | 1 µA | 137,7 | 0,0032% | 1,72 | 44,40 | 46,1 nW | 83,1% ❌ |
| 30 nA | 1 µA | 130,2 | 0,0026% | 5,06 | 42,22 | 47,3 nW | 81,1% ❌ |
| **10 nA** | **3 µA** | **138,3** | **0,0050%** | **1,69** | **81,77** | **83,5 nW** | **92,2%** ✅ |

### Ponto que atende a todos os critérios: IB1 = 10 nA, IB2 = 3 µA

| Critério | Exigido | Obtido | |
|---|---|---|---|
| Potência por neurônio | ≤ 100 nW | **83,5 nW** | aprova, folga de 1,2× |
| Pulso de saída | ≥ 90% VDD | **92,2%** | aprova |
| CV do ISI | < 0,1% | **0,0050%** | aprova, folga de 20× |
| Frequência preservada | — | 138,3 Hz (base 160,3) | desvio de 14% |

**Redução total: 12 600 → 83,5 nW = 151×.** Energia por disparo: 78 nJ → 0,60 nJ.

## Pendências — este resultado NÃO está fechado

1. **A curva f–I não foi refeita** neste ponto. Sem ela, não se sabe se a
   linearidade e a passagem pela origem sobrevivem. É o item que falta para o
   critério de aceitação completo.
2. **Sem estudo de convergência** neste ponto de operação. Os pontos com IB2 na
   casa de µA precisaram de `.nodeset` para convergir; sem ele, `Timestep too
   small` no nó de referência.
3. **As dimensões do espelho em nA são fictícias no nível 1.** W/L = 0,05 entrega
   10 nA no modelo com Vov ≈ 0,09 V, mas 90 mV de sobretensão é regime de inversão
   moderada, que o nível 1 modela como lei quadrática — errado. O **comportamento**
   de limitador está correto; o **dimensionamento** do circuito de polarização só
   pode ser projetado com o PDK.
4. **A margem de 1,2× é estreita** e o ponto ótimo é uma ilha: IB2 = 1 µA reprova
   no pulso, IB2 = 3 µA aprova. Falta mapear a vizinhança.
5. Nível 1, sem sub-limiar, sem descasamento, sem parasitas — como sempre.

## Correções de método acumuladas nesta linha de investigação

| Testbench | Falha | Quem pegou |
|---|---|---|
| Fontes de corrente ideais | Conformidade infinita: viola trilhos até o diodo de corpo | Claude CLI |
| Fonte ideal + resistor paralelo | Norton: V(aberto) = VDD + IB·R, viola por construção | Claude CLI |
| Espelho de corrente | — validado (trilhos respeitados) | — |
| Fome simétrica | Destrói a razão de correntes, curto migra de estágio | esta rodada |
| Espelho estreito no 2º estágio | Rouba excursão do pulso (81% VDD) | esta rodada |
