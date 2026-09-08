# Etapa 2 · rodada 1 — validação do instrumento estatístico

Data: 2026-09-08 · **ngspice 42** (`42+ds-3build1`, prefixo local `~/opt/ngspice42`)
· **sky130A**, cantos `tt` e `tt_mm`, `.temp 27` · N = 100 dispositivos por array,
N = 12 amostras de neurônio
Previsões pré-registradas em `previsao_pre_registrada.md`, commit `3b0400c`,
**antes de qualquer execução**.

> **Esta rodada não mede dispersão.** Nenhum número de frequência daqui é resultado da
> etapa 2. A pergunta era: o motor estatístico existe, sorteia por instância, é
> reprodutível, e tem a magnitude que o PDK declara?

---

## Placar das previsões

| teste | previsto | medido | veredito |
|---|---|---|---|
| **V5** integridade | f a menos de 1% de 139,58 Hz | **139,5821 Hz**, +0,002% | ✅ **passa** |
| **V0** controle negativo | σ(f) = zero exato | **0,000 Hz**; 6 arquivos, **1 SHA-256** | ✅ **passa** |
| **V1** sorteio por instância | 100 valores distintos por array | **100/100 nos três arrays** | ✅ **passa** |
| **V2** sorteio entre execuções | sem semente: idênticas | **diferentes** | ❌ **REFUTADA** |
| **V3** magnitude (array A) | σ(Vth_eq) 4,2 a 6,0 mV | **6,200 mV** | ⚠️ **3,3% acima da faixa** |
| **V3b** lei de Pelgrom | σ(A)/σ(C) = 2,00 ± 10% | **1,944** e **1,952** | ✅ **passa** |
| **V4** sensibilidade | σ(f)/f > 2% | **1,762%** | ❌ **REFUTADA** (mas passa o critério de falha) |
| **convergência** | desvio < 1% com `tstep`/4 | **−0,0006%** e **−0,0018%** | ✅ **passa** |

Duas previsões refutadas, uma fora da faixa por pouco, cinco confirmadas.
**O instrumento está validado.** Mas uma das refutações mudou o procedimento da etapa 2.

---

## O achado que importa: `set rndseed` NÃO fixa o sorteio

**Previsto:** que a ngspice sem semente explícita repetisse o mesmo sorteio, e que
`set rndseed` no `.control` o controlasse. **As duas metades estavam erradas.**

O que se mediu:

| mecanismo | mesma semente, 2 execuções | sementes diferentes | mesma semente, `tstep` diferente |
|---|---|---|---|
| `set rndseed=N` dentro do `.control` | **DIFERE** | difere | **DIFERE** |
| `.option seed=N` no netlist | **idêntico bit a bit** | difere | **idêntico bit a bit** |

**O mecanismo, e ele é geral.** Os `.model` que carregam o `AGAUSS` são avaliados quando
o netlist é **lido**. O bloco `.control` só executa **depois**. Um `set rndseed` ali chega
tarde: o sorteio já aconteceu, com a semente que a ngspice escolheu sozinha — que varia
entre execuções. `.option seed` é uma diretiva de netlist e chega a tempo.

**Como isso foi pego, e não foi pelo teste que deveria pegar.** O V2 comparou arquivos e
viu que diferiam — mas eu li isso como "a semente funciona". O que derrubou a leitura foi o
**teste de convergência**: a frequência mudou **+4,84%** ao dividir `tstep` por 4, num
circuito que converge a 0,002%. Como o sorteio não pode depender do `tstep`, ou a
convergência estava quebrada ou a amostra tinha mudado.

**O desempate foi um `op` antes do `tran`.** O ponto de operação DC não depende de `tstep`.
Com `set rndseed=1` nas duas execuções:

| nó | `tstep` = 0,5 µs | `tstep` = 0,125 µs |
|---|---|---|
| `v(rp1)` | 0,843524 V | **0,852996 V** |
| `v(rp2)` | 0,683184 V | **0,686550 V** |

9,5 mV de diferença num DC. **Não era convergência: era outra amostra.** Refeito com
`.option seed`, o desvio de convergência caiu de **+4,84%** para **−0,0006%** — fator
**8 000×**.

**Por que isto é grave e não apenas chato.** Sem `.option seed`, um Monte Carlo roda,
produz um histograma, e **não pode ser repetido** — nem para conferir, nem para separar
uma cauda de um artefato, nem para comparar com a rodada seguinte. E o sintoma não é um
erro: é um resultado com aparência perfeitamente física. **É a quarta ocorrência da mesma
classe de falha neste projeto** — `abstol` contra o sinal, `reltol` contra o pico do ramo,
limiar fixo contra pulso colapsado, e agora semente contra ordem de avaliação. Em todas, o
que falhou foi o instrumento e o sintoma foi um número limpo.

---

## V1 · o sorteio é por instância — inclusive no par do espelho

O modo de falha perigoso pré-registrado **não ocorreu**. O array B tem 100 cópias de
`W=5 L=1` — a geometria de `Mbp2` **e** `Mref2`, idênticas entre si — e as 100 correntes
saíram distintas. O par do 2º espelho vai descasar de verdade na rodada 2.

| array | dispositivo | área | distintos, `tt_mm` | distintos, `tt` | σ(Id)/Id em `tt_mm` |
|---|---|---|---|---|---|
| A | `nfet` W=1 L=0.5 | 0,5 µm² | **100/100** | 1/100 | 1,944% |
| B | `pfet` W=5 L=1 | 5,0 µm² | **100/100** | 1/100 | 2,515% |
| C | `nfet` W=4 L=0.5 | 2,0 µm² | **100/100** | 1/100 | 0,967% |

Denominador: média do próprio array, |Vgs| = 1,20 V, Vds = 1,8 V, canto `tt_mm`.

---

## V3 · a magnitude, contra os slopes do PDK

σ(Vth equivalente) = σ(ln Id) × n·Ut em sub-limiar; σ(Id)/gm em inversão forte.

| array | regime | medido | previsto só `vth0` | previsto `vth0`+`voff` | medido/previsto |
|---|---|---|---|---|---|
| A `nfet` 0,5 µm² | inversão forte | 6,200 mV | 4,746 mV | — | **1,31×** |
| A | **sub-limiar** | 11,486 mV | 4,746 mV | 10,978 mV | **1,046×** |
| B `pfet` 5 µm² | inversão forte | 2,476 mV | 2,619 mV | — | **0,95×** |
| B | **sub-limiar** | 3,483 mV | 2,619 mV | 2,619 mV (`voff_slope` = 0) | **1,33×** |
| C `nfet` 2 µm² | inversão forte | 3,189 mV | 2,373 mV | — | **1,34×** |
| C | **sub-limiar** | 5,885 mV | 2,373 mV | 5,489 mV | **1,072×** |

**Onde minha previsão errou, e o erro é instrutivo.** Pré-registrei 5,0 mV para o array A
descartando `voff` como "desprezível em inversão forte". Medido: 6,200 mV — a faixa
[4,2; 6,0] mV ficou 3,3% curta. Mas o erro maior não é esse: é que **o `voff` do nfet tem
slope 2,1× maior que o do `vth0`** (7,0e-3 contra 3,356e-3 V·µm) e eu o dispensei com uma
frase. Em sub-limiar, onde o circuito de fato opera, incluí-lo faz os dois arrays de nfet
baterem em **1,046×** e **1,072×** — praticamente exato.

**O pfet excede em 1,33× em sub-limiar, e o `voff` não pode explicar** — o
`voff_slope` do `pfet_01v8` é **zero** neste bin. O único termo estatístico restante
específico do PMOS é o **`nfactor_slope` = 0,1**, que não existe para o nfet. Isso é
**evidência do risco R4, não prova**: não isolei o parâmetro, apenas eliminei os outros.

**Um erro meu de análise, corrigido antes de reportar.** A primeira extração em sub-limiar
deu `n` = 0,73 — fisicamente impossível, já que `n` ≥ 1. Eu havia usado a secante
(I₂−I₁)/ΔV como se fosse a derivada de uma exponencial; ela superestima `gm` por
(e^x−1)/x ≈ 2,0 nas condições usadas. Refeita em espaço logarítmico, `n` = 1,49 a 1,56 e a
inclinação sub-limiar sai 89,7 a 101,7 mV/década — **cercando os 91,3 mV/década medidos na
etapa 1** por um caminho independente.

**V3b · a lei de Pelgrom.** σ(A)/σ(C) = **1,944** (inversão forte) e **1,952** (sub-limiar),
contra o 2,000 geométrico de 4× de área. Concordância em dois regimes de polarização
independentes. Antes de fixar a semente esta razão dava 2,32 — o excesso era ruído de
amostra, não física.

---

## V4 · a frequência se move quando deve

N = 12, canto `tt_mm`, sementes 1 a 12 via `.option seed`.

| | valor | denominador |
|---|---|---|
| média | 139,6467 Hz | 12 amostras; nominal `tt` = 139,5821 Hz (viés de +0,046%) |
| **σ(f)/f** | **1,762%** | média das 12 |
| extremos | 133,596 a 143,231 Hz | espalhamento 1,072× |
| todas dispararam | sim | excursão mínima de `out` = 1,57 V |
| nenhum nó fora dos trilhos | sim | `out` máx global 1,6199 V < VDD = 1,8 V |

**Previsão de > 2% REFUTADA por pouco.** Mais interessante que o erro: **1,76% é 6,2× menor
que os ~11% de piso estimados para σ(IB)/IB dos espelhos.** A corrente do espelho descasa
muito mais do que a frequência. Isso é consistente com `IB1` fixar só a parcela de
*disparo* do período, e não a de *rampa* — mas **não foi testado**, e a decomposição do
período em rampa e disparo continua sendo o experimento que responderia (§5-A item 14).

**Este 1,762% NÃO é a dispersão da etapa 2** e não deve ser citado como tal. N = 12 é
pequeno, e falta a distinção que a rodada 2 tem de fazer: aqui os ramos de referência
`Mref1`/`Mref2` sorteiam junto com o neurônio. Num chip real **a referência é compartilhada
entre N neurônios** — o sorteio dela desloca todos juntos (não é dispersão) enquanto só
`Mbp1`/`Mbp2` variam por neurônio. As duas topologias dão números diferentes, e a rodada 2
precisa medir a certa.

---

## Ressalvas desta rodada

1. **O array B em sub-limiar opera perto do piso do solver.** Id = 9,67e-14 A com
   `abstol` = 1e-15 A: a resolução é **1,03% da média**, contra um σ medido de 8,76% —
   folga de só **8,5×**. Os números de B em sub-limiar são utilizáveis, não confortáveis.
2. **O ponto de polarização de B não é o do circuito.** `Mbp1` opera em 10 nA e `Mbp2` em
   3 µA; medi em 0,1 pA. V3 é teste de instrumento, não caracterização do espelho.
3. **Arrays A e C caem em bins BSIM diferentes** (W=1 µm em [1,00; 1,26[ µm; W=4 µm em
   [3,0; 5,0[ µm). O V3b compara dispositivos com parâmetros nominais distintos; que a
   razão dê 1,94–1,95 apesar disso reforça o resultado, mas a comparação não é pura.
4. **Avisos de `.cm` não resolvidos.** A ngspice do prefixo local procura os modelos XSPICE
   em `/usr/lib/...` e não os acha. O circuito não usa nenhum, e o V5 reproduziu a etapa 1 a
   0,002% assim — **não mexi no ambiente depois de validá-lo**. Fica registrado.
5. **`mult`/`nf` não foram exercitados.** Todos os dispositivos têm `mult` = 1. Se a rodada 2
   usar multiplicidade para casar, o `sqrt(l*w*mult)` da fórmula precisa ser reverificado.

---

## O que fica obrigatório para a rodada 2

| regra | motivo |
|---|---|
| **`.option seed=N` no netlist. NUNCA `set rndseed` no `.control`** | os `.model` são avaliados antes do `.control`; sem isso o Monte Carlo não é reprodutível |
| **canto `*_mm`** (`tt_mm`, `ss_mm`, …), nunca o canto liso | `mc_mm_switch` = 0 nos cantos normais: contribuição exatamente zero |
| **rodar o controle negativo junto**, no canto liso, e exigir σ = 0 | é o que provaria que uma dispersão futura é descasamento e não fundo |
| **conferir a convergência com a semente FIXA** | com a semente solta o teste mede a amostra, não o integrador |
