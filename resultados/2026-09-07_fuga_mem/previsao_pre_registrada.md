# Previsão pré-registrada — a fuga no nó `mem`, medida diretamente

Escrita em 2026-09-07, **antes** de rodar. Commitada antes da medida.

**Pergunta:** a fuga no nó `mem`, medida diretamente, confirma os 25,3 fA inferidos da curva
f–I?

---

## As duas âncoras que já tenho

| medida | valor | condição |
|---|---|---|
| `Mrst` isolado (W=0,5, L=2), porta em 0 V | **84,7 fA** | `Vds` = 1,8 V, muito acima da operação |
| fuga efetiva inferida da curva f–I | **25,3 fA** | valor único, médio ao longo da rampa |
| inclinação sub-limiar medida neste PDK | 91,3 mV/década | — |
| excursão de `mem` em operação | −0,127 a 0,562 V | ponto nominal |

Os 84,7 fA e os 25,3 fA diferem por **3,3×**, e a hipótese registrada é que a diferença é
`Vds`: o transistor isolado foi medido em 1,8 V, e `mem` nunca passa de 0,562 V.

## A forma esperada da curva

Dois mecanismos governam, e agem em faixas diferentes de `V(mem)`:

**1. Supressão em `Vds` pequeno.** A corrente sub-limiar carrega o fator
`(1 − e^{−Vds/V_T})`, com `V_T` = 25,9 mV. Isso obriga a fuga a **passar por zero em
`mem` = 0** e a saturar rápido:

| V(mem) | fator | |
|---|---|---|
| 10 mV | 0,32 | ainda muito suprimido |
| 26 mV | 0,63 | |
| 78 mV | 0,95 | praticamente saturado |
| ≥ 150 mV | 1,00 | o fator deixa de importar |

**2. DIBL acima disso.** Passados ~150 mV, a fuga volta a crescer devagar com `Vds`, por
redução de barreira. Para `L` = 2 µm — 13× o mínimo — o DIBL é fraco, tipicamente 10 a
20 mV/V. Entre `mem` = 0,562 V e `Vds` = 1,8 V isso dá 12 a 25 mV de deslocamento de `V_th`,
que a 91,3 mV/década vale um fator de **1,37× a 1,87×**.

> **Previsão da forma:** curva monotônica, **zero em `mem` = 0**, subindo íngreme até
> ~100–150 mV, e daí em diante quase plana, com crescimento suave por DIBL. **Não** um
> patamar único.

## Os números

Partindo dos 84,7 fA a `Vds` = 1,8 V e dividindo pelo fator DIBL:

> **No topo da excursão (`mem` = 0,562 V): 45 a 62 fA**, centro **~53 fA**.
> **No meio da rampa (`mem` ≈ 0,25 V): 40 a 58 fA**.
> **Em `mem` = 0: exatamente 0 fA** (nenhum viés).
> **Média ponderada no tempo ao longo da rampa: 35 a 55 fA**, centro **~45 fA**.

## O veredito que espero

> **Confirmação parcial: mesma ordem de grandeza, mas os 25,3 fA ficam baixos por ~1,5 a
> 2×.**

Razão: a rampa é linear no tempo, então `mem` passa tempo aproximadamente igual em cada
tensão. Como o fator de supressão só morde abaixo de ~100 mV — que é uma fração pequena da
excursão de 0,69 V — a média deve ficar **perto do patamar**, não a meio caminho entre zero e
o patamar.

**Se eu estiver certo, a tesoura precisa de correção modesta.** Com 45 fA em vez de 25,3, o
fator até 1 pA cai de 39,5 para 22,2, isto é, 0,83 duplicação a menos — as temperaturas de
cruzamento **descem 7 a 8 °C**. O cruzamento de 1 pA sairia de 69–80 °C para ~61–72 °C.
Muda a margem, não a conclusão.

## O que me faria dizer que estou errado

- **Se a fuga medida for próxima de 25 fA no patamar**, minha estimativa de DIBL está alta
  demais e o valor único usado na projeção está correto como está.
- **Se a fuga variar mais de 3× ao longo da excursão útil** (acima de 150 mV), aí o valor
  único é inadequado por construção e a tesoura precisa ser reprojetada com a curva inteira,
  não com um número.
- **Se a fuga não passar por zero em `mem` = 0**, há um caminho de corrente que não é o
  `Mrst` e que eu não identifiquei — provavelmente corrente de porta de `M1n`/`M1p`, que
  estou supondo desprezível.

## Método

Ponto de operação **DC**, conforme a convenção do `CLAUDE.md` §7 estabelecida nesta mesma
data — corrente estática nunca por média de transiente. `mem` forçado por fonte de tensão,
varrido ao longo da faixa de operação; a corrente na fonte é a fuga líquida que o nó vê.
O circuito fica no estado de integração (`out` baixo) enquanto `mem` estiver abaixo do ponto
de disparo; onde ele virar, a medida deixa de valer e será reportada como tal.
