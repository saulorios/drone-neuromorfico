# Fome de corrente com conformidade finita — o testbench REPROVA a validação

Data: 2026-09-06 · **ngspice 41** (`ngspice --version`) · modelos nível 1
(`generic_l1.mod`), inalterados · netlist derivado de `spice/neuronio.cir` com o bloco
`.options` obrigatório.

**Resultado: os sweeps 1 e 2 não foram executados.** O critério de validação do
testbench, a conferir antes de olhar potência, reprovou. Conforme combinado, parei aqui.

---

## O que foi montado

Cada fonte de corrente ideal ganhou um resistor em paralelo:

```spice
Ibp vdd1 sp1 DC {IB}      Rp  sp1  vdd1 {R}
Ibn sn1  0   DC {IB}      Rn  sn1  0    {R}
```

com `R = 0,3 V / IB`, para ~0,3 V de queda com o transistor cortado:

| IB | 1 nA | 10 nA | 100 nA | 1 µA |
|---|---|---|---|---|
| R | 300 MΩ | 30 MΩ | 3 MΩ | 300 kΩ |

`Rp` e `Rn` são **elementos de bancada, não de projeto**. Nenhum chip integraria 30 MΩ;
existem só para dar conformidade finita a uma fonte idealizada.

Não foram alterados `Cmem` (100 fF), `Cfb` (20 fF), `Wrst` (0,5 µm) nem a dimensão de
nenhum transistor. `Iin` = 10 pA, `tstop` = 100 ms, `tstep` = 0,5 µs.

---

## A · Validação — reprova nos dois critérios de trilho

Exigido: `sp1` ≤ 1,8 V, `sn1` ≥ 0 V em toda a simulação, e `n1` de volta a ~0,12–1,8 V.
Medido sobre os últimos 80% de cada corrida:

| IB | sp1 (V) | | sn1 (V) | | n1 (V) | f (Hz) |
|---|---|---|---|---|---|---|
| | min..máx | veredito | min..máx | veredito | min..máx | |
| — (base) | — | — | — | — | 0,121..1,800 | 160,37 |
| 1 nA | 0,783..**2,039** | **VIOLA** por 239 mV | **−0,350**..0,435 | **VIOLA** por 350 mV | 0,829..2,039 | 79,37 |
| 10 nA | 0,840..**2,075** | **VIOLA** por 275 mV | **−0,349**..0,419 | **VIOLA** por 349 mV | 0,840..2,075 | 77,13 |
| 100 nA | 0,928..**1,992** | **VIOLA** por 192 mV | **−0,237**..0,401 | **VIOLA** por 237 mV | 0,862..1,992 | 109,51 |
| 1 µA | 1,098..**1,954** | **VIOLA** por 154 mV | **−0,192**..0,357 | **VIOLA** por 192 mV | 0,833..1,952 | 127,97 |

`n1` também não voltou: continua em ~0,83–2,04 V em vez de 0,12–1,80 V. O piso de 0,83 V
segue dentro da janela de condução do 2º inversor (0,45–1,35 V), que era exatamente o
problema que a correção pretendia eliminar.

Comparação com o testbench anterior, de fontes ideais puras (`sp1` máx. 2,139 V,
`sn1` mín. −0,362 V): a violação **diminuiu de ~340 mV para ~280 mV**, mas não sumiu.
Trocou o grampo de diodo de corpo por um grampo resistivo, num valor próximo.

---

## B · Por que — a violação é estrutural, não de dimensionamento

Uma fonte de corrente ideal em paralelo com um resistor **é uma fonte de Norton**. Seu
equivalente de Thévenin visto de `sp1` é uma fonte de tensão de `IB·R` **em série** com
`R`, orientada para **cima** de `vdd1`:

```
V(sp1) em circuito aberto = vdd1 + IB·R = 1,8 + 0,3 = 2,1 V
```

Com M1p cortado, `IB` não tem para onde ir senão voltar por `Rp` até `vdd1`, e para isso
`sp1` **precisa** estar acima de `vdd1`. Simetricamente, `sn1` precisa estar abaixo de 0 V
para que a corrente venha do terra por `Rn`.

| IB | sp1 previsto | sp1 medido | sn1 previsto | sn1 medido |
|---|---|---|---|---|
| 1 nA | 2,100 V | 2,039 V | −0,300 V | −0,350 V |
| 10 nA | 2,100 V | 2,075 V | −0,300 V | −0,349 V |
| 100 nA | 2,100 V | 1,992 V | −0,300 V | −0,237 V |
| 1 µA | 2,100 V | 1,954 V | −0,300 V | −0,192 V |

Previsão e medida batem dentro de ~10% (as diferenças vêm de M1p/M1n nunca cortarem por
completo). **A conclusão não depende do valor de R:** para `sp1 ≤ vdd1` seria preciso
`IB·R ≤ 0`, ou seja, `R = 0`. Qualquer resistor positivo viola. Não é erro de
dimensionamento — é a topologia do grampo.

### E há um segundo problema, independente do primeiro

Quando o transistor **conduz**, `sp1` cai, e o resistor passa a injetar `(vdd1 − sp1)/R`
**em paralelo** com a fonte:

| IB | I pelo resistor, média | ÷ IB | I pelo resistor, pico | ÷ IB |
|---|---|---|---|---|
| 1 nA | 0,59 nA | 0,59× | 3,39 nA | **3,39×** |
| 10 nA | 5,98 nA | 0,60× | 32,02 nA | **3,20×** |
| 100 nA | 44,96 nA | 0,45× | 290,79 nA | **2,91×** |
| 1 µA | 355,46 nA | 0,36× | 2 338,90 nA | **2,34×** |

No pico, o resistor entrega **até 3,4× a corrente da própria fonte**. A limitação de
corrente — que é o objeto do experimento — **deixa de existir** justamente nos instantes
de transição, que é quando ela deveria atuar. Mesmo que a violação de trilho fosse
resolvida por outro meio, este dimensionamento de R não implementa fome de corrente.

Os dois efeitos são o mesmo trade-off visto de dois lados: `R` grande dá violação de
trilho grande (`IB·R`); `R` pequeno faz o resistor curto-circuitar a fonte. Não existe
`R` que satisfaça os dois.

---

## C · A verificação nova, sobre sensibilidade a IB

Pedida: a frequência **deve** variar com IB de forma apreciável.

| IB | 1 nA | 10 nA | 100 nA | 1 µA |
|---|---|---|---|---|
| f (Hz) | 79,37 | 77,13 | 109,51 | 127,97 |

A frequência agora **varia 1,66×** sobre 1000× de IB, contra 2% no testbench anterior.
Isso confirma o diagnóstico da rodada passada: a insensibilidade de antes era artefato dos
grampos de diodo. **Mas isso não valida o testbench** — a curva é não-monotônica (cai de
79,4 para 77,1 e depois sobe), e enquanto os nós de source violarem os trilhos não há como
atribuir a variação à polarização em vez de ao grampo resistivo.

---

## D · O que seria preciso para um testbench limpo

Registrado como diagnóstico, **não implementado** — a escolha é do autor do projeto.

A raiz do problema: uma fonte de corrente ideal é um *forçador* de corrente (passa
exatamente IB, sempre), enquanto o que a topologia precisa é um *limitador* (passa de 0 a
IB, conforme o circuito pedir). Um transistor de polarização é um limitador: com o
inversor cortado, ele fica com Vds ≈ 0 e o source encosta no trilho naturalmente.

Caminhos possíveis, todos com contrapartida:

1. **Transistor de polarização de verdade.** Resolve os dois problemas de uma vez. A
   objeção original — nível 1 não modela sub-limiar — vale para IB = 1 nA e 10 nA, mas em
   100 nA e 1 µA um MOSFET nível 1 opera em inversão forte, onde o modelo é razoável. Daria
   pelo menos os dois pontos altos da varredura sem artefato.
2. **Manter a fonte ideal e acrescentar um grampo** que impeça a ultrapassagem do trilho.
   Introduz um elemento não-físico a mais, e é preciso verificar que ele não conduz durante
   a operação normal.
3. **Aceitar a violação e medir só o que ela não contamina.** A potência do 1º estágio já
   é `IB·VDD` por construção e não depende do grampo; o que está contaminado é o 2º estágio.

---

## E · Pendências

1. **Os sweeps 1 e 2 não foram executados.** A pergunta original — o neurônio chega a
   ≤ 100 nW? — continua sem resposta com testbench validado.
2. **Continua aberta a divergência de 11% na potência da linha de base** entre a
   revalidação (ngspice 42, 12,6 µW) e este ambiente (ngspice 41, 13,99 µW). A convenção de
   registrar a versão em todo relatório foi acrescentada ao `CLAUDE.md` §7, mas as duas
   versões não foram comparadas lado a lado na mesma máquina.
3. **Tudo em modelos nível 1**, sem condução sub-limiar.
4. A linha de base neste testbench dá `n1` de 0,121 a 1,800 V e f = 160,37 Hz, batendo com
   a rodada anterior — o circuito não mudou, só o aparato de medida.

---

## Arquivos

- `validacao_testbench.png` — a figura (2 painéis)
- `raw/` — netlists `.cir` (caminhos relativos) e saídas brutas
- `../../scripts/run_conformidade.py` — testbench
- `../../scripts/plots_conformidade.py` — figura
