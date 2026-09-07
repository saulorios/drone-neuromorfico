# Previsão pré-registrada — o achado central sobrevive ao PDK?

Escrita em 2026-09-07, **antes** de rodar. Commitada antes da medida.

**Pergunta:** varredura de `Cmem` no sky130. O achado central do projeto — `Cmem` não controla
a frequência — sobrevive ao PDK?

Ponto de operação: `IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA, canto `tt`, `.temp 27`.
`Cmem` em 25, 50, 100, 200, 400 e 800 fF, os mesmos valores do nível 1.

**Referência a bater** (nível 1, tolerâncias corrigidas): 183,1 / 173,8 / 160,4 / 145,4 /
140,0 / 151,0 Hz. Queda de 23,5% entre 25 e 400 fF, e subida de 7,9% em 800 fF.

---

## 1 · Tentei a previsão de primeiros princípios pedida. Ela FALHOU na validação.

Com `Ctot` medido (129,71 fF), `V` de disparo medido (0,5512 V), excursão de `out` medida
(1,6243 V) e a curva de fuga medida por DC, montei:

`T = Ctot · ∫[V_min → V_disparo] dV/(Iin − fuga(V))`, com
`Ctot(Cmem) = Cmem + 29,71 fF` e `V_min(Cmem) = 0,1224 − 1,6243·Cfb/Ctot`.

**O modelo acerta a janela e erra a frequência:**

| grandeza em `Cmem` = 100 fF | previsto | medido | erro |
|---|---|---|---|
| janela | 0,6793 V | 0,6792 V | **+0,01%** |
| frequência | 114,61 Hz | 139,58 Hz | **−17,9%** |

**Por que:** o modelo integra a janela inteira, mas a rampa percorre só **0,5492 V** dos
0,6792 V. O ponto de partida da rampa é **+0,002 V** — praticamente o terra. **O undershoot de
−0,128 V não é integrado por `Iin`.** É um transiente do próprio disparo, e a curva de fuga
medida por DC, mesmo extrapolada, não o atravessa rápido o bastante para reproduzir o
observado.

**Registro isto como falha antes de rodar, não depois.** Foi a previsão mais forte que este
projeto podia tentar, e ela não passou na própria validação.

## 2 · Restam dois modelos, ambos calibrados, com previsões irreconciliáveis

**Modelo A — "a rampa parte do zero".** Corrige a falha acima fixando o início da rampa em
`V` ≈ 0: `T = Ctot · V_disparo/(Iin − fuga)`, logo **f ∝ 1/Ctot**.

**Modelo B — "a forma do nível 1 se repete".** O mecanismo do achado é o divisor capacitivo
`Cfb`/`Ctot`, que é **topológico**, não depende de modelo de dispositivo. O mesmo argumento
fez o ganho f–I reproduzir dentro de 0,7% na migração. Previsão: a forma normalizada se repete.

| `Cmem` | `Ctot` | **Modelo A** | **Modelo B** |
|---|---|---|---|
| 25 fF | 54,7 fF | **329,8 Hz** | **159,3 Hz** |
| 50 fF | 79,7 fF | 226,3 Hz | 151,2 Hz |
| 100 fF | 129,7 fF | 139,1 Hz | 139,6 Hz |
| 200 fF | 229,7 fF | 78,5 Hz | 126,5 Hz |
| 400 fF | 429,7 fF | 42,0 Hz | 121,8 Hz |
| 800 fF | 829,7 fF | **21,7 Hz** | **131,4 Hz** |

| | Modelo A | Modelo B |
|---|---|---|
| erro no ponto de calibração (100 fF) | **−0,36%** | +0,01% (por construção) |
| queda de 25 a 400 fF | **87%** | **23,5%** |
| 800 fF sobe? | não, cai para 0,52× | sim, 1,079× |

**Os dois não podem estar certos.** O Modelo A valida em 100 fF com 0,36% e destrói o achado
central; o Modelo B preserva o achado e é uma extrapolação de forma, não uma derivação.
**A varredura discrimina entre eles**, e é isso que a torna decisiva em vez de confirmatória.

## 3 · A previsão em que aposto

> **Aposto no Modelo B: o achado sobrevive.** Espero cada ponto **dentro de ±15%** dos valores
> da coluna B, a queda de 25 a 400 fF entre **15% e 35%**, e **nenhuma variação acima de 2×**
> ao longo dos 32× de `Cmem`.

Razão: o cancelamento é geométrico. `Cmem` aparece no numerador (a carga a mover) e no
denominador (a altura do degrau de `Cfb`) da mesma forma, e isso não depende de `V_th`, de
mobilidade ou de condução sub-limiar. Foi o que sustentou a f–I na migração, e é o mesmo
mecanismo.

**Se o Modelo A vencer**, o achado central do projeto **não sobrevive ao PDK** — e essa seria
a descoberta mais importante desde a etapa 0, porque inverteria a decisão de manter `Cmem`
pequeno registrada no `CLAUDE.md` §6.

## 4 · O ponto de 800 fF

Hipótese registrada: a subida de 7,9% em 800 fF vem de **mudança de regime quando a excursão
cai abaixo de ~0,2 V**.

> **Previsão: o 800 fF sobe também no sky130.** Se subir, a hipótese ganha confirmação em
> **dois modelos de dispositivo independentes** — nível 1 e BSIM4 do sky130 — e passa de
> especulação a achado reprodutível. Se não subir, a subida do nível 1 era artefato daquele
> modelo.

Previsão da excursão em 800 fF: **0,15 a 0,25 V**, contra 0,107 V medidos no nível 1.

## 5 · O que mais espero medir

- **`Ctot` pela rampa, com o desconto da fuga** (`CLAUDE.md` §7): deve dar `Cmem` + 29,7 fF em
  cada ponto, dentro de 2%. É o teste do parasita de 9,71 fF como constante do circuito.
- **CV do ISI** abaixo de 0,05% em todos os pontos.
- **Janela**: deve encolher com `Cmem`, de ~1,0 V em 25 fF a ~0,47 V em 800 fF.

## 6 · Critério de fechamento da etapa 1

Este é o **último** critério de saída em aberto. Se a varredura reproduzir o comportamento do
nível 1 dentro das margens acima, **a etapa 1 fecha** e o `CLAUDE.md` §2 deve dizê-lo.
Se o Modelo A vencer, a etapa 1 **não** fecha: o achado central precisaria ser reescrito antes.
