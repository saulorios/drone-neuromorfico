# Previsões pré-registradas — o pulso aciona o estágio seguinte?

Escritas em 2026-09-07, **antes** de rodar. Commitadas antes da medida.

**Pergunta:** o pulso serve para acionar o estágio seguinte sem criar curto novo?

**Regra desta rodada:** nenhuma âncora em constante do nível 1. Toda previsão abaixo se
apoia ou em grandeza já **medida no sky130**, ou em raciocínio de topologia.

---

## 1 · Dimensões do inversor receptor, e por quê

> `XRn out_r out 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.5`
> `XRp out_r out vddL vddL sky130_fd_pr__pfet_01v8 W=2 L=0.5`

**Razão da razão 2:1.** É a mesma proporção dos inversores do neurônio. Como a mobilidade do
buraco é ~3× menor que a do elétron neste nó, 2:1 **não** centra o ponto de transição em
VDD/2 — deixa o NMOS mais forte e o ponto de transição **abaixo** da metade. Isso é
deliberado e favorável aqui: `out` fica parado em **baixo** a maior parte do tempo (o spike é
breve), e um ponto de transição baixo dá mais margem para o nível alto do pulso, que é
justamente o nível sob suspeita.

**Razão de L = 0,5 µm.** Mesmo argumento das outras dimensões do projeto: 3,3× o mínimo,
o que reduz fuga e melhora casamento. Como a grandeza medida nesta rodada é **corrente
estática do receptor**, usar canal mínimo inflaria artificialmente o número que se quer
medir. Velocidade não é restrição: o circuito opera em centenas de hertz.

**Alimentação própria (`vddL`)** para medir a corrente do receptor separada da do neurônio.

## 2 · O nível baixo de `out` — o número que falta

Não foi medido em rodada alguma. Previsão por topologia: quando `n1` está alto, `M2p` tem
`Vsg = VDD − n1`. Já está medido no sky130 que **`n1` chega a 1,800 V**, o trilho — logo
`Vsg(M2p) = 0` e o PMOS está desligado sem ambiguidade, restando só `M2n` puxando para o
terra contra fuga.

> **Previsão: `out` baixo entre 0 e 5 mV.** Essencialmente o trilho.

Se der acima de ~50 mV, há um caminho de corrente que eu não identifiquei, e a análise do
receptor muda.

## 3 · Comutação do receptor

Já medido no sky130: `out` alto = **1,599 V**, `out` baixo previsto ≈ 0 V.
O ponto de transição do receptor 2:1 deve cair **abaixo** de VDD/2 = 0,9 V.

> **Previsão: comuta limpo nos dois sentidos.** Margem de ruído alta ≥ 0,6 V (de 1,599 V até
> o ponto de transição) e margem baixa ≥ 0,7 V. A saída do receptor deve excursionar
> **trilho a trilho**, 0 a 1,8 V — o receptor não tem espelho limitando corrente, ao
> contrário do 2º estágio do neurônio.

## 4 · A corrente estática do receptor — a pergunta central

**Com `out` parado em BAIXO (≈ 0 V):** o NMOS do receptor tem `Vgs` = 0 e está cortado; o
PMOS está totalmente ligado. A corrente estática é a **fuga do NMOS cortado**. Âncora medida
no sky130 nesta etapa: um nfet W=0,5 L=2 com a porta em 0 V e `Vds` = 1,8 V conduz **84,7 fA**.
O receptor tem W=1 L=0,5, isto é, W/L 8× maior, e a fuga sub-limiar escala com W/L:

> **Previsão: 0,3 a 2 pA.** Centro ~0,7 pA.

**Com `out` parado em ALTO (1,599 V):** o NMOS está fortemente ligado; o PMOS tem
`Vsg = 1,800 − 1,599 = 201 mV`. A pergunta é se 201 mV bastam para o PMOS conduzir. Âncora
medida no sky130 nesta etapa: a inclinação sub-limiar medida é **91,3 mV/década**. Se o
`|V_th|` do pfet estiver entre 0,6 e 0,9 V, `Vsg` = 201 mV o coloca de **4,4 a 7,7 décadas**
abaixo do limiar. Tomando ~100 nA como corrente de limiar para W/L = 4:

> **Previsão: 2 fA a 4 pA** — faixa larga de propósito, porque depende exponencialmente de um
> `|V_th|` que ainda não medi. Centro geométrico ~90 fA.

**Ambos os casos, em potência:** com 1,8 V, 4 pA são **7,2 pW**, ou **0,12%** dos 6,03 nW do
neurônio.

> **Previsão de veredito: DESPREZÍVEL.** Espero corrente estática do receptor abaixo de
> **1% dos 6,03 nW** (isto é, abaixo de 60 pW, ou 33 pA) nos dois estados.

## 5 · Critério e gatilho de parada

**Critério de aprovação:** corrente estática do receptor desprezível perto dos 6,03 nW do
neurônio. Fixo o limiar em **≤ 1% de 6,03 nW = 60 pW = 33 pA** em qualquer dos dois estados.

**Gatilho de parada — reporto e paro se:**
- a corrente estática do receptor passar de **60 pW** em qualquer estado. Se isso acontecer,
  o curto migrou de novo, um estágio adiante, e o problema é o **nível de `out`**, não o
  receptor;
- o receptor não comutar em algum dos dois sentidos;
- a saída do receptor não excursionar trilho a trilho.

**O que NÃO faria** sem falar antes: mudar as dimensões do receptor para "consertar" o
número, ou mexer no neurônio. Se o nível de `out` for insuficiente, isso é resultado.

## 6 · O que falsifica minha análise

Se a corrente com `out` alto vier **muito maior** que com `out` baixo, o PMOS do receptor
está conduzindo de verdade e o `|V_th|` do pfet é menor do que suponho — nesse caso os
201 mV de folga são o problema real, e o pulso do neurônio precisa subir. Esse é o desfecho
que eu considero menos provável, e é o que o experimento existe para descartar.
