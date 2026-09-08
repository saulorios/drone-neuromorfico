# Drone Neuromórfico — contexto do projeto

> Este arquivo é a memória do projeto. Está estruturado conforme a Parte 9.3 do
> dossiê (`docs/dossie_v1.0.pdf`). Atualize-o ao fim de cada etapa.
> Última atualização: 2026-09-07.
>
> **Estado do dossiê v1.0.** Ele é preservado como registro do que se acreditava em
> setembro de 2026 — metade do valor deste projeto está em poder comparar o que se
> pensava com o que se mediu. Mas duas de suas partes já não valem:
>
> | Parte do dossiê v1.0 | Estado |
> |---|---|
> | **Parte 7** (plano de etapas) | **SUBSTITUÍDA** por [`docs/etapas.md`](docs/etapas.md) |
> | **Parte 4** (resultados da simulação) | **SUPERADA** por `resultados/` e pela §4 deste arquivo |
> | Partes 1, 2, 3, 5 e 6 | **continuam válidas** |

---

## 1 · Objetivo

Construir um drone com percepção e aprendizado em hardware neuromórfico — circuitos
que processam informação por pulsos espaçados no tempo, não por instruções. A
aplicação-alvo é detecção de eventos em busca e resgate: voar por horas com consumo
muito baixo e sinalizar quando algo se destaca do padrão de fundo do ambiente.

O nicho é estreito de propósito: **detecção de eventos em tempo contínuo com consumo
desprezível**. Não é reconhecimento de objetos, identificação de pessoas nem
compreensão de cena — nessas tarefas uma GPU comum é largamente superior.

---

## 2 · Estado atual

| Etapa | Descrição | Situação |
|---|---|---|
| 0 | Neurônio axon-hillock em ngspice, modelos nível 1 | **Concluída e revalidada.** Ressalvas numéricas fechadas (§5); **consumo resolvido** em 2026-09-06 (12,6 µW → 83,5 nW) e topologia confirmada. Pendências não bloqueantes em §5-A |
| 1 | Migrar para PDK SkyWater 130 nm | **CONCLUÍDA em 2026-09-07.** Os seis critérios de saída fechados: armadilha do W/L, neurônio migrado, fuga em `mem` medida, janela de histerese medida, fator 1,76× resolvido (é 1,99× no PDK), e varredura de `Cmem`. Consumo **14× menor** (6,03 nW, 43,2 pJ/disparo), f–I linear com R² = 0,999996 e ganho a 0,7% do nível 1, pulso aprovado no critério funcional. **⚠️ Fecha invertendo o achado central: `Cmem` CONTROLA a frequência no PDK** (§3). |
| 2 | Monte Carlo (descasamento) | Não iniciada — maior risco do projeto |
| 3–10 | Cantos, par acoplado, coincidência, AER/FPGA, layout, tapeout | Não iniciadas |

Nenhum hardware foi construído. Todo número neste repositório vem de simulação ou de
literatura, e a origem está sempre indicada.

**Ambiente desta máquina (verificado em 2026-09-06):** Ubuntu 24.04. **ngspice NÃO está
instalado**; `numpy` e `matplotlib` **não estão instalados** no Python padrão
(`~/miniconda3/bin/python3`); nenhum PDK presente. Disco: 20 GB livres de 468 GB (96%
ocupado) — restrição real para instalar o sky130. Os scripts em `scripts/` **não foram
executados nesta máquina**; foram herdados da etapa 0, rodada em outro ambiente. A
revalidação de 2026-09-06 também foi executada fora deste ambiente — os números da §4 vêm
de `resultados/2026-09-06_revalidacao_etapa0/revalidacao.md`, não de execução local.

---

## 3 · Resultado central da etapa 0

**O capacitor de membrana não controla a frequência de disparo.**

Modelo analítico de primeira ordem que explica o achado (derivado, não medido):

- O degrau de realimentação desloca a membrana em `ΔV = VDD · Cfb / Ctot`, onde
  `Ctot = Cmem + Cfb + parasitas de gate`.
- A rampa de integração sobe a `dV/dt = Iin / Ctot`.
- Logo o período de integração é `T = Ctot · ΔV / Iin = Cfb · VDD / Iin`.

> ⚠️ **REVOGADO em 2026-09-07 pela medida no PDK.** O que segue nesta caixa era a
> formulação do nível 1 e **não sobrevive ao sky130**. Mantido riscado porque o motivo da
> revogação vale mais que a revogação.
>
> ~~`Cmem` é um controle fraco, com resíduo medido de 24% em 16×. O cancelamento é real e
> dominante — a intuição ingênua `f ∝ 1/Cmem` previria 1600% — mas não é exato. Medido na
> revalidação: 183,1 Hz em 25 fF → 140,0 Hz em 400 fF.~~

**A formulação medida no sky130** (`resultados/2026-09-07_cmem_sky130/`):

**No regime integra-e-dispara, `Cmem` É o controle dominante da frequência.**
`f ≈ k/Ctot`, com `Ctot = Cmem + 29,71 fF` medido. Medido: **290,3 Hz em 25 fF → 85,6 Hz em
200 fF**, isto é, **3,39× sobre 8× de `Cmem`** — contra 1,26× do nível 1 no mesmo intervalo.
O produto `f·Ctot` varia 21,4%: o modelo é aproximado, mas 16× mais estável que `f` sozinha.

**Existem dois regimes, e a fronteira é a excursão da membrana em ~0,2 V:**

| | `Cmem` ≤ 200 fF — integra-e-dispara | `Cmem` ≥ 400 fF — degenerado |
|---|---|---|
| excursão | 0,58 a 1,02 V | 0,061 a 0,19 V |
| CV do ISI | 0,0005 a 0,0050% | **0,129 a 0,223%** — salto de 26× |
| pulso de `out` | 1,01 a 1,80 V | 0,72 a 0,82 V, sem excursão lógica |
| f com `Cmem` | **cai** | **sobe** |

**O MECANISMO DA INVERSÃO — por que o cancelamento evaporou.** O cancelamento exigia que a
janela de histerese fosse `VDD·Cfb/Ctot`, isto é, que ela **encolhesse na mesma proporção em
que `Ctot` cresce**. Só assim `T = Ctot·ΔV/Iin` fica independente de `Cmem`.

A janela medida diz que não é isso:

| parcela da janela em `Cmem` = 100 fF | valor | encolhe com `Ctot`? |
|---|---|---|
| divisor capacitivo `VDD·Cfb/Ctot` | 0,278 V (**41%**) | **sim** |
| distância entre limiar de comutação e fundo do undershoot | 0,402 V (**59%**) | **não** — são tensões absolutas |
| **janela medida** | **0,679 V** | fator **2,45×** sobre o divisor |

**O chute capacitivo é minoria.** A maior parte da janela é a distância entre duas tensões
**absolutas** — o limiar de comutação do primeiro inversor e o fundo do undershoot — e
nenhuma das duas encolhe quando `Ctot` cresce. Por isso o cancelamento não se sustenta.

**E por isso ele dependia do modelo:** no nível 1 o `V_th` menor deixava o termo do divisor
dominar a janela, e o cancelamento aparecia. No sky130, com `V_th` maior, o termo absoluto
domina e o cancelamento evapora.

**Quantificando, com denominador.** Ajustando `f ∝ Ctot^-x` no mesmo intervalo (`Cmem` de 25 a
200 fF, `Ctot` de 54,71 a 229,71 fF) nos dois modelos:

| | expoente `x` | cancelamento restante |
|---|---|---|
| nível 1 | **0,16** | **84%** |
| **sky130** | **0,85** | **15%** |
| integrador sem cancelamento algum | 1,00 | 0% |

**Sobrava 84% de cancelamento; sobram 15%.**

**Nota de método:** a previsão de que o cancelamento seria geométrico e portanto independente
do modelo era razoável — **e a medida da janela já a contradizia uma rodada antes**. O fator
2,45× entre janela medida e divisor estava registrado em
`resultados/2026-09-07_histerese/` e eu não tirei a consequência dele. O dado que refutava a
hipótese já estava na mesa.

**Por que o nível 1 dizia o contrário:** ele mantinha a excursão grande com `Cmem` grande
(0,107 V em 800 fF contra 0,061 V no sky130), sustentando a compensação. No PDK a excursão
colapsa antes e o circuito sai do regime.

**A subida em 800 fF está confirmada em dois modelos de dispositivo independentes** —
nível 1 (×1,079) e BSIM4 do sky130 (×1,742), que não compartilham equações. A hipótese de
mudança de regime deixa de ser especulação.

**O modelo acima é incompleto por um motivo identificado:** ele supõe reset completo e
auto-terminado. O reset real é incompleto — a membrana para em 0,406 V, não em zero — e
por isso `Mrst` também fixa a frequência (ver §4 e §5 item 4).

**Consequência de projeto — a decisão SOBREVIVE, com motivo novo e mais forte.** `Cmem`
deve ser **pequeno**. Não mais porque "não compra lentidão": ele compra. E sim porque `Cmem`
grande **empurra o circuito para fora do regime de integra-e-dispara** — o jitter piora 26×,
o pulso perde excursão lógica e a frequência inverte de sentido.

**E há um ganho que o projeto não sabia que tinha:** `Cmem` é um **parâmetro de projeto
utilizável** para fixar a frequência. Antes só havia um botão, `Iin`. Agora há dois, e são
independentes.

**O impacto na área — SEGUNDA correção.** A §4.3 do dossiê dizia que o capacitor não
dominaria a área porque `Cmem` podia encolher livremente. Isso já havia sido corrigido uma vez
em 2026-09-06, para "`Cfb` fixa a frequência e não pode encolher". **Agora `Cmem` também
fixa.** Encolher **qualquer um dos dois** muda a frequência:

| | fixa a frequência? | pode encolher livremente? |
|---|---|---|
| `Cfb` | sim (define o degrau de realimentação) | **não** |
| `Cmem` | sim, `f ∝ Ctot^-0,85` | **não** |

**Não há economia de área livre em capacitor neste circuito.** Os dois são compromissos
acoplados com a frequência. O que sobra é escolher o ponto de operação sabendo o preço, não
encolher de graça.

**Impacto na área do chip:** `Cmem` pode encolher, mas **quem fixa a frequência é `Cfb`, e
`Cfb` não pode encolher sem alterar o ganho f–I**. A área do neurônio continua dominada por
um capacitor — o outro. A economia é menor do que a formulação anterior ("o neurônio pode
ser mais compacto que o previsto") sugeria. Corrigido em 2026-09-06.

**Consequência ainda não explorada:** como `T ∝ VDD`, a frequência depende da alimentação
por construção. Isso explica quantitativamente o painel 6 (ver §5) e indica que a
compensação de VDD é um problema de topologia, não de ajuste fino.

---

## 4 · Números da etapa 0 (com unidade e denominador)

**Fonte: `resultados/2026-09-06_revalidacao_etapa0/revalidacao.md`** (ngspice 42, modelos
nível 1 inalterados, netlist com o bloco `.options` — circuito não modificado). Os valores
anteriores a 2026-09-06 foram produzidos com tolerâncias padrão e **estão descartados**,
não corrigidos: ver §5.

Todos com modelos nível 1, `Cmem = 100 fF`, `Cfb = 20 fF`, `VDD = 1,8 V`, `Wrst = 0,5 µm`,
T = 27 °C nominal.

| Grandeza | Valor | Denominador / condição |
|---|---|---|
| Frequência de disparo | **160,3 Hz** | com `Iin` = 10 pA; convergido — invariante de `tstep` de 5 µs a 0,5 µs |
| CV do ISI (jitter) | 0,010% | desvio padrão do ISI sobre o ISI médio, dentro de uma corrida |
| Ganho f–I | **16,0 Hz/pA** | ajuste sobre 12 pontos, `Iin` de 1 a 100 pA |
| Faixa de frequência | 15,3 Hz a 1,604 kHz | extremos medidos em `Iin` = 1 pA e 100 pA |
| Zona morta em corrente baixa | nenhuma detectável | reta pela origem; menor corrente testada = 1 pA |
| Potência por neurônio | **12,6 µW** | no ponto nominal; = 6,97 µA médios × 1,8 V |
| Razão potência/sinal | **7 × 10⁵** | denominador = potência do sinal de entrada, 1,8 V × 10 pA = 18 pW |
| Energia por disparo | **78 nJ** | = 12,6 µW ÷ 160,3 Hz. Neurônios neuromórficos publicados: 1–100 pJ, ~10⁶× abaixo |
| Dependência do consumo com `Iin` | **nenhuma** | 12,6 a 12,8 µW para `Iin` de 10 a 100 pA (16,3 µW em 1 pA). É um piso fixo, não consumo de sinal |
| Excursão da membrana | 1,43 V → 0,107 V | `Cmem` de 25 fF a 800 fF (32×), `Iin` = 10 pA |
| Variação de f com `Cmem` | 24% | denominador = f em `Cmem` = 25 fF (183,1 Hz); `Cmem` variado 16× (25→400 fF) |
| Variação de f com `Wrst` | 2,3× | `Wrst` variado 32× (0,25 → 8 µm). **`Mrst` fixa a frequência** |
| Deriva com alimentação | 18% pico-a-pico | ⚠️ **não revalidado** — número de tolerância padrão, tratar como descartado até refazer |

**Com fome de corrente assimétrica no PMOS dos dois estágios** (fonte: `resultados/2026-09-06_espelho/espelho.md`, ngspice 42). Denominador comum: `IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA, demais parâmetros no nominal acima.

| Grandeza | Valor | Denominador / condição |
|---|---|---|
| Potência por neurônio | **83,5 nW** | soma dos dois estágios; **exclui o ramo de referência do espelho**, que é compartilhado entre neurônios num chip real |
| Energia por disparo | **0,60 nJ** | = 83,5 nW ÷ 138,3 Hz. Era 78 nJ na linha de base |
| Frequência de disparo | **138,3 Hz** | contra 160,3 Hz da linha de base: desvio de 14% |
| Redução de potência | 151× | denominador = linha de base revalidada, 12,6 µW |
| CV do ISI | 0,0050% | dentro de uma corrida |
| Pulso de saída | 92,2% de VDD | critério: ≥ 90% |

**Com o PDK sky130** (canto `tt`, `.temp 27`, mesmas dimensões; fonte: `resultados/2026-09-07_migracao_sky130/migracao_sky130.md`). Mesmo denominador: `IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA.

| Grandeza | Valor | Denominador / condição |
|---|---|---|
| Potência por neurônio | **6,03 nW** | soma dos dois estágios, sobre ciclos inteiros; **exclui o ramo de referência** do espelho. Era 85,4 nW em nível 1 — **14× menor** |
| Energia por disparo | **43,2 pJ** | = 6,03 nW ÷ 139,58 Hz. **Dentro da faixa publicada de 1 a 100 pJ** para neurônios neuromórficos — o projeto entra na faixa da literatura pela primeira vez. Era 0,60 nJ em nível 1 |
| Potência na faixa 1–100 pA | 4,30 a 13,67 nW | nunca cruza o orçamento de 100 nW |
| Frequência de disparo | 139,58 Hz | +0,9% sobre o nível 1 |
| Ganho f–I | 13,886 Hz/pA | +0,7% sobre o nível 1; R² = 0,99999597 |
| Fuga no nó `mem` | **25,3 fA** | inferida da curva f–I em operação, a 27 °C. O transistor isolado em `Vds` = 1,8 V dá 84,7 fA — 3,3× acima, por ser condição mais severa |

**Curva f–I nesse mesmo ponto** (fonte: `resultados/2026-09-07_fi_espelho/fi_espelho.md`,
ngspice 42, 12 pontos de 1 a 100 pA).

| Grandeza | Valor | Denominador / condição |
|---|---|---|
| Ganho f–I | **13,79 Hz/pA** | ajuste de intercepto livre, 12 pontos, `Iin` de 1 a 100 pA. Linha de base: 16,0 |
| R² | **0,99999917** | ajuste linear; expoente log–log = 1,0005 |
| Zona morta | **nenhuma** | intercepto de +0,31 Hz → −22,8 fA, 44× abaixo do menor ponto medido |
| Resíduo máximo | 2,73% | no ponto de 1 pA; os outros 11 dentro de ±1,17% |
| Deriva de f/`Iin` | **0,7%** | ao longo de dois decades. Linha de base: 5% — a linearidade **melhorou** |
| Potência no ponto nominal | **85,4 nW** | medida sobre ciclos inteiros; era 87,5 nW com janela bruta |
| **Faixa de validade do orçamento** | **`Iin` de 1 a 50 pA → f de 14 a 690 Hz** | decidido em 2026-09-07 (§6). Nessa faixa a potência vai de 80,5 a 99,1 nW e o orçamento de 100 nW é respeitado em todos os pontos |
| Potência acima da faixa | 104,2 nW em 70 pA; 112,4 nW em 100 pA | ⚠️ **fora de validade** — o orçamento cruza os 100 nW em `Iin` ≈ 54 pA (f ≈ 745 Hz) |
| Ramo de referência do espelho | **5,42 µW** | ⚠️ fora do orçamento por neurônio; exige **N ≥ 370 neurônios** para amortizar dentro de 100 nW |

---

## 5 · Estado das ressalvas da etapa 0 — resolvidas em 2026-09-06

Levantadas ao aplicar a Regra 1 sobre os resultados originais; **fechadas** pela
revalidação em `resultados/2026-09-06_revalidacao_etapa0/revalidacao.md`. Mantidas aqui
com o veredito, porque o motivo do descarte vale mais que o descarte.

1. **RESOLVIDA — era ruído numérico.** O espalhamento de ~10% entre corridas (158 / ≈175 /
   ≈166 Hz para o mesmo circuito) não era física. Com tolerâncias corrigidas a frequência
   converge para **160,3 Hz**, invariante de `tstep` de 5 µs a 0,5 µs. O jitter *dentro* de
   cada corrida era pior que o espalhamento entre elas: **CV do ISI de 20%** num circuito
   determinístico, onde o valor correto é 0,01% — fator 2000.

2. **RESOLVIDA — a estrutura do painel 4 era ruído, mas o resíduo de 24% é real.** Com
   tolerâncias corrigidas a varredura de `Cmem` fica limpa (CV do ISI ~0,03%). O achado
   sobrevive: 16× de capacitor produz 24% de variação, contra os 1600% da intuição ingênua.
   Mas não é o cancelamento exato que a §3 afirmava — ver a reformulação lá.
   ✅ **A subida em 800 fF está EXPLICADA e CONFIRMADA (2026-09-07).** Ela existe nos dois
   modelos de dispositivo: ×1,079 no nível 1 e **×1,742 no sky130** — modelos que não
   compartilham equações. **Causa: mudança de regime.** Quando a excursão da membrana cai
   abaixo de ~0,2 V o circuito deixa de ser integra-e-dispara e vira oscilador de pequeno
   sinal; o CV do ISI salta 26× e a frequência inverte de sentido. A hipótese registrada
   estava certa, e agora tem confirmação independente.

3. **RESOLVIDA — a curva é linear e passa pela origem.** A razão f/`Iin` fica entre 15,3 e
   16,04 Hz/pA ao longo de toda a faixa de 1 a 100 pA. Um ajuste de intercepto livre sobre
   os 12 pontos dá `f = 16,05·Iin − 1,21 Hz`, isto é, uma zona morta implícita de ~75 fA —
   treze vezes abaixo da menor corrente testada, portanto **não detectável**. A curvatura
   aparente no original era o ruído do item 1.
   ⚠️ Continua valendo o defeito de método: `scripts/plots.py` imprime a string literal
   `(linear, R² alto)` sem calcular R² algum. **Não corrigido no código.**

4. **RESOLVIDA, com a minha hipótese REFUTADA.** O fator 1,76× do modelo analítico existe,
   mas **a causa não é overshoot da saída acima de VDD**, como eu havia suposto. É **reset
   incompleto**: `Mrst` é fraco e a membrana para em **0,406 V**, não em zero. Onde ela
   para depende da força de `Mrst` e da largura do pulso — daí `Wrst` variado 32× mover a
   frequência 2,3× (189,4 Hz em 0,25 µm → 81,4 Hz em 8 µm). `T = Cfb·VDD/Iin` só valeria
   com reset completo e auto-terminado.
   **Consequência para a etapa 2:** existe um caminho direto de descasamento de `Mrst` para
   dispersão de frequência entre neurônios, que **não está no mapa de riscos do dossiê §8**.
   `Mrst` passa a ser um dispositivo crítico de casamento, ao lado de `Cfb`.
   **FECHADA em 2026-09-07 — a janela foi MEDIDA** (`resultados/2026-09-07_histerese/`), com
   `Ctot` medido pela inclinação da rampa e não suposto: janela de **0,6792 V** contra os
   0,2759 V do modelo `VDD·Cfb/Ctot` — **fator 2,46×**; contra 0,2489 V usando a excursão real
   de `out`, **2,73×**. Em período, **1,99×** no sky130 contra 1,76× no nível 1. O fator
   sobrevive ao PDK e é maior.
   **E a razão entre os dois números está explicada:** a rampa percorre só **0,5490 V** dos
   0,6792 V da janela. A diferença, 0,1303 V, **é o undershoot** (0,128 V medido) — trecho que
   não é integrado por `Iin`, e sim atravessado depressa pela injeção de junção do item 15.

5. **CONFIRMADA — era `abstol`, e também `trtol`.** A hipótese está validada: as tolerâncias
   padrão do ngspice invalidavam os três itens acima de uma vez. `trtol` (padrão 7) pesa
   tanto quanto `abstol` — relaxa o controle de erro de truncamento local e deixa o
   integrador dar passos grandes demais. Virou regra permanente do projeto: ver §7.

6. **Limitações do dossiê §4.4 permanecem** (sem modelo sub-limiar, sem variação de
   fabricação, sem parasitas de layout). A #1 é o objeto da etapa 1.

---

### Observação de leitura — o que os 85,4 nW significam, e o que não significam

**O neurônio continua dominado por consumo estático.** Dos 85,4 nW do ponto nominal,
**~80,9 nW são piso estático** e apenas **~4,5 nW acompanham a atividade** — 5,2% do total.
O ajuste na faixa útil dá `P = 0,406·Iin + 80,9 nW`, com `Iin` em pA. Em 1 pA, a menor
corrente medida, o neurônio já consome 94% do que consome no ponto nominal.

**Consequência para a leitura do dossiê.** A Parte 1 afirma que um sistema baseado em
eventos "não gasta energia quando nada acontece". Essa afirmação **segue qualitativamente
falsa** para este circuito, agora num patamar 150× menor. O que mudou foi a magnitude, não
o mecanismo: o neurônio não é um dispositivo orientado a evento, é um dispositivo de piso
estático com uma pequena modulação por atividade.

**Passa em números absolutos; não passa como descrição do mecanismo.** O argumento de
consumo do projeto deve ser reescrito em termos de "piso estático baixo o bastante", não de
"consumo proporcional à atividade" — são justificativas diferentes, com implicações
diferentes para a arquitetura. Um chip com N neurônios ociosos gasta `N × 80,9 nW`, e isso
escala com a contagem de neurônios, não com a taxa de eventos.

---

### Ressalva ABERTA — a tesoura: o teto caiu, o piso térmico continua

**Atualizada em 2026-09-07 com a fuga medida em operação.** Isto é ressalva, não conclusão.

**O teto de consumo DESAPARECEU.** Ele vinha de a potência cruzar 100 nW em `Iin` ≈ 54 pA,
medido em nível 1. No sky130 a potência fica entre 4,30 e 13,67 nW em toda a faixa de 1 a
100 pA e não cruza o orçamento em ponto algum. A faixa útil foi restaurada (§6).

**O piso térmico continua, e a base foi MEDIDA em 2026-09-07** (`resultados/2026-09-07_fuga_mem/`).
Os 25,3 fA que se usava antes eram **inferidos** da curva f–I e **estão revogados** — ver §5-A
item 14. A fuga medida por ponto de operação DC **não é um número**: vale **0 em `mem` = 0**,
sobe a um patamar de **55,4 a 62,1 fA** acima de 100 mV (variação de só 1,12×), e **muda de
sinal** abaixo de zero, virando **injeção** de até **+3,7 pA em `mem` = −0,127 V**.

Projetando pelo patamar, **56 fA** (duplicação a cada 8–10 °C):

| a fuga alcança | com 56 fA medidos | *(com os 25,3 fA revogados)* |
|---|---|---|
| 1 pA — o extremo **inferior** da faixa | **60 a 69 °C** | *(69 a 80 °C)* |
| 10 pA — o ponto nominal | **87 a 102 °C** | *(96 a 113 °C)* |
| 100 pA — o extremo **superior** | **113 a 135 °C** | *(123 a 146 °C)* |

⚠️ **Esta projeção é conservadora mas não é fiel.** Ela usa só o patamar e ignora que a
injeção abaixo de zero **também cresce com a temperatura**, e mais rápido, por ser condução
direta de junção. Os dois termos crescem juntos e em sentidos opostos. **A projeção correta
exige medir a curva inteira em temperatura, não escalar um número** — etapa 3.

**O canto quente deixou de ameaçar a faixa inteira e passou a cortar só o extremo inferior.**
Com 84,7 fA a projeção dizia que a fuga engolia toda a faixa antes dos 120 °C; com 25,3 fA,
o extremo superior sobrevive além de 120 °C e o que se perde é a sensibilidade a correntes
pequenas — o neurônio deixa de responder a 1 pA por volta de 70–80 °C, mas continua
funcionando com estímulos maiores.

**Continua sendo extrapolação, não medida.** Regra de bolso aplicada a um ponto de 27 °C.
O PDK tem os modelos de temperatura e responde direto — etapa 3. **E a pergunta da faixa
térmica real continua pendente** (§5-A item 13): sem ela, não há como dizer se 69–80 °C é
um problema ou uma margem confortável.

---

## 5-A · Ressalvas ABERTAS

**O bloqueio de consumo está resolvido.** A ressalva que dizia "o consumo inviabiliza a
topologia" foi fechada em 2026-09-06: 12,6 µW → **83,5 nW** com fome de corrente assimétrica
no PMOS dos dois estágios. A topologia axon-hillock fica (§6). O que segue aberto:

### Do experimento do espelho (`resultados/2026-09-06_espelho/espelho.md`)

1. ~~A curva f–I não foi refeita no ponto novo.~~ **FECHADA em 2026-09-07:** sobrevive.
   R² = 0,99999917, expoente log–log 1,0005, sem zona morta, resíduo máximo 2,73%.
2. ~~Sem estudo de convergência nesse ponto.~~ **FECHADA em 2026-09-07:** f invariante em
   0,002% sobre 16× de `tstep`. O `.nodeset` é de fato obrigatório e virou convenção (§7).
3. **As dimensões do espelho em nA são fictícias no nível 1.** W/L = 0,05 entrega 10 nA no
   modelo com Vov ≈ 0,09 V, mas 90 mV de sobretensão é inversão moderada, que o nível 1
   trata como lei quadrática — errado. O **comportamento** de limitador está correto; o
   **dimensionamento** do circuito de polarização só pode ser projetado com o PDK.
4. **A margem de 1,2× é estreita e o ponto ótimo é uma ilha.** `IB2` = 1 µA reprova no pulso
   (83,1% de VDD), `IB2` = 3 µA aprova (92,2%). A vizinhança entre 1 e 3 µA não foi mapeada.
5. **Nível 1, sem sub-limiar, sem descasamento, sem parasitas** — como sempre.
6. **DIFERIDA para depois da migração — ramo de referência do espelho.** Custa **5,42 µW**
   medidos, 63× o consumo do neurônio, exigindo **N ≥ 370** neurônios para amortizar dentro
   de 100 nW.
   **Causa identificada:** o espelho é **1:1**, razão que tive de assumir porque o relatório
   do espelho não a especificou. É omissão da documentação, não escolha de projeto.
   **Direção da solução, não simulada:** espelho **com razão** — referência em 100 nA e
   dispositivo de saída ~30× mais largo, entregando os mesmos 3 µA ao 2º estágio. O ramo cai
   para **198 nW** (= (10 nA + 100 nA) × 1,8 V) e o requisito desaba de 370 para **N ≥ 14**
   neurônios (198 nW ÷ 14,6 nW de folga por neurônio).
   *Correção de 2026-09-07:* a primeira estimativa dizia 216 nW e N ≈ 15. Vinha de contar um
   espelho de NMOS que a variante assimétrica eliminou — a fome é só no PMOS. Erro do autor
   do projeto, corrigido aqui.
   **Por que fica diferida:** dimensionar um espelho com razão em regime de nA é projeto de
   polarização que o nível 1 não modela — é o mesmo motivo da pendência 3. Só faz sentido
   depois da etapa 1. **Não simular antes do PDK.**
7. **O orçamento de 100 nW não vale em toda a faixa útil.** A potência cresce com `Iin` e
   cruza os 100 nW em ≈ 54 pA (f ≈ 745 Hz), enquanto a faixa declarada vai a 100 pA. O
   critério foi enunciado no ponto nominal e lá passa; na faixa toda, não. Critério e faixa
   de operação são incompatíveis como estão — decisão pendente do autor.

### Herdadas

6. **A deriva de 18% com VDD não foi revalidada.** É número de tolerância padrão; pela lição
   do item 1 da §5, deve ser tratado como descartado, não como aproximado. E foi medido na
   topologia sem fome de corrente — provavelmente não vale mais.
7. **O CV de 5,8% em 4 dos 12 pontos da varredura de `Iin`** (revalidação) não foi
   investigado. Suspeita: artefato do detector de disparo, não do circuito.
8. **O ponto de 800 fF da varredura de `Cmem`** (§5 item 2) não está explicado.
9. **Divergência de 11% na potência da linha de base entre ngspice 41 e 42**, não separada.
   Ver a convenção de registrar versão em §7.

10. **O pulso de saída reprova no sky130: 88,84% contra o mínimo de 90%**, em toda a faixa
    útil (passa só em 70 e 100 pA). Causa identificada e não corrigida: o nível baixo de `n1`
    subiu de 0,051 para 0,591 V porque `M1n` opera em inversão fraca no sky130, e com `n1`
    parando aí o `M2n` continua parcialmente ligado, prendendo `out` num divisor. As correções
    óbvias mexem em dimensão ou polarização e não foram tentadas.

11. **A faixa útil de 1 a 50 pA pode ser reaberta.** O teto de 54 pA (§6, 2026-09-07) **era
    artefato dos modelos nível 1**. No sky130 a potência em 100 pA é 13,67 nW, 7,3× abaixo do
    orçamento, e não cruza os 100 nW em ponto algum. Decisão do autor — não alterei o §6.

12. **A tesoura (§5) perdeu o teto, mas não o piso.** O limite de consumo desapareceu. A fuga
    térmica continua, e agora com base melhor: **25,3 fA em operação** a 27 °C, inferidos da
    própria curva f–I, contra os 84,7 fA do transistor isolado em `Vds` = 1,8 V — 3,3× menor,
    como a ressalva do `Vds` previa. A projeção da tesoura precisa ser refeita com 25 fA, o
    que desloca os cruzamentos para temperatura mais alta. Não recalculada: depende da faixa
    térmica ainda indefinida (item 13).

14. **A curvatura da curva f–I em corrente baixa está SEM EXPLICAÇÃO, com DUAS hipóteses já
    derrubadas por medida direta.** O ponto de 1 pA fica 2,53% abaixo de uma reta proporcional.
    - **Hipótese 1, fuga — REFUTADA** (2026-09-07): sobre a excursão real a fuga produz
      **+1,62%**, para cima. A injeção de junção abaixo de `mem` = 0 mais que compensa a fuga
      acima, e o efeito líquido é uma *ajuda*.
    - **Hipótese 2, janela de histerese variável — REFUTADA** (2026-09-07): medida da forma de
      onda, a janela varia **−0,21%** em 1 pA contra os **+4,15%** necessários, e no **sentido
      oposto** — ela cresce com `Iin`, não com a lentidão.
    - **`Ctot` também está descartado:** parecia variar +5,70%, mas isso era a fuga disfarçada
      na medida `Ctot = Iin/(dV/dt)`. `Ctot` real é constante: **129,71 fF, espalhamento
      0,05%** sobre dois decades.
    Um modelo montado das três grandezas medidas (janela, `Ctot`, curva de fuga) reproduz a
    **frequência absoluta dentro de 3,4%** mas prevê a curvatura em **+1,62%** contra os
    **−2,53%** medidos — **erra o sinal**, por 4,15 pontos percentuais.
    **NÃO é ruído de ajuste — hipótese corrigida em 2026-09-07.** Os −2,53% não são resíduo de
    regressão: são a **razão entre duas frequências medidas diretamente**, cada uma com CV do
    ISI de ~0,005% e convergência de 0,000% sobre 16× de `tstep`. A incerteza da razão é da
    ordem de **0,01%**, e o efeito é **~250× isso**. Calcular a barra de erro do ajuste da f–I
    continua valendo como escrituração, mas **não dissolve este número**.

    **Status: ressalva ABERTA e NÃO BLOQUEANTE.** Não é critério de saída de etapa nenhuma. São
    2,5% no ponto extremo e menos usado da faixa (1 pA, f = 13,6 Hz). Não perseguir agora.

    **Palpite do Claude, não testado, registrado como palpite e não como direção de trabalho:**
    o período tem uma parte de **rampa** e uma de **disparo**. A de rampa escala com `Iin` por
    construção. A de disparo tem dois componentes: um que escala com `Iin` e outro **limitado
    pela taxa do espelho** (`IB1` = 10 nA fixa a velocidade de `n1` independentemente de
    `Iin`), que **não** escala. A competição entre os dois muda de peso ao longo da faixa e é
    candidata a produzir curvatura. **O teste é decompor o período** em rampa e disparo e medir
    cada parcela contra `Iin` — para quando isso voltar a importar.

15. **A junção de dreno do `Mrst` conduz DIRETO quando `mem` < 0**, injetando até **+3,7 pA**
    em −0,127 V — 37% de `Iin` no ponto nominal e **370%** em `Iin` = 1 pA.
    **Raiz, e não é para mexer:** `mem` só desce abaixo do terra porque o **degrau de descida
    de `out`** a puxa por `Cfb` depois que o reset termina. É a mesma física que produz o fator
    de ~1,8× entre o modelo `T = Cfb·VDD/Iin` e o período real — o acoplamento capacitivo da
    saída de volta à membrana é o mecanismo do circuito, não um defeito. **Não mexer.**
    A injeção se divide em dois riscos, de pesos muito diferentes:

15a. **Latch-up — risco BAIXO, vigiar em temperatura.** Os 3,7 pA estão ~9 ordens de grandeza
     abaixo da corrente necessária para acionar a estrutura tiristor parasita. Não é
     preocupação no estado atual. Reavaliar na etapa 3: a injeção é condução direta de junção
     e cresce com a temperatura mais rápido que a fuga sub-limiar.

15b. **Acoplamento por substrato entre neurônios vizinhos — risco ALTO.** E o motivo é
     específico deste projeto: **o sinal também é da ordem de pA**. `Iin` vai de 1 a 100 pA, e
     a injeção é de 3,7 pA. Diafonia de pA aqui não é ruído somado a um sinal grande — é
     **sinal inteiro** chegando ao vizinho errado. Num chip com centenas de neurônios
     replicados, cada disparo injeta no substrato compartilhado.
     **Mitigação: anel de guarda, etapa 8.** E isso **custa área**, o que amarra esta
     pendência a duas outras: à contagem de neurônios por chip (o ramo de referência do
     espelho já impõe N ≥ 14, item 6) e à etapa 2, onde a decisão entre transistores maiores
     e calibração individual já disputa a mesma área.
     **Não está no mapa de riscos do dossiê §8 e precisa entrar** — como risco de isolamento,
     não de consumo.

16. **A medida DC de fuga não cobre `mem` de 0,45 a 0,562 V.** O disparo DC ocorre em 0,45 V;
    em operação a membrana chega a 0,562 V porque o degrau de `Cfb` a empurra além. Esse
    trecho só existe dinamicamente e não foi caracterizado.

13. **PERGUNTA DE REQUISITO, EM ABERTO — qual é a faixa térmica real deste projeto?**
    Os −40 °C e 125 °C que a etapa 3 do dossiê usa **nunca foram justificados**. São a faixa
    automotiva, herdada por convenção, não derivada da aplicação. Um drone de busca e resgate
    com um chip abaixo de 1 mW dificilmente chega a 125 °C de junção.
    **Por que importa agora:** a tesoura (§5) diz que a faixa útil sobrevive a 27 °C e
    provavelmente não sobrevive a 125 °C. Se o requisito real for, digamos, −10 a 60 °C, o
    problema muda de natureza — deixa de ser bloqueante e vira margem. Se for mesmo 125 °C, o
    `Mrst` precisa ser reprojetado antes de qualquer outra coisa.
    **Não respondida aqui.** É decisão do autor do projeto e **pré-requisito da etapa 3** —
    definir os cantos antes de simulá-los, e não o contrário.

---

## 6 · Decisões tomadas — não reabrir sem motivo novo

| Data | Decisão | Motivo |
|---|---|---|
| 2026-09 | **Um chip homogêneo, replicado** — não chips especializados por modalidade | O gargalo real é a comunicação entre chips; a proporção entre modalidades é desconhecida e chips fixos a travam cedo demais; três máscaras custam três vezes mais. Mesma escolha de Loihi, SpiNNaker e Akida. Exceção legítima: a interface analógica de sensor é específica por modalidade e vai num chip pequeno separado. |
| 2026-09 | **Topologia axon-hillock** (Mead, 1989), 7 transistores — **CONFIRMADA em 2026-09-06 com fome de corrente assimétrica no PMOS de ambos os estágios: 83,5 nW por neurônio, 151× abaixo da linha de base** | Base histórica validada; simples o bastante para ser entendida por inteiro antes de complicar. O consumo de 12,6 µW, que chegou a ameaçar a escolha, é corrigível dentro da própria topologia — não exige trocá-la. Fonte: `resultados/2026-09-06_espelho/espelho.md`. |
| 2026-09-06 | **A fome de corrente é ASSIMÉTRICA: limita-se só o PMOS**, nunca os dois lados do inversor | A membrana opera entre 0,41 e 0,99 V, faixa em que M1p e M1n conduzem os dois sempre. O nível de `n1` é fixado pela **razão** entre as duas correntes. Grampear ambas ao mesmo IB destrói essa razão: nenhum lado vence, `n1` estaciona em ~0,83 V — dentro da janela de condução do 2º inversor — e o curto migra de estágio. Medido: fome simétrica dá 302 a 1 949 nW, **pior que as fontes ideais** (218 nW). A variante só-NMOS não dispara em 1 e 10 nA. |
| 2026-09-07 (c) | **`Cmem` pequeno — decisão MANTIDA, motivo REESCRITO** | A razão antiga ("`Cmem` não controla a frequência") **foi refutada no PDK**: ele controla, 3,39× sobre 8×. A razão nova é mais forte: acima de ~200 fF a excursão cai abaixo de 0,2 V e o circuito sai do regime integra-e-dispara — CV do ISI piora 26×, o pulso perde excursão lógica e a frequência inverte de sentido. **Limite de projeto: `Cmem` ≤ 200 fF.** E `Cmem` passa a ser um botão de frequência utilizável, ao lado de `Iin`. Medido em `resultados/2026-09-07_cmem_sky130/`. |
| 2026-09-07 (b) | **A faixa útil volta a `Iin` de 1 a 100 pA** — REVERTE a decisão da mesma data, abaixo | O teto de 50 pA vinha de a potência cruzar 100 nW em 54 pA, e **isso era artefato dos modelos nível 1**. No sky130 a potência fica entre 4,30 e 13,67 nW em toda a faixa de 1 a 100 pA — folga de **7,3×** contra o orçamento, sem cruzá-lo em ponto algum. Medido em `resultados/2026-09-07_migracao_sky130/`. A restrição de consumo desapareceu; a faixa volta a dois decades e o teto de frequência a 1,39 kHz. |
| ~~2026-09-07 (a)~~ | ~~**A faixa útil do neurônio é `Iin` de 1 a 50 pA (f de 14 a 690 Hz)**~~ — **REVERTIDA** no mesmo dia pela linha acima |
| 2026-09-06 | **O espelho do 2º estágio é largo (W = 5 µm, L = 1 µm)** | Um dispositivo estreito, de nA, rouba excursão do pulso de saída e o derruba para 81% de VDD, reprovando o critério de ≥ 90%. |
| 2026-09 | **Controle de voo não aprende** — software maduro existente (PX4 / ArduPilot) | Se a camada que estabiliza o drone aprender errado, o drone cai. Plasticidade só onde o erro custa um alarme falso. |
| 2026-09 | **Plasticidade modulada por surpresa** | Resolve dois problemas de uma vez: esquecimento catastrófico (quase nada é gravado) e correlações espúrias (ocorrem em momentos calmos, com plasticidade fechada). |
| 2026-09 | **`Cmem` pequeno** | Etapa 0, §3: `Cmem` não compra frequência e custa excursão de sinal. |
| 2026-09 | **Toda polarização que define constante de tempo, limiar ou corrente deve ser acessível externamente** | Se a corrente sair 40% menor que o simulado, compensa-se ajustando a polarização em vez de refabricar. |

---

## 7 · Convenções

**Nós do SPICE** (nomes fixos — não renomear sem atualizar os scripts):

| Nó | Significado |
|---|---|
| `mem` | tensão da membrana; nó de integração |
| `out` | saída do neurônio; o spike |
| `n1` | nó interno entre os dois inversores |
| `vdd` | alimentação |
| `0` | terra |

**Dispositivos:** `Cmem` (membrana), `Cfb` (realimentação), `Cload` (carga de saída),
`Iin` (corrente sináptica de entrada), `M1p/M1n` (1º inversor), `M2p/M2n` (2º inversor),
`Mrst` (reset).

**Tolerâncias numéricas — regra obrigatória.** Todo netlist deste projeto **DEVE** conter
o bloco `.options` de tolerância:

```spice
.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1
```

O `abstol` padrão do ngspice é **1e-12 A = 1 pA**, da mesma ordem do sinal deste circuito.
O `trtol` padrão é **7**, e relaxa o controle de erro de truncamento. Sem os dois
corrigidos, qualquer resultado numérico é inválido. **Resultado produzido sem esse bloco
deve ser descartado, não interpretado.** Confirmado experimentalmente em 2026-09-06:
tolerâncias padrão davam 20% de CV do ISI num circuito determinístico cujo valor correto é
0,01%, e três frequências diferentes para o mesmo circuito.

**Critério do pulso de saída — funcional, não fracionário.** O pulso **não** é julgado por
uma fração de VDD. A regra "≥ 90% de VDD" foi arbitrada sem base física e está **revogada**
em 2026-09-07. O que o pulso precisa fazer são três coisas, e cada uma é um teste:

1. **Chutar `Cfb`.** A carga injetada é `Cfb · ΔV(out)`, então o que importa é a **excursão**
   de `out`, não seu nível absoluto. Critério: a excursão precisa manter a janela de
   histerese da membrana acima do ruído e do descasamento.
2. **Abrir o gate do `Mrst`.** `out` no alto precisa levar `Mrst` a condução suficiente para
   completar o reset dentro do ciclo. Critério: o reset termina, verificável na forma de onda
   da membrana.
3. **Ser lido como nível alto pelo estágio seguinte.** `out` alto precisa ficar acima do
   ponto de transição do receptor com margem, e `out` baixo abaixo dele com margem — **e sem
   criar corrente estática apreciável no receptor**.

Um pulso que faz as três coisas está aprovado, tenha ele 88% ou 95% de VDD.

**Lição de método: critério pré-registrado não pode depender de parâmetro do modelo antigo.**
`VTO`, `V_th`, `KP` e tudo o que deles deriva mudam quando o modelo muda — que é justamente o
propósito da migração. Um critério ancorado neles testa o modelo velho, não o circuito.
Aconteceu **duas vezes** na migração de 2026-09-07:

| critério | por que quebrou |
|---|---|
| "pulso ≥ 90% de VDD" | a fração 90% foi arbitrada; o nível de `out` depende do `V_th` do receptor, que mudou |
| "`rp1`/`rp2` a menos de 300 mV do previsto" | a previsão usava `VTO` = 0,45 do nível 1; o pfet do sky130 tem `\|V_th\|` bem maior |

Nos dois casos o **circuito** estava certo e o **critério** estava errado. Ancore critérios em
grandezas funcionais — corrente entregue, transição completa, margem de ruído — ou em
grandezas medidas no modelo novo. Nunca numa constante do modelo velho.

**sky130: `W` e `L` são número puro em micrômetros.** Nos subcircuitos do `sky130_fd_pr`,
escreva `W=1 L=0.15`, **nunca** `W=1u L=0.15u`. A sintaxe com sufixo entrega 1e-06 ao
seletor de binning do BSIM4, que **aborta** com `could not find a valid modelname`.
Verificado em 2026-09-07: a falha é fatal e explícita, não silenciosa — não há risco de
resultado contaminado, mas o netlist não roda. Referência de sanidade:
`sky130_fd_pr__nfet_01v8` com `W=1 L=0.15` em Vgs = Vds = 1,8 V, canto `tt`, 27 °C, dá
**501,0 µA**.

**Não acrescentar `.option scale=1u` ao usar `.lib sky130.lib.spice`.** O `scale` está em
`libs.tech/ngspice/all.spice`, mas não na cadeia do `.lib` → `corners/tt.spice`. Com números
puros o resultado é idêntico com e sem ele (verificado: 501,05 µA nos dois casos). Pôr o
`scale` "por precaução" não ajuda e confunde quem ler o netlist depois.

**`.nodeset` obrigatório em netlist com espelho de corrente.** Com `uic`, o ngspice pula o
ponto de operação DC e parte de 0 V em todo nó fora do `.ic`. O nó de referência de um
espelho em 0 V põe o transistor diodo com Vsg = VDD, muito acima da corrente de projeto, e
a simulação **aborta**: `Timestep too small; initial timepoint: trouble with node "rpN"`.
Confirmado em 2026-09-07. Calcule o palpite, não arbitre — para PMOS em ligação diodo,
`V(rp) = VDD − (|VTO| + √(2·IB/(KP·W/L)))`.

**Detector de disparo: limiar ADAPTATIVO, nunca fixo.** Use 50% da excursão do próprio
`out` na janela medida, não uma fração de VDD. Em 2026-09-07 um limiar fixo de 0,9 V produziu
um falso **"não dispara"** em `Cmem` = 400 e 800 fF, onde o pulso colapsa para 0,82 e 0,72 V —
o circuito oscilava em regime estacionário e o detector é que não via. **É a mesma classe dos
outros erros de instrumento deste projeto:** o `abstol` contra o sinal, o `reltol` contra o
pico do ramo, a janela de média sem ciclos inteiros. Em todos, o que falhou foi a medida e não
o circuito, e em todos o sintoma foi um resultado que parecia físico.

**`Ctot` do nó de membrana: 129,71 fF, medido.** Espalhamento de **0,05%** sobre dois decades
de `Iin` (2026-09-07). Contra os **120 fF** de `Cmem` + `Cfb` ideais, sobram **9,7 fF** de
capacitância de porta de `M1p`/`M1n` e de junção — ordem fisicamente coerente para 1,5 µm² de
área de porta neste nó. Use este valor em vez de estimar `Ctot` por soma de nominais.

**Armadilha de contagem dupla: `Ctot` medido pela rampa JÁ CONTÉM a fuga.** Medindo
`Ctot = Iin/(dV/dt)`, o que se obtém não é `Ctot`: é
`Ctot_real · Iin/(Iin − fuga)`, porque `dV/dt = (Iin − fuga)/Ctot_real`. O valor vem inflado —
**+5,70% em `Iin` = 1 pA** com a fuga de 60 fA deste circuito, e o inflacionamento **cresce
quando `Iin` cai**, imitando perfeitamente uma capacitância que varia. **Somar esse `Ctot`
aparente a um termo de fuga separado é contar o mesmo efeito duas vezes.** Ou se desconta a
fuga do `Ctot` medido, ou se usa o `Ctot` aparente sozinho — nunca os dois.
Verificação que estabeleceu isto: a razão prevista pela curva de fuga era +5,745% e a medida
+5,701%, concordando em 0,04 ponto percentual.

**Corrente estática se mede por ponto de operação DC, nunca por média de transiente.**
O critério de convergência de um ramo é `reltol·|I| + abstol`, e o `|I|` que manda é o **maior
valor que aquele ramo carrega**, não o que se quer medir. Um ramo que conduz 2,9 µA nas
transições tem resolução efetiva de ~290 pA com `reltol` = 1e-4, mesmo com `abstol` em 1 fA.
Medido em 2026-09-07: a estática de um inversor receptor deu **0,1325 pA** em DC e
**1 607 pA** no transiente — **12 128×** de diferença, caindo para 428 pA ao apertar `vntol`.
Sinais de que o número é piso do solver e não do circuito: o nó de saída assenta alguns nV
**acima do trilho**; a corrente fica constante com desvio padrão da mesma ordem da média; e a
razão tensão/corrente não corresponde a condutância alguma do netlist. **Este é o erro
fundador do projeto um nível abaixo** — lá era o `abstol` em relação ao sinal, aqui é o
`reltol` em relação ao pico do ramo.

**Potência: integrar sobre número INTEIRO de ciclos.** Descartar 20% e integrar o resto
deixa um ciclo parcial na janela, e a sobra produz espalhamento da ordem de 1/N — o
bastante para gerar uma curva de potência não-monotônica que não é física. Integrar entre
o primeiro e o último cruzamento de disparo da janela. Confirmado em 2026-09-07: corrigiu
um espalhamento de ±5 nW numa medida de ~85 nW.

**Versão do simulador — obrigatória no cabeçalho.** Todo relatório em `resultados/`
declara a versão exata do ngspice usada (`ngspice --version`). Versões diferentes dão
números diferentes: a revalidação da etapa 0 rodou na **42** e o experimento de fome de
corrente na **41**, e essa diferença é candidata aos 11% de divergência na potência da
linha de base entre os dois. Sem a versão registrada, não há como separar mudança de
circuito de mudança de ferramenta.

**Unidades:** SI com prefixos SPICE (`f` = femto, `p` = pico, `u` = micro, `n` = nano).
Atenção: em SPICE `M` significa *mili*, não mega — use `MEG`. Todo número em texto,
gráfico ou commit carrega unidade.

**Onde ficam as coisas:**

```
CLAUDE.md                    este arquivo
README.md                    visão geral e como rodar
docs/dossie.pdf              o dossiê técnico v1.0
docs/caderno.md              registro de decisões e descartes
docs/decisoes.md             log datado: o que mudou e por quê
spice/neuronio.cir           netlist do neurônio
spice/models/                modelos e PDK
spice/testbenches/           f–I, Monte Carlo, cantos
scripts/run_sims.py          executa a bateria de simulações
scripts/plots.py             gera os gráficos
resultados/<AAAA-MM-DD_tag>/ dados brutos e figuras, datados — nunca sobrescrever
fpga/                        Verilog do roteador AER (etapa 6)
```

**Como rodar** (a partir da raiz do projeto):

```bash
RUN_TAG=2026-09-06_teste python3 scripts/run_sims.py   # grava em resultados/<RUN_TAG>/
RUN_TAG=2026-09-06_teste python3 scripts/plots.py
ngspice -b spice/neuronio.cir                          # simulação avulsa
```

Os scripts leem `NGSPICE_BIN` (padrão: `ngspice` do PATH) e `RUN_TAG` (padrão:
`rodada_atual`) do ambiente. Não há mais caminhos absolutos embutidos.

**Resultados:** uma pasta datada por rodada em `resultados/`. Nunca sobrescrever uma
rodada anterior — comparar a simulação de hoje com a de duas semanas atrás é
frequentemente o que revela um erro.

---

## 7-A · Riscos NOVOS, ausentes do mapa de riscos do dossiê §8

Levantados por medida ao longo da etapa 1. O dossiê §8 não os contém e precisa recebê-los.

### R1 · Descasamento de CAPACITOR vira dispersão de frequência — **novo na etapa 2**

**Por que é novo.** Enquanto `Cmem` era irrelevante para a frequência, o casamento entre
capacitores não precisava entrar no Monte Carlo. **Isso mudou:** `f ∝ Ctot^-0,85` (§3), então
dispersão de capacitância vira **dispersão de frequência diretamente**.

**O que o PDK oferece — verificado em 2026-09-07:**

| | situação |
|---|---|
| arquivos `__mismatch.corner.spice` | existem para **transistores e resistores**; **nenhum para capacitor** |
| mismatch no modelo do capacitor | **existe, embutido no subcircuito** |
| como está expresso | `czero = carea + cperim + MC_MM_SWITCH·AGAUSS(0,1,1)·0,01·2,8·(carea+cperim)/sqrt(wc·lc·mf)` |
| σ implicado | **2,8% ÷ √(área em µm²)** |
| **estado padrão** | ⚠️ **DESLIGADO** — `sky130.lib.spice` define `mc_mm_switch = 0` em **todos** os cantos |
| variação global de capacitância | disponível como cantos `cap_high` / `cap_low` em `libs.tech/ngspice/r+c/`, **não** selecionados pelo canto `tt` |

**A armadilha concreta:** rodar Monte Carlo sem `mc_mm_switch = 1` faz os capacitores **não
variarem nada** — não é que variem pouco, é que a contribuição é exatamente **zero**. O
histograma de frequência sairia artificialmente estreito, e a decisão da etapa 2 entre
"transistores maiores" e "calibração individual" seria tomada sobre um número otimista.

**Ordem de grandeza esperada, se ligado.** Com densidade MiM da ordem de 2 fF/µm²
(**a conferir no PDK, não medida**):

| | área | σ de C |
|---|---|---|
| `Cmem` = 100 fF | ~50 µm² | 0,40% |
| `Cfb` = 20 fF | ~10 µm² | 0,89% |
| σ de `Ctot` | — | **0,33%** |
| **σ de f pelos capacitores** | — | **~0,28%** |

Contra os critérios da etapa 2 (dispersão pequena ≈ 5%, grande ≥ 40%), **os capacitores
provavelmente não são o problema** — MiM casa bem, como se esperava. **Mas "provavelmente" não
é medida**, e é justamente por parecer desprezível que o switch fica desligado e ninguém
percebe. **Ação para a etapa 2: `mc_mm_switch = 1` explícito, e verificar no histograma que a
contribuição dos capacitores aparece.**

### R2 · Acoplamento por substrato entre neurônios vizinhos

Ver §5-A item 15b. Injeção de até 3,7 pA no substrato a cada disparo, num circuito cujo
**sinal também é de pA**. Mitigação por anel de guarda custa área, e amarra-se a R1 e à
contagem de neurônios.

### R3 · `Mrst` é dispositivo crítico de casamento

Ver §5 item 4. `Wrst` variado 32× move a frequência 2,3×, então descasamento de `Mrst` vira
dispersão de frequência. Soma-se a R1: a etapa 2 tem agora **três** caminhos de descasamento
para a frequência — transistores do inversor, `Mrst`, e capacitores — onde o dossiê previa um.

---

## 8 · Duas regras invioláveis deste projeto

**Regra 1 — Nunca aceite um resultado de simulação sem antes tentar derrubá-lo.**
Antes de registrar qualquer número, pergunte: qual seria o valor esperado por um modelo
analítico independente? O resultado sobrevive se eu mudar `tstep`, `tstop`, a condição
inicial, o método de integração? Existe um caso-limite em que ele deveria falhar e não
falha? Um resultado que ninguém tentou quebrar não é um resultado — é uma expectativa
com aparência de dado. A §5 é o exemplo de como isso se faz.

**Regra 2 — Todo número precisa de unidade e de denominador.**
"18% de deriva" não significa nada; "18% pico-a-pico de f, com denominador f em VDD
nominal, para VDD variado ±10%" significa. Percentual sem base, ganho sem faixa de
validade e "melhorou 2×" sem dizer em relação a quê são proibidos em qualquer arquivo
deste repositório — código, gráfico, commit ou comentário.

---

## 9 · O que NÃO fazer (erros já cometidos ou descartados)

- **Não aplicar fome de corrente simétrica** (limitar os dois lados do inversor com o mesmo
  IB). Descartado em 2026-09-06 com medida: dá 302 a 1 949 nW, **pior que as fontes ideais**
  (218 nW) e 3,6× a 23× pior que a assimétrica (83,5 nW). Motivo: na faixa em que a membrana
  opera (0,41–0,99 V) os dois transistores conduzem sempre, e o nível de `n1` é fixado pela
  **razão** entre as correntes. Grampear ambas ao mesmo valor destrói a razão, `n1` estaciona
  em ~0,83 V dentro da janela de condução do estágio seguinte, e o curto-circuito migra de
  estágio em vez de desaparecer. Limitar **só o PMOS**. A variante só-NMOS também está
  descartada: não dispara em 1 e 10 nA.
- **Não usar espelho estreito no 2º estágio.** Um dispositivo de nA rouba excursão do pulso e
  derruba a saída para 81% de VDD. W = 5 µm, L = 1 µm.
- **Não rodar ngspice sem o bloco `.options` de tolerância.** Ver §7. O resultado não é
  "aproximado" nem "com ruído": é inválido, e deve ser descartado em vez de interpretado.
  Este erro já custou a etapa 0 inteira — três meses de números que tiveram que ser
  refeitos, e três hipóteses de física levantadas para explicar um artefato de simulador.
- **Não escrever caminhos absolutos dentro dos netlists gerados.** Um `.cir` versionado
  com `/home/<usuario>/...` no `.include` ou no `wrdata` não roda em outra máquina — o
  netlist deixa de ser reprodutível e vira registro morto. Gerar sempre relativo à raiz
  do projeto, com o ngspice rodando a partir dela. Corrigido em 2026-09-06 em
  `scripts/run_starving.py`, que cometia exatamente isso.
- **Não escrever caminhos absolutos nos scripts.** A etapa 0 gravou `/home/claude/...`
  em `run_sims.py` e `plots.py`; ao mudar de máquina os dados brutos (`.npy`) se perderam
  e sobrou só o PNG — é por isso que as ressalvas da §5 tiveram que ser reconstruídas
  lendo a figura. Corrigido em 2026-09-06. Use caminhos relativos a partir de `ROOT`.
- **Não afirmar qualidade de ajuste sem calcular.** Ver §5 item 3: uma string
  `"R² alto"` foi impressa como se fosse medida. Se um número aparece na saída, ele tem
  que ter sido calculado naquela execução.
- **Não sobrescrever resultados.** Uma pasta datada por rodada, sempre.
- **Não citar os números da §4 como definitivos** enquanto as ressalvas da §5
  estiverem abertas.
- **Não aumentar `Cmem` para "deixar o neurônio mais lento".** Não funciona (§3) e
  destrói a excursão de sinal.
- **Não planejar contingências para sistemas que ainda não existem.** Uma pergunta por
  vez, respondida antes da próxima. Os modos de falha imaginados consomem energia e os
  reais serão diferentes.
- **Não subir de etapa com erro escondido na anterior.** Cada etapa custa ~10× a
  anterior e detecta uma classe de erro que a anterior não conseguia ver.
- **Não tratar modelos nível 1 como preditivos.** Eles não modelam condução sub-limiar —
  exatamente a região de pA onde o neurônio opera. Tendências valem; valores absolutos não.
