# Log de decisões

Uma linha por decisão, com data e motivo. Daqui a meses, a razão do descarte é mais
valiosa que o descarte. Ordem cronológica inversa (mais recente no topo).

---

## 2026-09-07 — Etapa 1 concluída, invertendo o achado central

**Fontes:** `resultados/2026-09-07_migracao_sky130/`, `_receptor/`, `_fuga_mem/`,
`_histerese/`, `_cmem_sky130/` — todas em ngspice 42, sky130A, canto `tt`, 27 °C.

**Os seis critérios de saída fecharam.** Armadilha do W/L (é *fail-stop*, não silenciosa),
neurônio migrado (f–I a 0,7% do nível 1, consumo 14× menor, 43,2 pJ por disparo), pulso
aprovado no critério funcional, fuga em `mem` medida, janela de histerese medida, e varredura
de `Cmem`.

**E a etapa fecha invertendo o achado central do projeto.**

| | nível 1 | sky130 |
|---|---|---|
| expoente de `f ∝ Ctot^-x` (25 a 200 fF) | **0,16** | **0,85** |
| cancelamento restante | **84%** | **15%** |

**O mecanismo, que fecha a história.** O cancelamento exigia que a janela de histerese fosse
`VDD·Cfb/Ctot` e portanto encolhesse junto com `Ctot`. A janela medida é **0,679 V** contra os
**0,278 V** do divisor — fator 2,45×. **O chute capacitivo é só 41% da janela.** Os outros 59%
são a distância entre o limiar de comutação e o fundo do undershoot, que são tensões
**absolutas** e não encolhem com `Ctot`. Daí a evaporação do cancelamento — e daí ele depender
do modelo: no nível 1 o `V_th` menor deixava o termo do divisor dominar.

**Nota de método que vale registrar.** A previsão de que o cancelamento seria geométrico e
independente do modelo era razoável, **e a medida da janela já a contradizia uma rodada
antes**. O fator 2,45× estava registrado e eu não tirei a consequência dele. O dado que
refutava a hipótese já estava na mesa antes de eu apostar contra ele.

**A decisão de projeto sobrevive com motivo melhor.** `Cmem` pequeno continua certo, agora
porque `Cmem` > 200 fF empurra o circuito para fora do regime integra-e-dispara (CV do ISI
piora 26×, o pulso perde excursão lógica, a frequência inverte de sentido). E há um ganho: o
projeto passa a ter **dois botões independentes** de frequência, `Iin` e `Cmem`, onde
acreditava ter um.

**Segunda correção do impacto na área.** Já se havia corrigido para "`Cfb` fixa a frequência e
não pode encolher". Agora `Cmem` também fixa. **Não há economia de área livre em capacitor
neste circuito** — os dois são compromissos acoplados com a frequência.

**Risco novo para a etapa 2, verificado no PDK.** Enquanto `Cmem` era irrelevante, o casamento
entre capacitores não precisava entrar no Monte Carlo. Agora precisa. O modelo MiM do sky130
**tem** mismatch embutido (σ = 2,8%/√área), mas `sky130.lib.spice` define `mc_mm_switch = 0`
em todos os cantos — **desligado por padrão**. Rodar Monte Carlo sem ligá-lo dá contribuição
capacitiva exatamente zero e um histograma artificialmente estreito. Registrado no `CLAUDE.md`
§7-A como R1, junto com R2 (acoplamento por substrato) e R3 (`Mrst` crítico de casamento). A
etapa 2 tem agora **três** caminhos de descasamento para a frequência, onde o dossiê previa um.

**Quinto erro de instrumento da série.** Um detector com limiar fixo de 0,9 V produziu um falso
"não dispara" contra um pulso colapsado para 0,82 V. Limiar adaptativo virou convenção. É a
mesma classe do `abstol` contra o sinal, do `reltol` contra o pico do ramo, e da janela de
média sem ciclos inteiros: em todos, o que falhou foi a medida, e em todos o sintoma foi um
resultado que parecia físico.

**Etapa 2 não iniciada.**

---

## 2026-09-07 — Etapa 1 iniciada: PDK instalado e transistor isolado validado

**Fonte:** [`resultados/2026-09-07_etapa1_pdk/validacao_pdk.md`](../resultados/2026-09-07_etapa1_pdk/validacao_pdk.md)
— ngspice 42, sky130A, canto `tt`, 27 °C.

**Instalação enxuta, medida antes de baixar.** Só os dois assets do volare que contêm o que
o ngspice consome: `common` (16,6 MB, traz `libs.tech/ngspice/`) e `sky130_fd_pr` (14,0 MB,
traz `libs.ref/sky130_fd_pr/spice/`). Deixados de fora 166,7 MB de células padrão, 54,2 MB de
HVL, 50,7 MB de I/O e 30,3 MB de SRAM. Baixados 30,6 MB comprimidos contra ~380 MB do
conjunto completo. `sky130B` (ReRAM) removido após a extração. **Ocupação final: 127 MB.**

**A armadilha do W/L existe, mas é `fail-stop`, não `fail-silent`.** `W=1u L=0.15u` entrega
1e-06 ao seletor de binning do BSIM4, que aborta com `could not find a valid modelname`.
A forma correta é número puro em µm: `W=1 L=0.15`. Isso é melhor do que eu previa — a
armadilha não pode contaminar resultado em silêncio.

**Descoberta lateral: `.option scale=1u` é irrelevante pela via do `.lib`.** Está em
`all.spice`, mas não na cadeia `sky130.lib.spice` → `corners/tt.spice`. Com números puros o
resultado é idêntico com e sem. Registrado no `CLAUDE.md` §7 para não ser reintroduzido
"por precaução" por alguém lendo o PDK de fora.

**Placar das previsões pré-registradas (commit `a0ffaf6`, antes da medida): duas refutadas.**

| Previsão | Veredito |
|---|---|
| A armadilha existe | confirmada |
| A armadilha é silenciosa | **REFUTADA** — é erro fatal |
| Id de 400 a 700 µA em W=1 L=0,15 | confirmada — 501,05 µA |
| Fuga de 0,1 a 10 fA a 27 °C | **REFUTADA** — 84,7 fA, 8,5× acima |
| Sem zona morta a 27 °C | sobrevive, com margem menor |
| Zona morta de 1 a 10 pA a 125 °C | provavelmente subestimada — projeção agora dá 85 a 340 pA |

As duas refutações são do mesmo tipo: subestimei a severidade nas duas direções. O cálculo
de fuga errou porque assumi `n` ≈ 1,3; a inclinação medida de 91,3 mV/década implica
`n` ≈ 1,53.

**Consequência para a etapa 3, registrada agora para ser testada lá:** projetando 84,7 fA
para 125 °C com duplicação a cada 8–10 °C, a fuga do `Mrst` vai a **85–340 pA** — acima de
**toda** a faixa útil decidida hoje (1 a 50 pA). No canto quente o neurônio provavelmente não
dispara em ponto algum. Isso torna o `Mrst` o dispositivo crítico do canto quente, somando-se
ao papel dele de fixar a frequência (§5 item 4) e de caminho de descasamento (etapa 2).

**O neurônio ainda não foi migrado.** Esta rodada validou a pré-condição.

---

## 2026-09-07 — A curva f–I sobrevive; duas pendências fechadas, duas abertas

**Fonte:** [`resultados/2026-09-07_fi_espelho/fi_espelho.md`](../resultados/2026-09-07_fi_espelho/fi_espelho.md)
— ngspice 42, modelos nível 1 inalterados, ponto IB1 = 10 nA / IB2 = 3 µA.

**O que fechou.** As pendências 1 e 2 do relatório do espelho. A curva f–I sobrevive com
folga: R² = 0,99999917 no ajuste de intercepto livre, expoente log–log 1,0005 (0,05% da
proporcionalidade exata), zona morta implícita de −22,8 fA — nenhuma, 44× abaixo do menor
ponto medido. Convergência: frequência invariante em 0,002% sobre 16× de `tstep`, contra
os 1% exigidos. Trilhos respeitados nos 12 pontos.

**A linearidade melhorou com a fome de corrente**, o que não era esperado: a razão f/`Iin`
deriva 0,7% ao longo de dois decades, contra 5% na linha de base. O preço é 14% de ganho
(16,0 → 13,79 Hz/pA).

**O `.nodeset` é obrigatório — confirmado e vira convenção.** Sem ele a simulação aborta
com `Timestep too small; initial timepoint: trouble with node "rp2"`. Causa: com `uic` o
ngspice parte de 0 V em todo nó fora do `.ic`, e o nó de referência em 0 V põe o transistor
diodo com Vsg = VDD, muito acima da corrente de projeto. Os valores foram calculados, não
arbitrados, e conferem com a medida dentro de 1 mV. `CLAUDE.md` §7.

**Correção de método, com custo real.** A média de potência sobre "descartar 20% e integrar
o resto" deixa um ciclo parcial na janela, e a sobra dá espalhamento de ±5 nW numa medida de
~85 nW — o bastante para produzir uma curva de potência não-monotônica que não é física.
Integrando sobre número inteiro de ciclos a curva fica limpa e monotônica. Isso também
explica os ~5% de diferença inicial contra o valor publicado: remedido, o ponto nominal dá
85,4 nW contra 83,5 nW, +2,2%. `CLAUDE.md` §7.

**Duas pendências NOVAS, ambas de arquitetura, ambas de denominador:**

1. **O ramo de referência do espelho custa 5,42 µW** — 63× o consumo do próprio neurônio.
   Está fora do orçamento por ser compartilhado, o que é legítimo, mas **por quantos
   neurônios nunca foi dito**. Para o total por neurônio caber em 100 nW é preciso
   **N ≥ 370**. Abaixo disso os 85,4 nW não descrevem o chip. Isso vira requisito de
   arquitetura: define um piso para o número de neurônios por ramo de polarização, e
   portanto interage com a decisão de calibração individual da etapa 2.
2. **O orçamento de 100 nW não vale em toda a faixa útil.** A potência cresce
   monotonicamente com `Iin` e cruza os 100 nW em ≈ 54 pA (f ≈ 745 Hz), enquanto a faixa
   declarada do neurônio vai a 100 pA. O critério foi enunciado no ponto nominal e lá passa
   com folga de 1,17×; na faixa inteira, não. Ou se limita a faixa, ou se afrouxa o alvo,
   ou se busca outro ponto de polarização — decisão do autor, não tomada aqui.

**Nota de reconstrução.** O netlist do Resultado 3 não veio junto — só o `mirror.cir` da
variante simétrica. Foi reconstruído da descrição do relatório e validado contra os números
publicados antes de ser usado: frequência (138,28 contra 138,3 Hz) e pulso (92,22 contra
92,2%) batem exatamente. As três premissas assumidas estão listadas na seção A do relatório.

**Fora do escopo por instrução:** mapear a vizinhança de IB2 entre 1 e 3 µA, e o PDK.

---

## 2026-09-06 — Consumo resolvido; a topologia axon-hillock FICA

**Fonte:** [`resultados/2026-09-06_espelho/espelho.md`](../resultados/2026-09-06_espelho/espelho.md)
— ngspice 42, modelos nível 1 inalterados.

**O que mudou:** o consumo de 12,6 µW por neurônio, que era a ressalva bloqueante da §5-A e
ameaçava a escolha de topologia, caiu para **83,5 nW** — redução de **151×**. Energia por
disparo: 78 nJ → **0,60 nJ**. A decisão de arquitetura está tomada pelo autor do projeto:
**a topologia axon-hillock fica.** A marca de revisão sai do `CLAUDE.md` §6.

**Por quê:** o problema nunca foi a topologia, foi o inversor operar permanentemente dentro
da janela de curto-circuito. Isso é corrigível **dentro** da própria topologia, limitando a
corrente do inversor — não exige trocá-la.

**A decisão de projeto nova, e é a parte não-óbvia: a fome de corrente é ASSIMÉTRICA.**
Limita-se só o PMOS, nunca os dois lados. A membrana opera entre 0,41 e 0,99 V, faixa em que
M1p e M1n conduzem os dois, sempre; o nível de `n1` é fixado pela **razão** entre as duas
correntes. Grampear ambas ao mesmo IB destrói essa razão — nenhum lado vence, `n1` estaciona
em ~0,83 V, dentro da janela de condução do estágio seguinte, e o curto **migra** do 1º para
o 2º inversor em vez de desaparecer. É o mesmo mecanismo do problema original, deslocado um
estágio adiante.

| variante | potência total | veredito |
|---|---|---|
| linha de base (sem fome) | 12 600 nW | — |
| fontes de corrente ideais | 218 nW | testbench inválido (viola trilhos) |
| fome **simétrica** (espelho) | 302 a 1 949 nW | **pior que as fontes ideais** — descartada |
| fome **assimétrica**, só 1º estágio | 107 a 306 nW | piso passa a ser o 2º estágio |
| fome **assimétrica**, os dois estágios | **83,5 nW** | **aprova** |

Descartadas com motivo, registradas no `CLAUDE.md` §9: fome simétrica; variante só-NMOS
(não dispara em 1 e 10 nA); espelho estreito no 2º estágio (rouba excursão, pulso cai a 81%
de VDD contra o mínimo de 90%).

**O elemento certo era um espelho de corrente, não uma fonte.** As duas tentativas
anteriores falharam pela mesma razão de fundo: uma fonte ideal é um *forçador* de corrente
(passa exatamente IB, sempre), e o que a topologia precisa é de um *limitador* (passa de 0 a
IB, conforme o circuito pedir). No espelho a fonte ideal fica no ramo de referência, onde o
transistor em ligação diodo sempre conduz e não há violação de trilho possível; o elemento
que limita o inversor é o transistor de saída do espelho, que é um transistor real. O ramo de
referência é compartilhado entre neurônios num chip real e por isso fica **fora do orçamento
por neurônio** — premissa que vale registrar, porque muda o denominador dos 83,5 nW.

**O que este resultado NÃO fecha:** cinco pendências foram para o `CLAUDE.md` §5-A. A que
bloqueia o critério de aceitação é a primeira — a curva f–I não foi refeita no ponto novo.

**Nota de método.** Os dois testbenches anteriores foram derrubados antes de produzirem
resultado (fontes ideais: conformidade infinita; fonte + resistor paralelo: Norton, com
V de circuito aberto em VDD + IB·R). Custaram duas rodadas e não geraram número algum que
tenha entrado no registro. Foi a Regra 1 funcionando como deveria: o resultado que não se
tentou derrubar não é resultado.

---

## 2026-09-06 — Revalidação da etapa 0: números refeitos, três hipóteses resolvidas

**Fonte:** [`resultados/2026-09-06_revalidacao_etapa0/revalidacao.md`](../resultados/2026-09-06_revalidacao_etapa0/revalidacao.md)
— ngspice 42, modelos nível 1 inalterados, **circuito não modificado**. A única alteração
foi o bloco `.options` acrescentado a `spice/neuronio.cir`.

**O que mudou:** a hipótese do `abstol` está **confirmada**, e com ela caem os números da
etapa 0. Não foram corrigidos — foram **descartados e refeitos**.

| Grandeza | Antes | Agora |
|---|---|---|
| Frequência nominal | 158 / ≈175 / ≈166 Hz | **160,3 Hz**, convergida |
| CV do ISI | 20% (não percebido) | **0,010%** |
| Ganho f–I | 17,5 Hz/pA | **16,0 Hz/pA** |
| Excursão (`Cmem` 25 fF → topo) | 1,05 V → 0,079 V | **1,43 V → 0,107 V** (a 800 fF) |
| Variação de f com `Cmem` (16×) | ~14%, não-monotônica | **24%**, monotônica de 25 a 400 fF |

**Por quê:** `abstol` padrão = 1e-12 A = 1 pA, da ordem do sinal; `trtol` padrão = 7,
relaxando o controle de erro de truncamento. As duas juntas produziam 20% de CV do ISI num
circuito determinístico — fator 2000 acima do correto. Virou regra permanente no
`CLAUDE.md` §7, com entrada correspondente no "o que não fazer" (§9).

**Três hipóteses, três vereditos:**

1. **Consumo excessivo — CONFIRMADA, pior que o estimado.** 12,6 µW por neurônio,
   **7 × 10⁵ vezes** a potência do sinal de entrada (18 pW), 78 nJ por disparo contra
   1–100 pJ na literatura. Independente de `Iin` de 1 a 100 pA: é piso fixo, não consumo de
   sinal. Mecanismo: a faixa de operação da membrana (0,41–0,99 V) está inteiramente dentro
   da janela em que os dois transistores do primeiro inversor conduzem — o inversor nunca
   sai da região de transição. Previsto 7,5 µA, medido 7,1 µA.

2. **Zona morta por corrente de fuga — REFUTADA.** Era hipótese minha, registrada como
   previsão a priori do plano da etapa 1. A reta passa pela origem e não há zona morta
   detectável até 1 pA; a razão f/`Iin` fica entre 15,3 e 16,04 Hz/pA em toda a faixa. A
   discrepância que motivou a hipótese era inteiramente ruído numérico.

3. **Fator 1,76× do modelo analítico — CONFIRMADO o desvio, REFUTADA a minha causa.** Eu
   havia atribuído a *overshoot* da saída acima de VDD. É **reset incompleto**: a membrana
   para em 0,406 V porque `Mrst` é fraco. `Wrst` variado 32× move a frequência 2,3×.
   **`Mrst` é um elemento que fixa a frequência** — e o dossiê não o identifica como tal em
   lugar nenhum. Consequência não prevista no mapa de riscos do dossiê §8: há um caminho
   direto de descasamento de `Mrst` para dispersão de frequência entre neurônios, o que faz
   dele um dispositivo crítico de casamento na etapa 2.

**O achado principal sobrevive, com correção de formulação.** `Cmem` continua não sendo o
controle de frequência — 16× de capacitor para 24% de frequência, contra os 1600% que
`f ∝ 1/Cmem` previria. Mas a afirmação anterior de que `Cmem` "some da equação" estava forte
demais: sobra um resíduo medido de 24%. O modelo `T = Cfb·VDD/Iin` só valeria com reset
completo e auto-terminado, que não é o caso.

**Ressalva nova, aberta, levantada na conferência desta integração:** a varredura de `Cmem`
é monotônica decrescente de 25 a 400 fF, mas o ponto de **800 fF sobe** de 140,0 para
151,0 Hz (+7,9%). Com CV intra-corrida de 0,03%, isso é ~260× o ruído — estrutura real, não
artefato, e não explicada. A descrição "monotônica decrescente e limpa" vale para a faixa
de 16× usada na comparação, não para a série completa. Registrado em `CLAUDE.md` §5 item 2.

**O que NÃO foi feito:** nenhuma simulação nova nesta máquina (ngspice continua não
instalado aqui), nenhuma alteração de circuito, nenhum download de PDK. A etapa 1 não foi
iniciada.

**Decisão adiada, não tomada:** a §6 ainda registra a topologia axon-hillock como decisão
travada. O consumo medido é motivo novo suficiente para reabri-la, mas reabrir uma decisão
de arquitetura não é ato de registro — fica aguardando o autor do projeto.

---

## 2026-09-06 — Estrutura de pastas e CLAUDE.md criados

**O quê:** os arquivos soltos na raiz foram reorganizados conforme a Parte 9.2 do dossiê,
e o `CLAUDE.md` foi escrito conforme a Parte 9.3. Repositório git inicializado (ainda sem
commit).

**Movimentações:**

| De | Para |
|---|---|
| `Projeto_Drone_Neuromorfico.pdf` | `docs/dossie.pdf` |
| `neuron_tran.cir` | `spice/neuronio.cir` |
| `run_experiments.py` | `scripts/run_sims.py` |
| `make_plots.py` | `scripts/plots.py` |
| `neuronio_resultados.png` | `resultados/2026-09-06_etapa0_nivel1/` |

**Motivo:** o repositório é a memória do projeto; o que não estiver escrito nele não
existe para a ferramenta.

---

## 2026-09-06 — Caminhos absolutos removidos dos scripts

**O quê:** `scripts/run_sims.py` e `scripts/plots.py` apontavam para `/home/claude/...`
(binário do ngspice, diretório de trabalho, todos os `.npy` e `.txt`). Substituídos por
caminhos derivados de `ROOT` (a raiz do projeto, calculada a partir do próprio arquivo),
com `NGSPICE_BIN` e `RUN_TAG` lidos do ambiente. Os modelos nível 1, que estavam
duplicados como string dentro de `run_sims.py` e de novo no netlist, passaram a viver só
em `spice/models/generic_l1.mod`, incluído pelos dois.

**Motivo:** os scripts não rodavam nesta máquina — o caminho não existe. E a duplicação
dos modelos em dois arquivos é um convite a divergirem em silêncio, com o netlist e a
bateria de simulações simulando circuitos diferentes sem ninguém perceber.

**Custo já pago por esse erro:** os dados brutos da etapa 0 (`wave.npy`, `fi.npy`,
`caps.npy`, `vdd.npy`, `raw_cm_*.txt`) ficaram em `/home/claude` e não vieram junto.
Sobrou só o PNG. As ressalvas registradas abaixo tiveram que ser reconstruídas lendo
valores da figura, com a imprecisão que isso implica.

---

## 2026-09-06 — Ressalvas abertas sobre os resultados da etapa 0

**O quê:** ao reler os resultados da etapa 0 aplicando a Regra 1 (tentar derrubar),
quatro problemas apareceram. Registrados em `CLAUDE.md` §5 e reproduzidos aqui em resumo:

1. O mesmo circuito com parâmetros idênticos dá 158 Hz, ≈175 Hz e ≈166 Hz em três
   experimentos diferentes — ~10% de espalhamento que acompanha `tstep`, não a física.
2. A estrutura residual do painel 4 (14% pico-a-pico, não-monotônica) está perto demais
   desse ruído numérico para ser interpretada.
3. O R² da curva f–I nunca foi calculado; `plots.py` imprimia a string `"R² alto"`.
4. O modelo analítico `T = Cfb·VDD/Iin` acerta todas as tendências (independência de
   `Cmem`, proporcionalidade a `Iin`, escala com VDD dentro de 3%) e erra o valor
   absoluto por 1,76×. Falta um fator constante, provavelmente overshoot/undershoot.

**Motivo do registro:** a conclusão principal da etapa 0 (`Cmem` não controla a
frequência) **sobrevive** — 16× de capacitor para 14% de frequência é folgado. Mas os
valores absolutos da §4 do `CLAUDE.md` não devem ser propagados até estes quatro pontos
serem fechados. Fechá-los é parte da etapa 1, porque exigem re-rodar de qualquer forma.

**Descartado:** re-rodar a etapa 0 com nível 1 para refazer os *números de física*.
Motivo: os modelos nível 1 não descrevem a região sub-limiar, então qualquer valor
refeito com eles teria que ser refeito de novo na etapa 1.

**Mantido, porém:** um re-rodar *de numérica*, barato, antes do PDK — ver a entrada
seguinte sobre `abstol`. Ele testa a ferramenta, não o circuito, e pode dissolver as
ressalvas 1 a 3 sozinho.

---

## 2026-09-06 — Hipótese para a irreprodutibilidade de ~10%: `abstol`

**O quê:** o padrão de `abstol` no ngspice é **1e-12 A = 1 pA** — a tolerância absoluta de
erro de corrente abaixo da qual o simulador considera dois valores iguais. As simulações
da etapa 0 rodaram com `Iin` entre **1 pA e 100 pA**, sem nenhum `.options`. No ponto de
1 pA da curva f–I, **a corrente de sinal inteira cabe dentro da tolerância do simulador**.
No ponto nominal de 10 pA, a tolerância vale 10% do sinal.

O `gmin` padrão (1e-12 S, somado em paralelo a cada junção pn) agrega mais ~0,9 pA de
condutância parasita no nó `mem` a 0,9 V — de novo, a mesma ordem de grandeza de `Iin`.

**Por que importa:** isso é candidato a explicar as ressalvas 1, 2 e 3 de uma vez — o
espalhamento de ~10% entre execuções, a estrutura não-monotônica do painel 4 e a
curvatura da curva f–I nas correntes baixas. Todas se concentram exatamente onde a
corrente de sinal se aproxima de `abstol`.

**Status: hipótese, não resultado.** Não foi testada — ngspice não está instalado nesta
máquina. Testar é barato (re-rodar a etapa 0 com `.options abstol=1e-15 gmin=1e-15
reltol=1e-4 vntol=1e-9` e comparar), e por isso vira o passo 1.0 da etapa 1, antes de
qualquer download de PDK.

**Consequência se confirmada:** nenhum número de corrente sub-limiar produzido neste
projeto — agora ou depois, com PDK ou sem — é válido sem `abstol` apertado. Viraria uma
linha permanente do `CLAUDE.md`.
