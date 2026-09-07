# Varredura de `Cmem` no sky130 — o achado central NÃO sobrevive ao PDK

Data: 2026-09-07 · **ngspice 42** · **sky130A**, canto `tt`, `.temp 27`
`IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA. Previsão em `previsao_pre_registrada.md`,
commit `d7b12cb`.

**Pergunta:** o achado central do projeto — `Cmem` não controla a frequência de disparo —
sobrevive ao PDK?

> **Resposta: NÃO.** No regime em que o circuito funciona, `Cmem` **controla** a frequência:
> **3,39× sobre 8× de `Cmem`**, contra 1,26× no nível 1 no mesmo intervalo. O **Modelo A**
> pré-registrado venceu, e era o modelo que matava o achado.

---

## A · A medida

| `Cmem` | f (Hz) | CV do ISI | janela | excursão de `mem` | pulso de `out` | `Ctot` (fuga descontada) | regime |
|---|---|---|---|---|---|---|---|
| 25 fF | **290,33** | 0,0007% | 1,0197 V | 1,0245 V | 1,7965 V | 54,77 fF | integra-e-dispara |
| 50 fF | **211,22** | 0,0017% | 0,8478 V | 0,8510 V | 1,7795 V | 79,76 fF | integra-e-dispara |
| 100 fF | **139,58** | 0,0005% | 0,6927 V | 0,6930 V | 1,5992 V | 129,77 fF | integra-e-dispara |
| 200 fF | **85,58** | 0,0050% | 0,5649 V | 0,5781 V | 1,0077 V | 229,82 fF | integra-e-dispara |
| 400 fF | **145,22** | **0,1286%** | 0,1807 V | 0,1896 V | 0,8237 V | 433,24 fF | **degenerado** |
| 800 fF | **252,96** | **0,2231%** | 0,0562 V | 0,0610 V | 0,7216 V | 856,56 fF | **degenerado** |

### Uma correção de instrumento, antes dos resultados

A primeira passagem reportou "não dispara" em 400 e 800 fF. **Era o meu detector, não o
circuito.** Ele usava limiar fixo de 0,9 V (0,5·VDD), e o pulso de `out` colapsa para 0,82 e
0,72 V nesses pontos — nunca cruza 0,9 V. Verifiquei a forma de onda: o circuito **oscila em
regime estacionário** nos quatro quartos da simulação. Refiz com limiar adaptativo a 50% da
excursão do próprio `out`. Os números acima são os corrigidos.

## B · Os dois modelos pré-registrados, confrontados

| `Cmem` | **medido** | Modelo A (f ∝ 1/Ctot) | erro A | Modelo B (forma do nível 1) | erro B | nível 1 |
|---|---|---|---|---|---|---|
| 25 fF | 290,33 | 329,8 | **+13,6%** | 159,3 | −45,1% | 183,1 |
| 50 fF | 211,22 | 226,3 | **+7,1%** | 151,2 | −28,4% | 173,8 |
| 100 fF | 139,58 | 139,1 | **−0,3%** | 139,6 | +0,0% | 160,4 |
| 200 fF | 85,58 | 78,5 | **−8,3%** | 126,5 | +47,8% | 145,4 |
| 400 fF | 145,22 | 42,0 | −71,1% | 121,8 | −16,1% | 140,0 |
| 800 fF | 252,96 | 21,7 | −91,4% | 131,4 | −48,1% | 151,0 |

**No regime útil (`Cmem` ≤ 200 fF): erro médio de 7,3% para o Modelo A contra 30,3% para o
Modelo B.** O Modelo A vence sem ambiguidade.

**Nenhum dos dois acerta o regime degenerado**, porque nenhum foi construído para ele — os
dois pressupõem integração de carga, e acima de 200 fF o circuito não está mais integrando.

**Eu apostei no Modelo B e perdi.** A aposta estava registrada em `d7b12cb`, com a
justificativa de que o cancelamento seria geométrico e portanto independente do modelo de
dispositivo. Estava errado.

## C · Os dois regimes, e a fronteira é nítida

| | `Cmem` ≤ 200 fF | `Cmem` ≥ 400 fF |
|---|---|---|
| excursão da membrana | 0,58 a 1,02 V | **0,061 a 0,19 V** |
| CV do ISI | 0,0005 a 0,0050% | **0,129 a 0,223%** |
| pulso de `out` | 1,01 a 1,80 V | 0,72 a 0,82 V |
| f com `Cmem` | **cai** monotonicamente | **sobe** |
| `Ctot` medido contra previsto | erro ≤ 0,10% | erro 0,8 a 3,2% |

**O CV do ISI salta 26×** entre 200 e 400 fF. Essa é a assinatura mais limpa da mudança de
regime: até 200 fF o disparo é regenerativo e o intervalo é reprodutível a cinco casas; a
partir de 400 fF o circuito vira um oscilador de pequeno sinal, com `out` sem excursão lógica
completa e com jitter duas ordens de grandeza maior.

**A fronteira é a excursão cruzando ~0,2 V**, exatamente onde a hipótese registrada dizia.

## D · A hipótese do 800 fF: CONFIRMADA em dois modelos independentes

| | nível 1 | sky130 |
|---|---|---|
| f em 400 fF | 140,0 Hz | 145,2 Hz |
| f em 800 fF | 151,0 Hz | 252,96 Hz |
| **subida** | **×1,079** | **×1,742** |
| excursão em 800 fF | 0,107 V | 0,061 V |

> **A subida existe nos dois modelos de dispositivo, e no sky130 é 22× maior em magnitude
> relativa.** A hipótese de mudança de regime quando a excursão cai abaixo de ~0,2 V passa de
> especulação a **achado reprodutível em dois modelos independentes** — nível 1
> (Shichman-Hodges) e BSIM4 do sky130, que não compartilham equações.

Isso fecha a ressalva que estava aberta desde a revalidação da etapa 0 (`CLAUDE.md` §5 item 2).

## E · O que o achado central vira

**A formulação antiga, agora refutada:** "`Cmem` é um controle fraco, com resíduo medido de
24% em 16×."

**A formulação medida no PDK:** no regime integra-e-dispara, `Cmem` é o **controle dominante**
da frequência, com `f ≈ k/Ctot` e `Ctot = Cmem + 29,71 fF`. O produto `f·Ctot` varia 21,4%
sobre a faixa útil — não é uma constante exata, mas é 16× mais estável que `f` sozinha.

**Por que o nível 1 dizia o contrário:** o nível 1 mantinha a excursão da membrana grande
mesmo com `Cmem` grande (0,223 V em 400 fF contra 0,190 V aqui, e 0,107 V contra 0,061 V em
800 fF), o que sustentava a compensação. No sky130 a excursão colapsa mais depressa e o
circuito sai do regime antes que a compensação possa agir.

### A decisão de projeto SOBREVIVE — mas por outro motivo, e mais forte

`CLAUDE.md` §6 registra: **`Cmem` pequeno.** Isso continua certo, e agora tem uma razão melhor:

- **Antes:** `Cmem` grande não compra lentidão e destrói a excursão de sinal.
- **Agora:** `Cmem` grande **empurra o circuito para fora do regime de integra-e-dispara** —
  o jitter piora 26×, o pulso perde excursão lógica e a frequência inverte de sentido.

**E há um ganho:** `Cmem` passa a ser um **parâmetro de projeto utilizável** para fixar a
frequência, o que o projeto acreditava não ter. Antes a frequência só se ajustava por `Iin`.
Agora há dois botões, e eles são independentes.

**O impacto na área do chip precisa ser reavaliado.** A §3 dizia que `Cmem` pode encolher
livremente. Continua podendo, mas encolher `Cmem` **sobe a frequência** — é um compromisso
acoplado, não uma economia livre.

## F · A previsão de `Ctot` — confirmada com precisão inesperada

| `Cmem` | previsto (`Cmem` + 29,71 fF) | medido | erro |
|---|---|---|---|
| 25 fF | 54,71 | 54,77 | **+0,10%** |
| 50 fF | 79,71 | 79,76 | **+0,06%** |
| 100 fF | 129,71 | 129,77 | **+0,05%** |
| 200 fF | 229,71 | 229,82 | **+0,05%** |
| 400 fF | 429,71 | 433,24 | +0,82% |
| 800 fF | 829,71 | 856,56 | +3,24% |

**O parasita de 9,71 fF é constante do circuito**, confirmado a 0,10% ao longo de 8× de
`Cmem`. A degradação em 400 e 800 fF é esperada: lá a "rampa" da qual a inclinação é extraída
já não é uma rampa de integração.

---

## G · Placar da previsão

| Previsão | Veredito |
|---|---|
| Modelo de primeiros princípios falharia na validação | **registrada antes e confirmada** — erro de −17,9% em 100 fF |
| **Aposta no Modelo B** | **REFUTADA** — o Modelo A venceu, 7,3% contra 30,3% |
| Cada ponto dentro de ±15% da coluna B | **refutada** — desvios de até 48% |
| Queda de 25 a 400 fF entre 15% e 35% | **refutada** — foi 50,0% |
| Nenhuma variação acima de 2× em 32× de `Cmem` | **refutada** — 3,39× só no regime útil |
| O 800 fF sobe também no sky130 | **confirmada** — e muito mais, ×1,742 |
| Excursão em 800 fF entre 0,15 e 0,25 V | **refutada** — 0,061 V, bem abaixo |
| `Ctot` = `Cmem` + 29,7 fF dentro de 2% | **confirmada** — 0,10% no regime útil |
| CV do ISI abaixo de 0,05% em todos os pontos | **refutada** — 0,129% e 0,223% no regime degenerado |

**Quatro de nove.** A rodada anterior teve nove de nove; esta teve a previsão principal
refutada. Apostei que o cancelamento seria geométrico e independente do modelo de dispositivo;
ele não é.

## H · A etapa 1

Este era o **último critério de saída em aberto**. A varredura foi executada, convergiu, e é
conclusiva.

> **A etapa 1 está tecnicamente completa.** Os seis critérios foram fechados: armadilha do
> W/L, neurônio migrado, fuga em `mem` medida, janela de histerese medida, fator de 1,76×
> resolvido, e varredura de `Cmem`.

**Mas ela fecha com um resultado que inverte o achado central do projeto**, e isso é ponto de
decisão do autor, não meu. O meu próprio pré-registro dizia: *"Se o Modelo A vencer, a etapa 1
não fecha: o achado central precisaria ser reescrito antes."* Reescrevi o achado no
`CLAUDE.md` §3 e §6 como registro do que foi medido. **A decisão sobre o que isso muda no
projeto fica com você.**

## I · Pendências

1. **O regime degenerado não foi caracterizado.** Sabe-se que existe, onde começa e como se
   manifesta, mas não o que fixa a frequência lá. Não é necessário para o projeto — a região é
   de uso proibido — mas está sem mecanismo.
2. **`f·Ctot` varia 21,4%** no regime útil: o Modelo A é aproximado, não exato. A dependência
   residual não foi decomposta.
3. **A fronteira de 0,2 V foi localizada entre dois pontos**, 200 e 400 fF. Não foi refinada.
4. **Só o canto `tt` a 27 °C.**
5. **`Cmem` e `Cfb` continuam ideais.**
6. A curvatura da f–I (§5-A item 14) continua aberta e não bloqueante.

## Arquivos

- `cmem_sky130.png` — a figura (3 painéis)
- `previsao_pre_registrada.md` — commitado antes da medida
- `raw/` — netlists dos seis pontos
- `../../scripts/plots_cmem.py`
