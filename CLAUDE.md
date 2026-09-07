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
| 0 | Neurônio axon-hillock em ngspice, modelos nível 1 | **Concluída** (com ressalvas — ver §5) |
| 1 | Migrar para PDK SkyWater 130 nm | **Próxima** — plano em revisão, não iniciada |
| 2 | Monte Carlo (descasamento) | Não iniciada — maior risco do projeto |
| 3–10 | Cantos, par acoplado, coincidência, AER/FPGA, layout, tapeout | Não iniciadas |

Nenhum hardware foi construído. Todo número neste repositório vem de simulação ou de
literatura, e a origem está sempre indicada.

**Ambiente desta máquina (verificado em 2026-09-06):** Ubuntu 24.04. **ngspice NÃO está
instalado**; `numpy` e `matplotlib` **não estão instalados** no Python padrão
(`~/miniconda3/bin/python3`); nenhum PDK presente. Disco: 20 GB livres de 468 GB (96%
ocupado) — restrição real para instalar o sky130. Os scripts em `scripts/` **não foram
executados nesta máquina**; foram herdados da etapa 0, rodada em outro ambiente.

---

## 3 · Resultado central da etapa 0

**O capacitor de membrana não controla a frequência de disparo.**

Modelo analítico de primeira ordem que explica o achado (derivado, não medido):

- O degrau de realimentação desloca a membrana em `ΔV = VDD · Cfb / Ctot`, onde
  `Ctot = Cmem + Cfb + parasitas de gate`.
- A rampa de integração sobe a `dV/dt = Iin / Ctot`.
- Logo o período de integração é `T = Ctot · ΔV / Iin = Cfb · VDD / Iin`.

**`Cmem` cancela exatamente.** Não é uma quase-compensação numérica: some da equação. O
que fixa a frequência é `Cfb`, `VDD` e `Iin`.

**Consequência de projeto:** `Cmem` deve ser **pequeno**. Não por velocidade, mas porque
com `Cmem` grande a excursão de sinal desaba (1,05 V em 25 fF → 0,079 V em 400 fF, medido)
e abaixo de ~0,2 V o neurônio fica refém de descasamento entre transistores e ruído de
alimentação. A frequência se controla pela corrente de entrada, não pela capacitância.

**Impacto na área do chip:** a estimativa inicial supunha que o capacitor dominaria a área
do neurônio. Está invertida — o neurônio pode ser mais compacto que o previsto.

**Consequência ainda não explorada:** como `T ∝ VDD`, a frequência depende da alimentação
por construção. Isso explica quantitativamente o painel 6 (ver §5) e indica que a
compensação de VDD é um problema de topologia, não de ajuste fino.

---

## 4 · Números da etapa 0 (com unidade e denominador)

Todos com modelos nível 1, `Cmem = 100 fF`, `Cfb = 20 fF`, `VDD = 1,8 V`, T = 27 °C nominal.

| Grandeza | Valor | Denominador / condição |
|---|---|---|
| Frequência de disparo | 158 Hz | com `Iin` = 10 pA (EXP1, `tstop` 80 ms, `tstep` 2 µs) |
| Ganho f–I | 17,5 Hz/pA | ajuste linear sobre 12 pontos, `Iin` de 1 a 100 pA |
| Faixa de frequência | 24 Hz a 1,75 kHz | extremos medidos em `Iin` = 1 pA e 100 pA |
| Deriva com alimentação | 18% pico-a-pico | de f; denominador = f em VDD nominal (1,80 V); VDD variado ±10% (1,62–1,98 V) |
| Excursão da membrana | 1,05 V → 0,079 V | `Cmem` de 25 fF a 400 fF (16×), `Iin` = 10 pA |
| Variação de f com `Cmem` | ~14% pico-a-pico | denominador = f em `Cmem` = 100 fF; `Cmem` variado 16× |

---

## 5 · Ressalvas abertas sobre a etapa 0 (ler antes de citar qualquer número acima)

Estes pontos foram levantados em 2026-09-06 ao reler os resultados. **Nenhum foi
resolvido.** Não propague os números da §4 como definitivos sem fechá-los.

1. **A reprodutibilidade numérica do próprio simulador é de ~10%, e não foi medida.**
   O mesmo circuito, com parâmetros nominais idênticos (`Cmem` 100 fF, `Iin` 10 pA,
   `VDD` 1,8 V), aparece com três valores em três experimentos: **158 Hz** (EXP1,
   `tstep` 2 µs), **≈175 Hz** (EXP2, ponto de 10 pA da curva f–I, `tstep` 3 µs) e
   **≈166 Hz** (EXP3/EXP4, ponto nominal, `tstep` 3 µs). Os dois últimos foram lidos da
   figura, não dos dados brutos (perdidos). A diferença acompanha `tstep`/`tstop`, o que
   aponta para erro de integração numérica, não física. **Ação: estudo de convergência de
   `tstep` antes de qualquer número da etapa 1.**

2. **O "quase plano" do painel 4 tem estrutura que provavelmente é ruído numérico.**
   A varredura de `Cmem` dá 176 / 168 / 166 / 153 / 172 Hz para 25 / 50 / 100 / 200 / 400 fF —
   não-monotônica, com 14% de espalhamento, apenas ~1,4× acima da irreprodutibilidade do
   item 1. A conclusão qualitativa (`Cmem` não controla f) sobrevive folgadamente: 16× de
   capacitor para 14% de frequência. Mas a *forma* da curva não é resultado.

3. **A linearidade da curva f–I foi afirmada, nunca medida.** `scripts/plots.py` imprime
   a string literal `(linear, R² alto)` — o R² **nunca é calculado**. Além disso o ajuste é
   dominado pelos pontos de corrente alta: com intercepto de +6,5 Hz, a reta prevê 181 Hz
   em 10 pA contra 158 Hz medidos (13% abaixo da reta). **Ação: calcular R² e resíduos, e
   ajustar em escala log-log para não deixar os pontos de 50–100 pA mandarem no ajuste.**

4. **O modelo analítico da §3 acerta as tendências e erra o valor absoluto por 1,76×.**
   `T = Cfb·VDD/Iin` prevê 278 Hz em 10 pA; mediu-se 158 Hz. Mas o modelo acerta a
   independência de `Cmem` (painel 4), acerta a proporcionalidade a `Iin` (painel 3) e
   acerta a escala com VDD: prevê 186 → 152 Hz de 1,62 a 1,98 V, mediu-se 186 → 156 Hz.
   Um fator multiplicativo constante está faltando — provavelmente o *overshoot* da saída
   acima de VDD (visível no painel 1, ~1,9 V) mais o *undershoot* do reset, que juntos
   alargam a janela de histerese. **Ação: medir a janela de histerese diretamente
   (V de disparo menos V de reset) em vez de inferi-la.**

5. **Hipótese que pode explicar 1, 2 e 3 de uma vez: `abstol`.** O padrão do ngspice é
   `abstol = 1e-12 A = 1 pA` — e a etapa 0 rodou com `Iin` de 1 a 100 pA, sem nenhum
   `.options`. No ponto de 1 pA da curva f–I, a corrente de sinal inteira cabe dentro da
   tolerância de convergência do simulador; no ponto nominal de 10 pA, a tolerância vale
   10% do sinal — a mesma ordem do espalhamento do item 1. O `gmin` padrão (1e-12 S) soma
   mais ~0,9 pA de condutância parasita no nó `mem`. **Não testado** (ngspice não está
   instalado aqui). É o passo 1.0 da etapa 1, antes de qualquer PDK, porque custa minutos.
   **Se confirmado, vira regra permanente:** nenhum número de corrente sub-limiar deste
   projeto é válido sem `abstol` apertado.

6. **Limitações já reconhecidas no dossiê §4.4** (sem modelo sub-limiar, sem variação de
   fabricação, sem parasitas de layout) permanecem. A #1 é o objeto da etapa 1.

---

## 6 · Decisões tomadas — não reabrir sem motivo novo

| Data | Decisão | Motivo |
|---|---|---|
| 2026-09 | **Um chip homogêneo, replicado** — não chips especializados por modalidade | O gargalo real é a comunicação entre chips; a proporção entre modalidades é desconhecida e chips fixos a travam cedo demais; três máscaras custam três vezes mais. Mesma escolha de Loihi, SpiNNaker e Akida. Exceção legítima: a interface analógica de sensor é específica por modalidade e vai num chip pequeno separado. |
| 2026-09 | **Topologia axon-hillock** (Mead, 1989), 7 transistores | Base histórica validada; simples o bastante para ser entendida por inteiro antes de complicar. |
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

Acréscimos ao passo 4 (mesmo commit):

9. §4, linha "Excursão da membrana": os valores 1,05 V → 0,079 V foram lidos de
   figura. As medidas corretas, com tolerâncias apertadas, são 1,43 V → 0,107 V
   para Cmem de 25 fF a 400 fF. O colapso é MAIS severo que o registrado.

10. §3, "Impacto na área do chip": corrigir. Cmem pode encolher, mas quem fixa a
    frequência é Cfb, que NÃO pode encolher sem alterar o ganho f-I. A área do
    neurônio continua dominada por um capacitor — o outro. A economia é menor
    que "o neurônio pode ser mais compacto que o previsto" sugere.

11. §6, decisão "Topologia axon-hillock": marcar como EM REVISÃO, com o motivo:
    consumo medido de 12,6 uW por neurônio, 7e5 vezes a potência do sinal, por
    curto-circuito permanente no primeiro inversor. Decisão de manter ou trocar
    depende do experimento de limitação de corrente. Não remover a decisão da
    tabela — marcá-la.

12. §5 item 3, a ação proposta: o ajuste log-log testa se o expoente é 1, mas não
    representa deslocamento da reta, que é o que revelaria zona morta. Registrar
    que são necessários os DOIS ajustes: log-log para o expoente, linear com
    intercepto livre para a zona morta.