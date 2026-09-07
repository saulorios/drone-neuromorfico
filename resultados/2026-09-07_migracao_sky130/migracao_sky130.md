# Migração do neurônio para o sky130 — a f–I reproduz, o consumo despenca, o pulso reprova

Data: 2026-09-07 · **ngspice 42** · **sky130A**, canto `tt`, `.temp 27`
Topologia e **dimensões idênticas** à versão nível 1. `Cmem` = 100 fF e `Cfb` = 20 fF ideais.
`IB1` = 10 nA, `IB2` = 3 µA. Previsões em `previsao_pre_registrada.md`, commit `357ac1e`.

**Pergunta:** o neurônio migrado para o sky130 reproduz o comportamento do nível 1?

**Resposta: na função de transferência, sim, quase exatamente. No consumo, não — é 14×
menor. E o pulso de saída reprova o critério de 90%.**

---

## A · O discriminador: a migração não falhou

Antes de qualquer número de comportamento, o teste que separa "migração quebrada" de
"circuito mudou", como pré-registrado. Espelhos com o dreno forçado a 0,9 V (saturação
garantida), ponto de operação DC:

| espelho | programado | entregue | erro |
|---|---|---|---|
| `Mbp1` (W=0,5 L=10) | 10 nA | **9,9906 nA** | **0,09%** |
| `Mbp2` (W=5 L=1) | 3 µA | **2,9839 µA** | **0,54%** |

O critério pré-registrado admitia até 2× de erro. Obtido: meio por cento. **A rede de
polarização entrega exatamente o que foi pedido.** Somado a trilhos respeitados em todos os
12 pontos da varredura (`sp1`, `sp2`, `rp1`, `rp2` sempre dentro de 0 a 1,8 V), isso fecha o
discriminador: **qualquer diferença daqui para baixo é do circuito, não da migração.**

### Um critério meu que estava errado

O critério 4 do pré-registro dizia que `rp1` e `rp2` não deveriam ficar a mais de 300 mV do
previsto analiticamente. Medido: `rp1` = 0,847 V contra 1,256 V previstos (**409 mV**) e
`rp2` = 0,687 V contra 1,187 V (**500 mV**). Os dois estouram o limite.

**O critério estava mal formulado, não a migração.** A previsão analítica usava o
`V_th` = 0,45 V do nível 1; o pfet_01v8 do sky130 tem `|V_th|` bem maior, então o nó de
referência assenta mais baixo por física, não por erro. O critério testava o meu palpite de
`V_th`, não a migração. **O critério 2 — medir a corrente entregue — é o certo, e supersede
este.** Registrado como erro de pré-registro.

## B · Convergência

| tstep | f (Hz) | desvio | P1 | P2 | P total | pulso |
|---|---|---|---|---|---|---|
| 2 µs | 139,582 | — | 2,364 nW | 3,671 nW | 6,035 nW | 88,84% |
| 1 µs | 139,582 | −0,000% | 2,379 | 3,803 | 6,182 | 88,84% |
| 0,5 µs | 139,582 | −0,000% | 2,329 | 3,697 | 6,026 | 88,84% |
| 0,125 µs | 139,582 | **−0,000%** | 2,318 | 3,854 | 6,172 | 88,84% |

Frequência invariante em **0,000%** sobre 16× de `tstep`. Potência varia 2,6% (0,16 nW em
absoluto). Passa com folga.

## C · A curva f–I — reproduz

| Iin (pA) | 1 | 2 | 3 | 5 | 7 | 10 | 15 | 20 | 30 | 50 | 70 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f (Hz) | 13,605 | 27,667 | 41,687 | 69,686 | 97,660 | 139,582 | 209,386 | 279,115 | 418,372 | 696,202 | 973,316 | 1387,685 |
| f/Iin | 13,605 | 13,833 | 13,896 | 13,937 | 13,951 | 13,958 | 13,959 | 13,956 | 13,946 | 13,924 | 13,905 | 13,877 |
| CV ISI (%) | 0,0016 | 0,0021 | 0,0019 | 0,0007 | 0,0016 | 0,0005 | 0,0025 | 0,0022 | 0,0019 | 0,0003 | 0,0027 | 0,0010 |
| P total (nW) | 4,30 | 4,66 | 5,00 | 5,35 | 5,64 | 6,03 | 6,71 | 7,72 | 8,32 | 9,81 | 11,18 | 13,67 |
| pulso (% VDD) | 88,39 | 88,47 | 88,53 | 88,64 | 88,73 | **88,84** | 89,01 | 89,14 | 89,38 | 89,74 | 90,03 | 90,37 |

**Ajuste linear com intercepto livre:** `f = 13,88639·Iin + 0,6269 Hz`, **R² = 0,99999597**.
Zona morta implícita: **−45,2 fA** — negativa, isto é, nenhuma.
**Ajuste log–log:** expoente **1,00270**, R² = 0,99998279.

### Comparação direta com o nível 1

| | nível 1 | sky130 | diferença |
|---|---|---|---|
| f no ponto nominal | 138,279 Hz | **139,582 Hz** | **+0,9%** |
| ganho f–I | 13,794 Hz/pA | **13,886 Hz/pA** | **+0,7%** |
| R² (intercepto livre) | 0,99999917 | 0,99999597 | ligeiramente pior |
| expoente log–log | 1,00054 | 1,00270 | +0,2% |
| resíduo máximo | 2,73% (em 1 pA) | **6,68%** (em 1 pA) | **2,4× pior** |
| deriva de f/Iin na faixa | 0,7% | 2,6% | 3,7× pior |
| CV do ISI | 0,0023–0,0048% | 0,0003–0,0027% | melhor |

**A função de transferência reproduz.** Ganho dentro de 0,7%, linearidade preservada,
sem zona morta. Isso é o resultado central: o modelo de primeira ordem
`T = Cfb·VDD/Iin` é capacitivo, não depende do transistor, e a migração confirma isso.

**Onde o sky130 se separa é no extremo inferior.** O resíduo em 1 pA passa de 2,73% para
6,68%, e o sinal é negativo — a frequência fica **abaixo** da reta. É a fuga sub-limiar
aparecendo, exatamente onde eu previ que apareceria.

### A fuga, inferida da própria curva

| | valor |
|---|---|
| f/`Iin` no platô (10 a 30 pA) | 13,958 Hz/pA |
| f/`Iin` em 1 pA | 13,605 Hz/pA |
| corrente efetiva em 1 pA | 0,9747 pA |
| **fuga inferida no nó `mem`** | **25,3 fA** |
| limite superior medido no transistor isolado (`Vds` = 1,8 V) | 84,7 fA |

**3,3× menor em operação que o limite superior** — exatamente o que a ressalva do `Vds`
antecipava, já que `mem` opera entre −0,13 e 0,57 V e não em 1,8 V. A ressalva estava certa
e agora está quantificada.

## D · O consumo despenca 14× — e o teto da faixa útil some

| | nível 1 | sky130 |
|---|---|---|
| P no ponto nominal | 85,37 nW | **6,03 nW** |
| P na faixa de 1 a 100 pA | 80,5 a 112,4 nW | **4,30 a 13,67 nW** |
| cruza os 100 nW em | `Iin` ≈ 54 pA | **nunca** |
| P1 (1º estágio) | 1,78 nW | 2,33 nW |
| P2 (2º estágio) | 85,67 nW | **3,70 nW** |

**O piso estático de 80,9 nW era quase todo do 2º estágio, e some.** P2 cai de 85,7 para
3,7 nW — fator **23**.

**Consequência direta para a decisão desta semana:** o teto de 54 pA que motivou limitar a
faixa útil a 1–50 pA (`CLAUDE.md` §6) **era artefato dos modelos nível 1**. No sky130 a
potência em 100 pA é 13,67 nW, **7,3× abaixo do orçamento**. A faixa útil pode voltar a ser
de dois decades, e o teto da tesoura (§5) desaparece. **Não alterei a decisão** — ela é do
autor do projeto, e está registrada como pendência.

## E · O preço: o pulso de saída reprova

| | nível 1 | sky130 |
|---|---|---|
| pulso no ponto nominal | 92,22% | **88,84%** |
| faixa de 1 a 100 pA | 92,15 a 92,45% | **88,39 a 90,37%** |
| critério ≥ 90% | aprova em todos | **reprova em `Iin` ≤ 50 pA** |

Passa só nos dois pontos mais altos (70 e 100 pA), que estão fora da faixa útil decidida.
**No ponto nominal reprova por 1,16 pontos percentuais.**

### O mecanismo — uma causa, dois efeitos

O nível baixo de `n1` subiu de **0,051 V** (nível 1) para **0,591 V** (sky130):

| Iin | n1 mínimo | out máximo | pulso |
|---|---|---|---|
| 1 pA | 0,593 V | 1,591 V | 88,39% |
| 10 pA | 0,591 V | 1,599 V | 88,84% |
| 100 pA | 0,582 V | 1,627 V | 90,37% |

`n1` baixo é onde `M1n`, puxando para o terra, equilibra os 10 nA que `Mbp1` injeta. No
nível 1, `M1n` com a membrana em ~0,56 V e `VTO` = 0,45 V está em condução forte e vence
folgadamente 10 nA, então `n1` vai quase a zero. No sky130, `M1n` na mesma tensão de porta
está em **inversão fraca** — o `V_th` é maior e a condução é exponencial, não quadrática —
e o equilíbrio com 10 nA acontece com `n1` 0,54 V mais alto.

Disso saem os dois efeitos, do mesmo tronco:

- **Bom:** com `n1` alto, o 2º inversor passa muito menos tempo com os dois transistores
  conduzindo. A corrente de curto despenca e **P2 cai 23×**.
- **Ruim:** com `n1` parando em 0,591 V, `M2n` continua **parcialmente ligado** quando
  deveria cortar. `out` fica preso num divisor entre `M2p` (limitado pelo espelho) e `M2n`,
  e **não alcança o trilho**. Daí 88,8% em vez de 92,2%.

Não são dois problemas: é um só, com sinais opostos.

---

## F · Placar das previsões pré-registradas

| Previsão | Faixa prevista | Medido | Veredito |
|---|---|---|---|
| Frequência | 60 a 200 Hz, centro 110 | **139,58 Hz** | **dentro da faixa**, mas errei a direção: previ queda, subiu 0,9% |
| Ganho f–I | 6 a 20 Hz/pA, centro 11 | **13,886** | **dentro**, centro errado por 26% |
| Consumo | 60 a 250 nW, centro 110 | **6,03 nW** | **REFUTADA** — 10× abaixo do piso da faixa |
| Zona morta | 50 a 150 fA | **nenhuma** (−45 fA no ajuste; 25 fA inferida) | **parcialmente refutada** — a fuga real é 25 fA e não produz zona morta |
| Migração falhou? | espelhos dentro de 2× | 0,09% e 0,54% | **não falhou** |
| Critério `rp` a menos de 300 mV | — | 409 e 500 mV | **critério mal formulado**, ver §A |

**A refutação que importa é o consumo.** Errei por um fator de 10 a 40, e errei por raciocinar
que a condução sub-limiar do sky130 **acrescentaria** corrente estática. Acrescenta, mas o
efeito dominante é o oposto: o `V_th` mais alto e a transição exponencial deslocam `n1` para
cima e **fecham** a janela de curto do 2º estágio. Eu tinha os dois efeitos na cabeça e
apostei no errado.

## G · Gatilhos de parada — um disparou

| gatilho pré-registrado | estado |
|---|---|
| Zona morta dura (não disparar em 1 pA, ou > 500 fA) | não disparou — não há zona morta |
| Perda de linearidade (R² < 0,999 ou expoente fora de 0,95–1,05) | não disparou — R² = 0,999996, expoente 1,0027 |
| Consumo acima de 171 nW | não disparou — despencou para 6 nW |
| **Pulso abaixo de 90% de VDD** | **DISPAROU — 88,84% no ponto nominal** |

**Parei aqui. Nenhuma dimensão foi alterada**, conforme instruído.

## H · Pendências

1. **O pulso reprova o critério de 90% em toda a faixa útil.** Causa identificada (§E), não
   corrigida. As direções óbvias mexem em dimensão ou polarização e por isso não foram
   tocadas.
2. **A faixa útil de 1–50 pA pode ser reaberta.** O teto de 54 pA era artefato de nível 1.
   Decisão do autor.
3. **A tesoura perdeu o teto, mas não o piso.** O limite de consumo desapareceu; a fuga
   térmica continua de pé e agora tem base melhor: 25 fA em operação a 27 °C, e não 84,7.
   Reprojetando a tesoura com 25 fA, o cruzamento de 1 pA se desloca para temperatura mais
   alta. Não recalculei — é matéria da etapa 3 e depende da faixa térmica ainda indefinida.
4. **Só o canto `tt` a 27 °C.** Cantos e temperatura são a etapa 3.
5. **`Cmem` e `Cfb` continuam ideais.** Capacitores reais do PDK são decisão de layout.
6. **Sem descasamento e sem parasitas** — etapas 2 e 8.

## Arquivos

- `migracao_sky130.png` — a figura (4 painéis)
- `previsao_pre_registrada.md` — as previsões, commitadas antes da medida
- `raw/` — netlists de todos os pontos, incluindo `teste_espelho.cir`
- `../../scripts/run_sky130.py`, `../../scripts/plots_sky130.py`
