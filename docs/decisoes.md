# Log de decisões

Uma linha por decisão, com data e motivo. Daqui a meses, a razão do descarte é mais
valiosa que o descarte. Ordem cronológica inversa (mais recente no topo).

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
