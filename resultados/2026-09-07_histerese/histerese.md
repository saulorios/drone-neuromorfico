# A janela de histerese medida — NÃO explica a curvatura, e o 1,76× está fechado

Data: 2026-09-07 · **ngspice 42** · **sky130A**, canto `tt`, `.temp 27`
`IB1` = 10 nA, `IB2` = 3 µA, `tstep` = 0,2 µs, dimensões inalteradas.
Medida **da forma de onda**, não inferida de modelo. Previsão em
`previsao_pre_registrada.md`, commit `22606e8`.

**Pergunta, com duas funções.** (1) A janela varia com `Iin` o bastante para explicar a
curvatura da f–I? **Não.** (2) O fator 1,76× da etapa 0 sobrevive ao PDK? **Sim, e agora está
medido: 2,46×.**

---

## A · A janela, medida

| `Iin` | V de disparo | V mínimo (reset) | **Janela** | f (Hz) |
|---|---|---|---|---|
| 1 pA | 0,54976 ± 2,3 mV | −0,12806 ± 11 µV | **0,677818 V** | 13,605 |
| 3 pA | 0,54900 ± 1,3 mV | −0,12808 ± 13 µV | **0,677081 V** | 41,687 |
| 10 pA | 0,55118 ± 2,3 mV | −0,12807 ± 2,3 µV | **0,679244 V** | 139,582 |
| 30 pA | 0,55302 ± 1,8 mV | −0,12800 ± 11 µV | **0,681015 V** | 418,380 |
| 100 pA | 0,56046 ± 1,9 mV | −0,12786 ± 3,5 µV | **0,688321 V** | 1387,680 |

(± = desvio entre ciclos dentro de cada corrida.)

**O fundo é fixo.** −0,12806 a −0,12786 V: **0,16% de variação sobre 100× de corrente**. Era
o previsto — o fundo é fixado pelo degrau de `Cfb`, que não depende de `Iin`.

**Só o topo se move**, e pouco: 0,5498 a 0,5605 V, 1,9%.

## B · A resposta: a janela não explica

| | valor |
|---|---|
| variação da janela em 1 pA (ref. 10 pA) | **−0,210%** |
| necessário para explicar a curvatura | **+4,15%** |
| razão | **20× pequena demais, e de sinal oposto** |

Variação total sobre dois decades: **+1,55%**, e ela **cresce com `Iin`** (0,6778 → 0,6883 V).

**Isso confirma a previsão pré-registrada, inclusive no mecanismo.** Eu havia escrito que
esperava variação abaixo de 2% e no sentido errado, porque `n1` tem a taxa limitada a
`IB1` = 10 nA pelo espelho: com a rampa rápida o inversor fica para trás e `mem` precisa subir
**mais** antes de comutar. É exatamente o que a coluna de V de disparo mostra — o topo sobe
11 mV de 1 para 100 pA.

> **A janela está descartada como causa da curvatura.** Conforme combinado, não forço o
> ajuste: digo que a causa é outra.

## C · O achado lateral que quase virou um falso positivo

Medindo `Ctot` pela inclinação da rampa (`Ctot = Iin / (dV/dt)`), como pré-registrado, apareceu
uma variação de **+5,70%** entre 1 e 10 pA — grande o bastante para explicar a curvatura
sozinha. Por um momento pareceu ser a resposta.

**Não é. É a fuga disfarçada.** A conta correta é
`dV/dt = (Iin − fuga)/Ctot_real`, logo
`Ctot_aparente = Ctot_real · Iin/(Iin − fuga)`. Com a fuga de ~60 fA medida por DC na rodada
anterior, no trecho de tensão onde o ajuste foi feito:

| `Iin` | Ctot aparente | fator `Iin/(Iin−60 fA)` | **Ctot real** |
|---|---|---|---|
| 1 pA | 137,94 fF | 1,06383 | **129,66 fF** |
| 3 pA | 132,35 fF | 1,02041 | **129,70 fF** |
| 10 pA | 130,50 fF | 1,00604 | **129,72 fF** |
| 30 pA | 129,99 fF | 1,00200 | **129,73 fF** |
| 100 pA | 129,81 fF | 1,00060 | **129,73 fF** |

> **`Ctot` é constante: 129,71 fF, com 0,05% de espalhamento sobre dois decades.**

E a verificação cruzada é forte: a razão prevista pela curva de fuga é **+5,745%**; a medida é
**+5,701%**. Concordam em 0,04 ponto percentual. **Duas medidas independentes — uma varredura
DC de fuga e a inclinação de uma rampa transiente — batem entre si.**

**Consequência de método:** o termo `Ctot` e o termo fuga são **o mesmo efeito**. Contar os
dois na decomposição seria contagem dupla, e foi o erro que quase cometi.

## D · O modelo montado das três medidas erra o SINAL da curvatura

Com `Ctot` = 129,71 fF medido, a janela medida por ponto, e a curva de fuga DC medida:

`T = Ctot · ∫[V_min → V_disparo] dV/(Iin − fuga(V))`

| `Iin` | f prevista | f medida | erro |
|---|---|---|---|
| 1 pA | 13,778 Hz | 13,605 Hz | +1,27% |
| 3 pA | 41,219 Hz | 41,687 Hz | −1,12% |
| 10 pA | 135,581 Hz | 139,582 Hz | −2,87% |
| 30 pA | 403,967 Hz | 418,380 Hz | −3,44% |
| 100 pA | 1342,612 Hz | 1387,680 Hz | −3,25% |

**A frequência absoluta é reproduzida dentro de 3,4%** — bom, para um modelo construído
inteiramente de grandezas medidas, sem nenhum parâmetro ajustado.

**Mas a curvatura sai com o sinal errado:**

| | 1 pA contra 10 pA |
|---|---|
| curvatura **prevista** pelo modelo | **+1,622%** |
| curvatura **medida** | **−2,530%** |
| discrepância | **4,15 pontos percentuais** |

Os 4,15 pontos são exatamente o alvo que restava. **O modelo das três medidas não o alcança —
ele aponta para o outro lado.**

> **Duas hipóteses estão agora derrubadas:** a fuga (rodada anterior) e a janela (esta). A
> curvatura da f–I em corrente baixa continua **sem explicação**.

## E · O fator 1,76× da etapa 0 — CRITÉRIO 4 FECHADO

Aberto desde a etapa 0, quando o modelo `T = Cfb·VDD/Iin` previu 278 Hz e mediu-se 158 Hz. A
ação registrada era "medir a janela de histerese diretamente em vez de inferi-la". Feito, e com
`Ctot` **medido**, não suposto:

| base do modelo | ΔV previsto | janela medida | **razão** |
|---|---|---|---|
| `VDD·Cfb/Ctot`, com VDD = 1,8 V | 0,27586 V | 0,679244 V | **2,462×** |
| `ΔV(out)·Cfb/Ctot`, com a excursão real de `out` = 1,624 V | 0,24889 V | 0,679244 V | **2,729×** |

Em termos de período: modelo 3,600 ms, medido 7,164 ms → **1,990×**, contra **1,76×** no
nível 1.

> **O fator sobrevive ao PDK e é maior: 1,99× em período, 2,46× em janela.**
> Previsão pré-registrada: 2,3× a 2,9× em janela. **Confirmada.**

### Por que a razão em janela (2,46×) difere da razão em período (1,99×)

Porque **a rampa não percorre a janela inteira**:

| | valor |
|---|---|
| excursão que a rampa de fato percorre (`T·Iin/Ctot`) | **0,5490 V** |
| janela total medida | **0,6792 V** |
| diferença | **0,1303 V** |
| undershoot medido | **0,128 V** |

A diferença **é o undershoot**, dentro de 2 mV. O trecho de −0,128 V até ~0 **não é integrado
por `Iin`** — é atravessado depressa pela injeção de junção medida na rodada anterior (3,7 pA
em −0,127 V, isto é, 370% de `Iin` no ponto de 1 pA).

**Isso amarra as duas rodadas:** a medida de fuga previu que o trecho negativo seria
atravessado rápido, e a medida de janela confirma, pela diferença entre a janela total e a
excursão efetivamente integrada.

---

## F · Placar da previsão

| Previsão | Veredito |
|---|---|
| A janela **não** explica o desvio | **confirmada** |
| Variação abaixo de 2% entre 1 e 100 pA | **confirmada** — 1,55% |
| Variação no sentido **errado** (cresce com `Iin`) | **confirmada** |
| Mecanismo (a): `n1` limitado a 10 nA faz o topo subir com `Iin` | **confirmado** — topo sobe 11 mV |
| Mecanismo (b): undershoot não varia | **confirmado** — 0,16% em 100× |
| V de disparo 0,50 a 0,57 V | **confirmada** — 0,5498 a 0,5605 |
| Janela 0,63 a 0,70 V | **confirmada** — 0,678 a 0,688 |
| Fator em janela: 2,3× a 2,9× | **confirmada** — 2,46× e 2,73× |
| *(pré-registrado como candidato futuro)* dependência de `Ctot` | **investigado e descartado** — `Ctot` é constante em 0,05% |

Nove de nove. Foi a rodada em que mais acertei, e ela produziu um resultado **negativo**: a
hipótese que eu havia levantado na rodada anterior está errada.

## G · Pendências

1. **A curvatura da f–I continua sem explicação**, agora com **duas** hipóteses derrubadas por
   medida direta. O modelo das três medidas erra por 4,15 pontos percentuais **no sentido
   oposto** ao observado — não é um resíduo pequeno, é uma discordância de sinal.
   **Candidato que ainda não foi testado:** que o desvio de −2,53% esteja dentro do erro do
   próprio ajuste da f–I e não seja efeito físico. Não verifiquei a barra de erro daquele
   ajuste.
2. **O modelo das três medidas erra a frequência absoluta por até 3,4%**, com sinal
   sistemático (subestima acima de 3 pA). Não investigado.
3. **A janela foi medida com `out` cruzando 0,5·VDD como definição de disparo.** Outra
   definição — início da comutação, pico de `mem` — daria outro número. A escolha está
   registrada e é consistente entre os cinco pontos, mas não é única.
4. **Só o canto `tt` a 27 °C.**
5. **`Cmem` e `Cfb` continuam ideais.** `Ctot` = 129,71 fF contra os 120 fF ideais: os
   ~9,7 fF de diferença são porta e junção, e não foram decompostos.

## Arquivos

- `histerese.png` — a figura (4 painéis)
- `previsao_pre_registrada.md` — commitado antes da medida
- `raw/` — netlists dos cinco pontos
- `../../scripts/plots_histerese.py`
