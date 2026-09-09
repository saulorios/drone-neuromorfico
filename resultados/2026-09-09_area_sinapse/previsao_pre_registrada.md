# Pré-registro — área da sinapse e contagem real de neurônios por chip

Data: 2026-09-09 · **Sem simulação.** Levantamento no PDK + aritmética, com premissas
explícitas. **Escrito e commitado ANTES de qualquer cálculo ou leitura do PDK.**
Autor das previsões: Claude.

> A pergunta: quantos neurônios cabem em 10 mm² **depois** de contar as sinapses?
> O projeto vinha estimando contagem a partir da área do **neurônio** apenas. Numa rede,
> sinapses são muito mais numerosas, e uma sinapse com peso digital não é obviamente
> menor que um neurônio.

---

## O número que decide tudo: razão área_sinapse / área_neurônio

Denominador fixo: neurônio = **15,5 µm² ativos**, **150 a 300 µm² de layout**
(estimativa corrente do projeto, `docs/etapas.md` etapa 9).

**Previsão, por resolução de peso:**

| peso | transistores que eu espero | área de layout prevista | **razão sobre o neurônio (150–300 µm²)** |
|---|---|---|---|
| 1 bit | 6 a 12 | **15 a 35 µm²** | **0,05 a 0,23×** |
| 2 bits | 16 a 28 | **30 a 70 µm²** | **0,10 a 0,47×** |
| 4 bits | 40 a 60 | **70 a 150 µm²** | **0,23 a 1,00×** |

**Previsão central que quero ser cobrado:** para 4 bits, **razão ≈ 0,4×**.

**O que me faria dizer que errei:** razão de 4 bits fora do intervalo **0,15× a 1,5×**.

**Modo de falha mais provável, e é o mesmo de sempre neste projeto: subestimar.** Errei
para baixo na fuga do `Mrst` (8,5×), no `n` sub-limiar, e no `voff` da etapa 2. Aqui a
armadilha específica é eu contar só os transistores e esquecer que **célula de memória
não escala como circuito analógico**: SRAM usa dispositivos mínimos e layout otimizado
(multiplicador de layout perto de 1,5–2×), enquanto o neurônio usa dispositivos grandes
com casamento (multiplicador 3–5×). Se eu aplicar 3–5× à SRAM vou **superestimar** a
sinapse; se aplicar 1,5× ao conversor analógico vou **subestimar**. Os dois blocos da
sinapse têm multiplicadores diferentes e preciso separá-los.

**Segundo modo de falha:** esquecer que o conversor de bits para corrente precisa
entregar **picoamperes casados**. Fontes de corrente de pA exigem `L` longo — o próprio
projeto usa `W=0,5 L=10` para 10 nA. Se cada bit precisar de um dispositivo desses, o
conversor domina a sinapse e minha previsão de transistores é irrelevante.

---

## Previsão sobre a contagem de neurônios

Premissas: 10 mm² úteis, **50% de aproveitamento** (como já vínhamos usando) → 5 mm²
= 5×10⁶ µm² de área utilizável.

Com apenas neurônios a 150–300 µm², o `etapas.md` dizia **15 a 30 mil neurônios**.

**Previsão: com 100 sinapses por neurônio e peso de 4 bits, a contagem cai para a ordem
de 100 a 400 neurônios** — uma queda de **~50 a 100×**, isto é, **uma a duas ordens de
grandeza**, exatamente a suspeita levantada.

**Previsão de qual termo domina:** a partir de aproximadamente **3 sinapses por neurônio**
(razão 0,4× → 3 × 0,4 = 1,2) a área passa a ser dominada por sinapse, não por neurônio.
**Acima de ~10 sinapses/neurônio o neurônio vira ruído na conta.**

---

## Previsão sobre a Parte B

**Densidade do MiM:** espero **1 a 3 fF/µm²**, confirmando a ordem do "2 fF/µm², a
conferir" que circula desde 2026-09-06.

**Sobreposição do MiM sobre transistores:** espero que o PDK **permita** — MiM em sky130
fica entre metais superiores (`capm`/`cap2m` sobre M3/M4), muito acima do poli. Se
permitir, a área do capacitor **não soma** à área do neurônio e os 150–300 µm² podem estar
**superestimados**.

**Mas registro a dúvida que me impede de afirmar:** roteamento. As camadas de metal sob o
MiM ainda precisam levar sinal e alimentação, e um capacitor de 47 µm² bloqueia esses
metais na sua sombra. **"Pode se sobrepor fisicamente" não é o mesmo que "não custa área".**
Se eu concluir que o capacitor é grátis, terei provavelmente ignorado o roteamento.

---

## O que esta rodada NÃO decide

Se a conta mostrar que a arquitetura da Parte 5 do dossiê não cabe em 10 mm², **isso é
relatório, não decisão**. Encolher a arquitetura é decisão do Saulo.

## Placar

A preencher depois, sem editar nada acima.
