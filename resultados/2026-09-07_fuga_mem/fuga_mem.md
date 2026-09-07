# A fuga no nó `mem`, medida diretamente — os 25,3 fA NÃO se confirmam

Data: 2026-09-07 · **ngspice 42** · **sky130A**, canto `tt`, `.temp 27`
Método: **ponto de operação DC** (`CLAUDE.md` §7), circuito completo, `mem` forçado por fonte
de tensão e varrido. `Iin` removida — a corrente na fonte **é** a fuga líquida que o nó vê.
Tolerâncias: `abstol` = 1e-18, `vntol` = 1e-12, `reltol` = 1e-6, `gmin` = 1e-18.
Previsão em `previsao_pre_registrada.md`, commit `c3ce36e`.

**Pergunta:** a fuga no nó `mem`, medida diretamente, confirma os 25,3 fA inferidos da curva?

**Resposta: não.** E a discordância é mais informativa que um simples desvio de valor: a fuga
não é um número, **muda de sinal** no meio da excursão, e o efeito líquido tem o **sinal
oposto** ao que a inferência supunha.

---

## A · A curva

| V(mem) | corrente (fA) | sentido | estado |
|---|---|---|---|
| −0,125 | **3 719,7** | **entrando** em `mem` | integração |
| −0,100 | 1 589,3 | entrando | integração |
| −0,050 | 264,7 | entrando | integração |
| −0,020 | 60,9 | entrando | integração |
| **0,000** | **−0,000** | — | integração |
| 0,010 | 18,0 | saindo | integração |
| 0,025 | 35,8 | saindo | integração |
| 0,050 | 49,0 | saindo | integração |
| 0,080 | 54,0 | saindo | integração |
| 0,100 | 55,4 | saindo | integração |
| 0,200 | 58,5 | saindo | integração |
| 0,300 | 60,4 | saindo | integração |
| 0,400 | 62,1 | saindo | integração |
| 0,450 | ~63 | saindo | último ponto antes do disparo |
| ≥ 0,455 | — | — | **disparou** — medida não vale |

**Ponto de disparo DC: entre 0,450 e 0,455 V.** Em operação `mem` chega a 0,562 V porque o
degrau de `Cfb` a empurra além do ponto DC — a diferença é o próprio efeito de histerese.

## B · A forma prevista bate; o valor não

| aspecto da previsão | previsto | medido | veredito |
|---|---|---|---|
| zero exato em `mem` = 0 | sim | **−0,000 fA** | **confirmado** |
| subida íngreme até ~100 mV, depois quase plana | sim | 0 → 55,4 fA em 100 mV; depois +12% em 300 mV | **confirmado** |
| variação no patamar | < 3× | **1,12×** (55,4 a 62,1 fA) | **confirmado, e mais plano do que eu esperava** |
| valor no topo da faixa medível | 45 a 62 fA | **~63 fA** | **na borda superior** |
| média no tempo, rampa positiva | 35 a 55 fA, centro 45 | **56,0 fA** | **acima da faixa por 2%** |

A forma segue exatamente o fator `(1 − e^{−Vds/V_T})` previsto, com `V_T` = 25,9 mV: metade
do patamar em ~18 mV, 95% em ~78 mV. **O mecanismo estava certo.**

**O patamar é 2,2× os 25,3 fA inferidos.** Nesse ponto minha previsão estava mais próxima da
verdade que a inferência anterior.

## C · O achado que não estava na previsão: a junção conduz direto abaixo de zero

Para `mem` < 0, a junção de dreno do `Mrst` fica **diretamente polarizada** e **injeta**
corrente no nó, em vez de drená-la:

| V(mem) | injeção | em relação a `Iin` = 10 pA | em relação a `Iin` = 1 pA |
|---|---|---|---|
| −0,127 V (o mínimo em operação) | **+3,7 pA** | 37% | **370%** |
| −0,100 V | +1,6 pA | 16% | 159% |
| −0,050 V | +0,26 pA | 2,6% | 26% |

Eu havia previsto que a curva passaria por zero, mas **não quantifiquei o outro lado**. Em
`Iin` = 1 pA a injeção no fundo da excursão é quase **4× a corrente de entrada**.

**Duas consequências, ambas novas:**

1. **Para o circuito:** a rampa não começa em regime de integração pura. O primeiro trecho,
   de −0,127 V até 0, é atravessado com corrente líquida maior que `Iin`, e tanto mais
   quanto menor for `Iin`.
2. **Para o silício, e esta é mais séria:** uma junção n+ diretamente polarizada **injeta
   portadores minoritários no substrato**. Isso é caminho de *latch-up* e de acoplamento
   entre neurônios vizinhos, e **não está no mapa de riscos do dossiê §8**. Não é uma questão
   de corrente — é uma questão de isolamento.

## D · O efeito líquido tem o sinal OPOSTO ao que a inferência supunha

A fuga efetiva — a que reproduz o mesmo tempo de rampa com valor constante,
`I_ef = Iin − ΔV/∫dV/(Iin − I_fuga)` — sobre a excursão completa:

| `Iin` | tempo de rampa | fuga efetiva | efeito na frequência |
|---|---|---|---|
| 1 pA | 0,973× | **−27,6 fA** | **+2,76%** |
| 3 pA | 0,976× | −74,2 fA | +2,47% |
| 10 pA | 0,989× | −112,1 fA | +1,12% |
| 30 pA | 0,996× | −129,2 fA | +0,43% |
| 100 pA | 0,999× | −136,4 fA | +0,14% |

Fuga efetiva **negativa** significa **ajuda**: sobre a excursão inteira, a injeção abaixo de
zero mais que compensa a fuga acima. A rampa fica mais rápida, e **mais rápida em corrente
baixa**.

Considerando só a parte positiva da rampa (78% da excursão), o valor é **+56,0 fA**,
praticamente independente de `Iin` (56,06 em 1 pA, 55,96 em 10 pA).

### Por que isso derruba a interpretação anterior

Na rodada da migração, o ponto de 1 pA da curva f–I ficou **2,5% abaixo** de uma reta
proporcional ancorada em 10 pA, e eu atribuí isso a 25,3 fA de fuga.

A medida direta diz que a fuga, sobre a excursão real, produz **+1,7%** de desvio relativo
nesse mesmo par de pontos — **para cima, não para baixo**.

> **Os 25,3 fA eram uma atribuição errada.** A fuga existe, é maior do que eu inferi (56 fA
> na rampa positiva), mas ela **não explica** a curvatura da f–I em corrente baixa — explica
> um desvio de sinal contrário. A causa da curvatura é outra, ainda não identificada.

O candidato mais provável é a **janela de histerese variar com `Iin`** — o que é exatamente o
próximo critério de saída da etapa 1, e por instrução não foi antecipado aqui.

## E · Consequência para a tesoura (§5)

O valor único a projetar termicamente passa a ser o **patamar medido**, não os 25,3 fA:

| base | 1 pA | 10 pA | 100 pA |
|---|---|---|---|
| 25,3 fA (inferido, **revogado**) | 69 a 80 °C | 96 a 113 °C | 123 a 146 °C |
| **56 fA (patamar medido)** | **60 a 69 °C** | **87 a 102 °C** | **113 a 135 °C** |

**As temperaturas de cruzamento descem 9 a 11 °C.** Muda a margem, não a conclusão — que era
o que eu havia previsto.

**Ressalva importante sobre esta projeção:** ela usa só o patamar e ignora que a injeção
abaixo de zero **também cresce com a temperatura**, e mais rápido, por ser condução direta de
junção. Os dois termos crescem juntos e em sentidos opostos. A tesoura projetada com um termo
só é conservadora, mas não é fiel. **A projeção térmica correta exige medir a curva inteira em
temperatura**, não escalar um número — matéria da etapa 3.

---

## F · Placar da previsão

| Previsão | Veredito |
|---|---|
| Forma: zero em `mem` = 0, íngreme até ~100 mV, depois plana | **confirmada** |
| Variação no patamar < 3× | **confirmada** — 1,12×, mais plano do que previ |
| Valor no topo: 45 a 62 fA | **confirmada** — ~63 fA, na borda |
| Média no tempo (rampa positiva): 35 a 55 fA | **quase** — 56,0 fA, 2% acima |
| Veredito: 25,3 fA baixo por 1,5 a 2× | **confirmado no valor** (2,2×) mas **a razão estava errada** |
| Tesoura desce 7 a 8 °C | **quase** — desce 9 a 11 °C |
| *(não previsto)* injeção direta abaixo de zero | **achado novo** |
| *(não previsto)* efeito líquido de sinal oposto | **achado novo, e derruba a atribuição anterior** |

Acertei a física do lado positivo quase inteira. Errei por **não olhar o outro lado da
excursão** — a previsão tratou `mem` < 0 como "sem viés" quando na verdade é a região de
maior corrente de toda a curva, por três ordens de grandeza.

## G · Pendências

1. **A curvatura da f–I em corrente baixa está sem explicação.** Não é fuga. Candidato:
   janela de histerese dependente de `Iin` — próximo critério de saída, não antecipado.
2. **A injeção no substrato não está no mapa de riscos** (dossiê §8). É risco de isolamento e
   de acoplamento entre neurônios, não de consumo. Precisa entrar.
3. **A projeção térmica da tesoura continua sendo extrapolação de um ponto**, e agora sabe-se
   que ela ignora um termo de sinal oposto que também cresce com T.
4. **A medida DC não vale acima de 0,45 V**, e em operação `mem` chega a 0,562 V. O trecho de
   0,45 a 0,562 V não foi caracterizado — ele só existe dinamicamente.
5. **Só o canto `tt` a 27 °C.**

## Arquivos

- `fuga_mem.png` — a figura (2 painéis)
- `previsao_pre_registrada.md` — commitado antes da medida
- `raw/fuga_mem.cir` — netlist da varredura DC
- `../../scripts/plots_fuga.py`
