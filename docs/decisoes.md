# Log de decisões

Uma linha por decisão, com data e motivo. Daqui a meses, a razão do descarte é mais
valiosa que o descarte. Ordem cronológica inversa (mais recente no topo).

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
