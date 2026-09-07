# Drone Neuromórfico — contexto do projeto

> Este arquivo é a memória do projeto. Está estruturado conforme a Parte 9.3 do
> dossiê (`docs/dossie.pdf`). Atualize-o ao fim de cada etapa.
> Última atualização: 2026-09-06.

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
| 1 | Migrar para PDK SkyWater 130 nm | **Próxima** — plano em revisão, não iniciada |
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

**`Cmem` é um controle fraco, com resíduo medido de 24% em 16×.** O cancelamento é real
e dominante — a intuição ingênua `f ∝ 1/Cmem` previria 1600% — mas **não é exato**. Medido
na revalidação: 183,1 Hz em 25 fF → 140,0 Hz em 400 fF. A formulação anterior, de que
`Cmem` "some da equação", estava forte demais. O que fixa a frequência de primeira ordem é
`Cfb`, `VDD` e `Iin`; `Cmem` entra como termo residual.

**O modelo acima é incompleto por um motivo identificado:** ele supõe reset completo e
auto-terminado. O reset real é incompleto — a membrana para em 0,406 V, não em zero — e
por isso `Mrst` também fixa a frequência (ver §4 e §5 item 4).

**Consequência de projeto:** `Cmem` deve ser **pequeno**. Não por velocidade, mas porque
com `Cmem` grande a excursão de sinal desaba (1,43 V em 25 fF → 0,107 V em 800 fF, medido)
e abaixo de ~0,2 V o neurônio fica refém de descasamento entre transistores e ruído de
alimentação. A frequência se controla pela corrente de entrada, não pela capacitância.

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
   ⚠️ **Ressalva nova, não fechada:** a curva é monotônica decrescente de 25 a 400 fF, mas
   o ponto de 800 fF **sobe** de 140,0 para 151,0 Hz (+7,9%). Com CV intra-corrida de
   0,03%, esse salto é ~260× o ruído: é estrutura real, não artefato, e não está explicada.
   A descrição "monotônica decrescente e limpa" vale para 25–400 fF, não para a série toda.

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
   para a ordem de **200 nW** (198 nW pela conta de 10 nA + 100 nA a 1,8 V; a estimativa do
   autor é 216 nW) e o requisito desaba de 370 para **~15 neurônios**.
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

---

## 6 · Decisões tomadas — não reabrir sem motivo novo

| Data | Decisão | Motivo |
|---|---|---|
| 2026-09 | **Um chip homogêneo, replicado** — não chips especializados por modalidade | O gargalo real é a comunicação entre chips; a proporção entre modalidades é desconhecida e chips fixos a travam cedo demais; três máscaras custam três vezes mais. Mesma escolha de Loihi, SpiNNaker e Akida. Exceção legítima: a interface analógica de sensor é específica por modalidade e vai num chip pequeno separado. |
| 2026-09 | **Topologia axon-hillock** (Mead, 1989), 7 transistores — **CONFIRMADA em 2026-09-06 com fome de corrente assimétrica no PMOS de ambos os estágios: 83,5 nW por neurônio, 151× abaixo da linha de base** | Base histórica validada; simples o bastante para ser entendida por inteiro antes de complicar. O consumo de 12,6 µW, que chegou a ameaçar a escolha, é corrigível dentro da própria topologia — não exige trocá-la. Fonte: `resultados/2026-09-06_espelho/espelho.md`. |
| 2026-09-06 | **A fome de corrente é ASSIMÉTRICA: limita-se só o PMOS**, nunca os dois lados do inversor | A membrana opera entre 0,41 e 0,99 V, faixa em que M1p e M1n conduzem os dois sempre. O nível de `n1` é fixado pela **razão** entre as duas correntes. Grampear ambas ao mesmo IB destrói essa razão: nenhum lado vence, `n1` estaciona em ~0,83 V — dentro da janela de condução do 2º inversor — e o curto migra de estágio. Medido: fome simétrica dá 302 a 1 949 nW, **pior que as fontes ideais** (218 nW). A variante só-NMOS não dispara em 1 e 10 nA. |
| 2026-09-07 | **A faixa útil do neurônio é `Iin` de 1 a 50 pA (f de 14 a 690 Hz)** | Acima de ~54 pA o consumo excede os 100 nW do orçamento (104,2 nW em 70 pA, 112,4 nW em 100 pA). Em vez de afrouxar o alvo de potência ou buscar outro ponto de polarização, limita-se a faixa. Consequência: a faixa útil encolhe de dois decades para 1,7, e o teto de frequência cai de 1,38 kHz para 690 Hz. Medida em `resultados/2026-09-07_fi_espelho/fi_espelho.md`. |
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

**`.nodeset` obrigatório em netlist com espelho de corrente.** Com `uic`, o ngspice pula o
ponto de operação DC e parte de 0 V em todo nó fora do `.ic`. O nó de referência de um
espelho em 0 V põe o transistor diodo com Vsg = VDD, muito acima da corrente de projeto, e
a simulação **aborta**: `Timestep too small; initial timepoint: trouble with node "rpN"`.
Confirmado em 2026-09-07. Calcule o palpite, não arbitre — para PMOS em ligação diodo,
`V(rp) = VDD − (|VTO| + √(2·IB/(KP·W/L)))`.

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
