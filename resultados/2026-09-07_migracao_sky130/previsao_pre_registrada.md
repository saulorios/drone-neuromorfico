# Previsões pré-registradas — migração do neurônio para o sky130

Escritas em 2026-09-07, **antes** de rodar a migração. Commitadas antes da medida.

**Pergunta da rodada:** o neurônio migrado para o sky130 reproduz o comportamento do
nível 1?

---

## 1 · Dimensões: escolhi NÃO mudar nenhuma. Por quê.

Todas as sete dimensões em uso são **legais no sky130** (mínimos: W = 0,42 µm, L = 0,15 µm):

| dispositivo | tipo | W (µm) | L (µm) | L em múltiplos do mínimo |
|---|---|---|---|---|
| `Mref1` / `Mbp1` | PMOS | 0,50 | 10,0 | 66,7× |
| `M1p` | PMOS | 2,00 | 0,50 | 3,3× |
| `M1n` | NMOS | 1,00 | 0,50 | 3,3× |
| `Mref2` / `Mbp2` | PMOS | 5,00 | 1,00 | 6,7× |
| `M2p` | PMOS | 4,00 | 0,50 | 3,3× |
| `M2n` | NMOS | 2,00 | 0,50 | 3,3× |
| `Mrst` | NMOS | 0,50 | 2,00 | 13,3× |

**Razão principal — a pergunta é uma comparação.** "Reproduz o comportamento do nível 1?"
só tem resposta se **uma** coisa mudar entre as duas simulações: o modelo do dispositivo.
Mudar dimensão junto torna qualquer diferença inatribuível. Redimensionar é uma pergunta
diferente, para outra rodada.

**Razão de mérito próprio — L = 0,5 µm não é uma escolha ruim, mesmo tendo sido arbitrária.**
O mínimo do processo é 0,15 µm, e ir até lá seria **ativamente errado** aqui. Os dois riscos
dominantes deste projeto são descasamento (etapa 2, o maior risco do projeto) e fuga térmica
(a tesoura, §5 do `CLAUDE.md`). Canal mais longo melhora os dois: o descasamento de `V_th`
escala com 1/√(W·L), e a fuga cai com L por menos DIBL. Canal mínimo compra velocidade, que
é justamente o que este circuito não precisa — ele opera em centenas de hertz.

**O que fica pendente:** L = 0,5 µm continua sendo um número que ninguém otimizou. A
afirmação aqui é só que ele é **legal e defensável**, não que seja **ótimo**. Otimizar exige
saber a resposta da etapa 2, e não é esta rodada.

## 2 · Base de comparação — corrente de acionamento já medida

Único dado de sky130 que tenho, do transistor isolado (Vgs = Vds = 1,8 V, `tt`, 27 °C):

| dispositivo | nível 1 (analítico) | sky130 (medido) | razão |
|---|---|---|---|
| `M1n` (W=1, L=0,5) | 242,3 µA | 225,5 µA | **0,93** |
| `Mrst` (W=0,5, L=2) | 30,3 µA | 33,6 µA | **1,11** |

Os modelos nível 1 estavam **razoavelmente calibrados em inversão forte** — erram por 7 a
11%, não por ordens de grandeza. É isso que sustenta as previsões abaixo.

## 3 · As previsões numéricas

Ponto nominal: `IB1` = 10 nA, `IB2` = 3 µA, `Iin` = 10 pA, canto `tt`, `.temp 27`,
`Cmem` = 100 fF e `Cfb` = 20 fF ideais.

### Frequência

Nível 1 dá **138,3 Hz**. O período é dominado por `T = Cfb·VDD/Iin`, que é capacitivo e não
depende do modelo do transistor, mais a parcela de reset incompleto, que depende. Como
`Mrst` é **11% mais forte** no sky130, o reset fica mais completo, a membrana desce mais, a
rampa fica mais longa e a frequência **cai**.

> **Previsão: 60 a 200 Hz, centrada em ~110 Hz.**

### Ganho f–I

A curva deve continuar passando pela origem, então o ganho segue a frequência:

> **Previsão: 6 a 20 Hz/pA, centrada em ~11 Hz/pA.** (Nível 1: 13,79.)

### Consumo no ponto nominal

Nível 1 dá **85,4 nW** (80,9 estático + 4,5 de atividade). Duas forças opostas:

- **Para cima:** o sky130 tem condução sub-limiar, que o nível 1 **não tem**. Aparece uma
  corrente estática que antes era exatamente zero.
- **Para baixo / contida:** a fome de corrente **limita por construção**. O caminho DC de
  `vdd` ao terra passa pelo PMOS espelhado, então a corrente de curto do inversor está
  presa em `IB`, seja qual for o modelo. `P1 ≤ 10 nA × 1,8 V = 18 nW` e
  `P2 ≤ 3 µA × 1,8 V = 5,4 µW`, com o valor real definido pela duração da travessia.

Aposto que a limitação vence, mas com margem menor:

> **Previsão: 60 a 250 nW, centrada em ~110 nW.** Se passar de 250 nW, a contribuição
> sub-limiar é maior do que estimei e o orçamento de 100 nW volta a estar em risco.

### Zona morta

A fuga do `Mrst` medida é 84,7 fA (limite superior, em `Vds` = 1,8 V). Contra 1 pA são 8,5%.

> **Previsão: zona morta implícita da ordem de 50 a 150 fA — não detectável como zona morta
> dura.** O ponto de 1 pA deve ficar alguns por cento abaixo da reta. R² ainda ≥ 0,999.

---

## 4 · O discriminador: migração falhou, ou o circuito mudou?

Esta é a parte que importa. **O critério é a rede de polarização**, porque ela é o que a
migração pode quebrar sem quebrar a simulação.

### Diria MIGRAÇÃO FALHOU se:

1. **A simulação abortar ou algum dispositivo cair fora do bin** do modelo. É fail-stop,
   como já verificado na rodada anterior.
2. **Os espelhos não entregarem a corrente programada.** Verificação direta: com o
   dispositivo em saturação, `I(Mbp1)` deve ser ≈ 10 nA e `I(Mbp2)` ≈ 3 µA. **Se algum
   estiver fora por mais de 2×, a migração falhou** — o espelho 1:1 depende de o par
   referência/saída ter as mesmas dimensões, e é aí que uma tradução errada aparece.
3. **Algum nó de polarização violar os trilhos** (`sp1`, `sp2`, `rp1`, `rp2` fora de
   0 a 1,8 V).
4. **`rp1` e `rp2` ficarem longe do previsto analiticamente.** Para PMOS em ligação diodo,
   `V(rp) = VDD − (|V_th| + V_ov)`. Com o `V_th` do sky130 diferente do nível 1 espero
   deslocamento, mas não mais que ~300 mV.
5. **O neurônio não oscilar E a polarização estiver errada** por um dos itens acima.

### Diria que O CIRCUITO MUDOU (resultado legítimo, não falha) se:

- A polarização estiver **toda correta** pelos critérios acima, e ainda assim a frequência,
  o ganho ou o consumo saírem fora das faixas previstas. Aí o que mudou foi a física do
  dispositivo, que é exatamente o que a etapa 1 existe para descobrir.
- O neurônio não oscilar **com a polarização correta** — seria achado real e grave, não erro
  de migração.

**Em uma frase:** se a rede de polarização entrega o que foi pedido e os nós estão onde a
teoria diz, qualquer diferença restante é do circuito. Se a polarização está errada, nada
mais do que eu medir vale.

## 5 · Gatilhos de parada (reportar sem redimensionar)

Conforme instruído, paro e reporto sem mexer em dimensão se:

- **Zona morta dura:** o neurônio não disparar em `Iin` = 1 pA, ou zona morta implícita
  acima de 500 fA.
- **Perda de linearidade:** R² < 0,999 no ajuste de intercepto livre, ou expoente log–log
  fora de 0,95 a 1,05.
- **Consumo estourando:** acima de **171 nW** no ponto nominal, isto é, 2× o valor de
  nível 1.
- **Pulso de saída** abaixo de 90% de VDD.
