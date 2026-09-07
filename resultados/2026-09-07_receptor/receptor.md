# O pulso aciona o estágio seguinte sem criar curto novo — APROVA

Data: 2026-09-07 · **ngspice 42** · **sky130A**, canto `tt`, `.temp 27`
Neurônio: `IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA, dimensões inalteradas.
Receptor: inversor comum, `W` = 1 (NMOS) e `W` = 2 (PMOS), `L` = 0,5, alimentação própria
(`vddL`). Previsões em `previsao_pre_registrada.md`, commit `733afee`.

**Pergunta:** o pulso serve para acionar o estágio seguinte sem criar curto novo?

**Resposta: SIM, com folga de ~135×.** A corrente estática do receptor é **0,13 pA** com
`out` parado em baixo e **0,24 pA** parado em alto — 0,004% e 0,007% dos 6,03 nW do
neurônio, contra um limiar de aprovação de 1%.

---

## A · O nível baixo de `out` — o número que faltava

> **`out` baixo = 0,000 mV.** O trilho, dentro da resolução da medida (−1×10⁻⁷ V).

Previsão pré-registrada: 0 a 5 mV. **Confirmada.** O raciocínio se sustentou: `n1` alcança
1,800 V, o trilho, então `M2p` fica com `Vsg` = 0 e desliga sem ambiguidade, restando só
`M2n` puxando para o terra.

Isso importa porque **o nível baixo não é o problema** — se houvesse curto novo, viria do
nível alto, que é o degradado (1,624 V, 90,2% de VDD).

## B · Comutação — limpa nos dois sentidos

| grandeza | valor |
|---|---|
| `out` baixo → `outr` | 0,000 V → **1,800 V** |
| `out` alto (1,624 V) → `outr` | → **0,000 V** |
| excursão de `outr` | **1,8010 V = 100,1% de VDD** — trilho a trilho |
| ponto de transição do receptor | **0,730 V** |
| **margem de ruído alta** | 1,624 − 0,730 = **0,894 V** |
| **margem de ruído baixa** | 0,730 − 0,000 = **0,730 V** |
| tempo de subida de `out` (0,1 a 1,5 V) | 0,09 µs |
| tempo de descida de `out` (1,5 a 0,1 V) | 0,14 µs |

O ponto de transição caiu **abaixo** de VDD/2, como previsto para uma razão 2:1 num processo
onde a mobilidade do buraco é ~3× menor. Isso é favorável: sobra margem justamente para o
nível alto, que é o lado sob suspeita.

## C · A corrente estática — a resposta

Medida por **ponto de operação DC** com `out` forçado a cada nível. Sem integração no tempo,
portanto sem erro de integração.

| estado | `out` | I estática | Potência | % dos 6,03 nW |
|---|---|---|---|---|
| parado em BAIXO | 0,0000 V | **0,1325 pA** | 0,239 pW | **0,004%** |
| parado em ALTO | 1,6243 V | **0,2443 pA** | 0,440 pW | **0,007%** |
| (transição) | 0,725 V | 2,90 µA (pico) | — | só de passagem |

**Limiar de aprovação pré-registrado: 33 pA / 60 pW / 1%. Passa por ~135×.**

O pico de 2,90 µA existe, mas o receptor só o atravessa: `out` cruza a janela de crowbar em
**0,09 µs por ciclo**, ou 0,001% do período. Não há curto novo — há uma travessia rápida,
que é o comportamento normal de qualquer porta CMOS.

### Por que o nível alto degradado não cria curto

`out` alto = 1,624 V deixa o PMOS do receptor com `Vsg` = 1,800 − 1,624 = **176 mV**. Com a
inclinação sub-limiar de 91,3 mV/década medida neste PDK, isso põe o PMOS várias décadas
abaixo do limiar. Os 176 mV de folga são pequenos em tensão mas enormes em corrente, porque
a relação é exponencial. **O nível alto degradado é suficiente.**

## D · Correção de método — o transiente estava medindo o solver, não o circuito

**Isto quase virou um falso alarme meu.** A primeira medida, tirada da média do transiente,
deu **3,63 nW para o receptor — 60% do neurônio**, o que teria disparado o gatilho de parada
e produzido um relatório dizendo que o curto migrou.

Aplicando a Regra 1 antes de reportar, o número não sobreviveu:

| medida | I estática no mesmo ponto de operação |
|---|---|
| **DC (sem integração no tempo)** | **0,1325 pA** ← físico |
| transiente, `vntol` = 1e-9, `gmin` = 1e-15 | 1 607 pA — **12 128×** acima |
| transiente, `vntol` = 1e-12, `gmin` = 1e-18 | 428,3 pA — **3 232×** acima |

**O número cai quando aperto a tolerância, sem tocar no circuito.** É piso numérico.

As evidências que o denunciam, no trecho quieto (4 ms de rampa, `out` parado em 0 V):

- `v(outr)` fica **10 nV acima do trilho** de alimentação, o que é fisicamente impossível em
  regime;
- `i(vddL)` é **constante em +1682,63 pA**, com desvio padrão de 499 pA e 2,2% das amostras
  de sinal invertido;
- a razão entre os dois não corresponde a **condutância alguma do circuito** — 10 nV por
  1682 pA daria 6 Ω, que não existe em lugar nenhum deste netlist.

**Causa provável:** o ramo do receptor carrega **2,9 µA de pico** nas transições. Com
`reltol` = 1e-4, o critério de convergência daquele ramo admite erro absoluto da ordem de
`reltol × 2,9 µA ≈ 290 pA`, e é essa a resolução efetiva ali — não o `abstol` de 1 fA que eu
havia configurado. A corrente real, 0,13 pA, está **2 200× abaixo desse piso**.

**É o mesmo erro que fundou este projeto**, um nível abaixo. A regra do `CLAUDE.md` §7 dizia
que o `abstol` padrão é da ordem do sinal; aqui o `abstol` estava certo e quem manda é o
`reltol` aplicado à **maior corrente daquele ramo**, não à corrente que se quer medir.

**Convenção nova, registrada no `CLAUDE.md` §7:** corrente estática se mede por ponto de
operação DC, nunca por média de transiente.

## E · O critério funcional do pulso, aplicado

O critério de "≥ 90% de VDD" foi revogado nesta mesma data e substituído por três testes
funcionais (`CLAUDE.md` §7). Aplicando-os a este pulso:

| teste | evidência | veredito |
|---|---|---|
| 1. Chuta `Cfb` | excursão de 1,6243 V; o neurônio oscila em 139,7 Hz com CV do ISI na casa de 0,001% | **PASSA** |
| 2. Abre o gate do `Mrst` | o reset completa todo ciclo: `mem` volta a −0,127 V e a rampa recomeça | **PASSA** |
| 3. Lido como alto pelo estágio seguinte | margens de 0,894 V e 0,730 V, `outr` trilho a trilho, estática de 0,44 pW | **PASSA** |

**O pulso passa nos três.** Sob o critério antigo ele tinha reprovado por 1,16 pontos
percentuais. O circuito nunca esteve errado — o critério estava.

## F · O receptor perturbou o neurônio?

Pouco, e para melhor:

| grandeza | sem receptor | com receptor |
|---|---|---|
| frequência | 139,582 Hz | 139,727 Hz (+0,10%) |
| potência do neurônio | 6,030 nW | 6,337 nW (+5,1%) |
| `out` alto | 1,5990 V | 1,6243 V (+1,6%) |
| `mem` | −0,128 a 0,565 V | −0,127 a 0,562 V |

O acréscimo de 0,31 nW no neurônio é o custo de acionar a capacitância de porta do receptor,
e é real — deve entrar em qualquer orçamento de sistema, ao contrário dos 3,63 nW
descartados na §D, que eram artefato.

---

## G · Placar das previsões pré-registradas

| Previsão | Prevista | Medida | Veredito |
|---|---|---|---|
| `out` baixo | 0 a 5 mV | **0,000 mV** | **confirmada** |
| Comutação limpa, trilho a trilho | sim | `outr` 0 a 1,801 V | **confirmada** |
| Margens ≥ 0,6 V (alta) e ≥ 0,7 V (baixa) | — | 0,894 e 0,730 V | **confirmadas** |
| Ponto de transição abaixo de VDD/2 | sim | 0,730 V | **confirmada** |
| Estática com `out` baixo | 0,3 a 2 pA | **0,1325 pA** | **fora por 2,3×**, na direção conservadora |
| Estática com `out` alto | 2 fA a 4 pA | **0,2443 pA** | **dentro**, perto do centro geométrico |
| Veredito: desprezível (< 1%) | sim | 0,004% e 0,007% | **confirmada** |

Seis de sete. A que errei — a estática com `out` em baixo — errei **por excesso de cautela**:
supus que a fuga escalaria com W/L a partir do `Mrst` (W=0,5, L=2), mas o receptor tem
`L` = 0,5 e `V_th` diferente, e a extrapolação linear em W/L não vale entre comprimentos de
canal diferentes.

**O falsificador que eu havia definido não disparou.** Eu disse que, se a corrente com `out`
alto viesse muito maior que com `out` baixo, o `|V_th|` do pfet seria menor do que suponho e
os 176 mV de folga seriam o problema real. Vieram 0,24 contra 0,13 pA — mesma ordem. O
desfecho menos provável está descartado.

## H · Pendências

1. **A corrida de tolerância mais apertada** (`abstol` = 1e-18, `reltol` = 1e-6) **travou** em
   t = 0,00 ms. O terceiro ponto da série da §D não foi obtido. Os dois pontos existentes já
   estabelecem a tendência, mas o valor de convergência do transiente não foi determinado.
2. **`CloadR` = 5 fF na saída do receptor é arbitrário** — copiei do `Cload` do neurônio.
   O que vem depois do receptor define esse número de verdade.
3. **Um só receptor.** Fan-out maior multiplica a capacitância de porta e o custo de 0,31 nW
   da §F. Não medido.
4. **Só o canto `tt` a 27 °C.** A margem de ruído e a estática mudam com temperatura e canto;
   os 176 mV de folga do PMOS são o item a vigiar, por serem exponenciais.
5. **Nível 1 não entra aqui** — este experimento é todo sky130.

## Arquivos

- `receptor.png` — a figura (4 painéis)
- `previsao_pre_registrada.md` — commitado antes da medida
- `raw/neuronio_receptor.cir`, `raw/estatica_dc.cir`, `raw/tol_test.cir`
- `../../scripts/plots_receptor.py`
