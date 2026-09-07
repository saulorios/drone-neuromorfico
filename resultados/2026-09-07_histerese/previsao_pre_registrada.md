# Previsão pré-registrada — a janela de histerese varia com `Iin`?

Escrita em 2026-09-07, **antes** de rodar. Commitada antes da medida.

**Pergunta, com duas funções:** a janela de histerese, medida diretamente, varia com `Iin`?
Fecha o critério 4 da etapa 0 — medir `V` de disparo menos `V` de reset em vez de inferir — e
testa a minha hipótese nova para a curvatura da f–I.

---

## 1 · O alvo quantitativo

| parcela | valor |
|---|---|
| f/`Iin` em 1 pA | 13,605 Hz/pA |
| f/`Iin` em 10 pA | 13,958 Hz/pA |
| desvio observado | **−2,53%** |
| o que a fuga empurra no sentido contrário (§ fuga, medida DC) | **+1,62%** |
| **falta explicar** | **−4,15%** |

Para a janela explicar isso, ela precisa ser **4,15% MAIOR em 1 pA do que em 10 pA**.

## 2 · A previsão principal, e ela é desconfortável

> **Previsão: a janela NÃO vai explicar o desvio. Espero variação abaixo de 2% entre 1 e
> 100 pA, e considero mais provável que ela varie no sentido ERRADO — crescendo com `Iin`,
> não caindo.**

Registro isto sabendo que contraria a hipótese que eu mesmo levantei na rodada passada. Os
mecanismos que consigo nomear apontam todos na direção contrária:

**(a) O atraso do primeiro inversor cresce com `Iin`, não com a lentidão.** `n1` tem sua
corrente limitada a `IB1` = 10 nA pelo espelho, então sua taxa de variação tem teto. Com a
rampa lenta (1 pA), `n1` acompanha quase estaticamente; com a rampa rápida (100 pA), `n1`
fica para trás e `mem` precisa subir **mais** antes de a saída comutar. Isso faz a janela
**crescer com `Iin`** — o oposto do necessário.

**(b) A profundidade do undershoot já foi medida e não varia.** `mem` mínimo é −0,128 V em
`Iin` = 1 pA e −0,128 V em 10 pA e −0,128 V em 100 pA (dados da migração). O fundo da janela
é fixado pelo degrau de `Cfb`, que não depende de `Iin`.

**(c) A recuperação do undershoot é dominada pela injeção de junção, não por `Iin`.** Em
−0,127 V a junção injeta 3,7 pA. Em `Iin` = 1 pA isso é 3,7× a corrente de entrada, e o
trecho negativo é atravessado depressa **independentemente** de `Iin` — o que, se algo,
encurta a janela efetiva em corrente baixa.

**(d) Um tempo morto fixo por ciclo teria o sinal errado.** Se houvesse uma duração fixa de
spike somada ao período, ela pesaria 10× mais em 10 pA do que em 1 pA, fazendo o ponto de
1 pA parecer **mais rápido**, não mais lento.

## 3 · O que isso implica, se eu estiver certo

**Não vou forçar o ajuste.** Se a variação da janela não for da ordem de 4%, digo que a causa
é outra e paro, como instruído. Nesse caso a curvatura da f–I em corrente baixa fica **em
aberto com duas hipóteses derrubadas** — a fuga, na rodada passada, e a janela, nesta.

Candidatos que sobrariam, para rodadas futuras e **não investigados aqui**: dependência de
`Ctot` com a tensão de membrana através das capacitâncias de junção e de porta (que são
não-lineares e percorrem a mesma faixa, mas com tempos de resposta diferentes conforme a
velocidade da rampa); e a possibilidade de o desvio de −2,53% estar dentro do próprio erro do
ajuste da f–I, e não ser um efeito físico.

## 4 · Os números que espero medir

Ponto nominal (`Iin` = 10 pA), do que já está medido na migração:

> **`V` de disparo: 0,50 a 0,57 V.** O disparo DC ocorre em 0,45 V; em operação a
> realimentação empurra além. Reporto `V(mem)` no instante em que `out` cruza 0,9 V.
> **`V` mínimo após o reset: −0,128 V**, praticamente sem variação com `Iin`.
> **Janela: 0,63 a 0,70 V.**

## 5 · O fator de 1,76× da etapa 0 — sobrevive ao PDK?

O modelo `T = Cfb·VDD/Iin` prevê 3,60 ms em `Iin` = 10 pA, isto é, **277,8 Hz**. Medido:
139,58 Hz. **O fator já está em 1,99× no sky130**, contra 1,76× no nível 1.

Em termos de janela, com `Ctot` estimado entre 120 e 132 fF (os 120 fF ideais mais 6 a 12 fF
de porta e junção):

| base do modelo | ΔV previsto | contra a janela observada de ~0,693 V |
|---|---|---|
| `VDD·Cfb/Ctot`, Ctot = 132 fF | 0,273 V | **2,54×** |
| excursão real de `out` (1,624 V), Ctot = 132 fF | 0,246 V | **2,82×** |

> **Previsão: o fator sobrevive e é maior no sky130.** Espero a janela medida entre **2,3× e
> 2,9×** o que `Cfb·VDD/Ctot` prevê. Vou medir `Ctot` diretamente pela inclinação da rampa
> (`Ctot = Iin / (dV/dt)`) em vez de estimá-la, o que torna a comparação uma medida e não uma
> conta com parâmetro suposto.

## 6 · Método

Da **forma de onda**, não de modelo. Para `Iin` = 1, 3, 10, 30, 100 pA, transiente com
tolerâncias apertadas e passo fino, medindo por ciclo:

- `V(mem)` no instante em que `out` cruza 0,5·VDD — a tensão de disparo;
- o mínimo de `V(mem)` no ciclo — o fundo após o reset;
- a diferença — a janela;
- a inclinação `dV/dt` no trecho central da rampa — de onde sai `Ctot` medido.

Média sobre ciclos inteiros, descartando os primeiros 20%, com o desvio entre ciclos
reportado para separar variação real de ruído numérico.
