# Previsões pré-registradas — etapa 1 (PDK SkyWater 130 nm)

Escritas em 2026-09-07, **antes** de baixar o PDK e antes de qualquer simulação.
Commitadas antes da medida, para que o erro fique registrado se houver.

---

## 1 · A armadilha do W e L (a pergunta desta rodada)

**Previsão A — a armadilha existe e é silenciosa.** Nos subcircuitos do
`sky130_fd_pr`, `W` e `L` são parâmetros em **micrômetros como número puro**. Escrever
`W=1u L=0.15u`, que é a sintaxe correta em SPICE nativo e a que este projeto usou a etapa
inteira, será interpretado como 1e-6 µm = 1 pm. Espero que o ngspice **não emita erro** —
apenas devolva corrente absurdamente baixa, da ordem de 10⁻⁶ do valor correto, ou que o
modelo faça *clamp* silencioso no mínimo do processo.

**Previsão B — valor de referência com a sintaxe correta.** Para
`sky130_fd_pr__nfet_01v8` com `W=1 L=0.15` (isto é, 1 µm por 0,15 µm), em Vgs = Vds = 1,8 V,
canto `tt`, 27 °C:

> **Id esperado: 400 a 700 µA**, centrado em **≈ 550 µA**.

Base: densidade de corrente de saturação típica de 500–600 µA/µm para o dispositivo de
1,8 V neste nó. Se o valor medido cair fora de 400–700 µA, ou a minha compreensão do
dispositivo está errada, ou a instanciação está errada — e nos dois casos nada mais deve ser
simulado até resolver.

**Critério de falsificação:** se `W=1u` e `W=1` derem a mesma corrente, a armadilha não
existe e a Previsão A está errada.

---

## 2 · A zona morta por fuga sub-limiar — revisão da previsão anterior

No plano da etapa 1 eu previ que **a curva f–I ganharia zona morta em corrente baixa**,
porque com condução sub-limiar modelada a fuga no nó `mem` passaria a ser comparável a
`Iin` = 10 pA. Aquela previsão foi feita sem número. Agora com número, e **ela muda**.

### O cálculo

A fuga que importa é a do transistor de reset `Mrst` (W = 0,5 µm, L = 2 µm) com a porta em
0 V, mais a fuga de junção do seu dreno. Corrente sub-limiar:

```
I_sub = µCox·(n−1)·V_T²·(W/L)·exp(−V_th /(n·V_T))
```

Com `V_th` ≈ 0,5–0,7 V para canal longo neste processo, `n` ≈ 1,3, `V_T` = 25,9 mV
(logo `n·V_T` = 33,6 mV), µCox ≈ 150 µA/V² e W/L = 0,25:

| V_th | exp(−V_th/nV_T) | I_sub |
|---|---|---|
| 0,5 V | 3,4 × 10⁻⁷ | ≈ 2,6 fA |
| 0,6 V | 1,8 × 10⁻⁸ | ≈ 0,14 fA |
| 0,7 V | 9,2 × 10⁻¹⁰ | ≈ 0,007 fA |

A fuga de junção do dreno de `Mrst` (área ≈ 0,25 µm²) fica na mesma ordem ou abaixo.

### A previsão revisada

> **A 27 °C: NÃO haverá zona morta detectável.** Espero fuga total no nó `mem` de
> **0,1 a 10 fA**, isto é, **0,01% a 1% da menor corrente de teste** (1 pA). A curva f–I
> deve continuar passando pela origem, com zona morta implícita abaixo de 10 fA.
>
> **A 125 °C (canto quente da etapa 3): haverá.** A fuga sub-limiar dobra a cada ~8–10 °C;
> de 27 a 125 °C são ~10 a 12 duplicações, fator **10³ a 4×10³**. A fuga vai para
> **0,1 a 40 pA** — comparável ou superior a `Iin`. Espero **zona morta de ordem 1 a 10 pA
> a 125 °C**, e possivelmente o neurônio não disparar no ponto de 1 pA.

**Isto corrige a minha previsão anterior.** Eu havia dito que a zona morta apareceria, sem
qualificar temperatura. O cálculo diz que a 27 °C ela **não** aparece — a fuga fica três
ordens de grandeza abaixo do sinal — e que o problema é de **canto quente**, não de
temperatura nominal. Se aparecer zona morta a 27 °C, a previsão está errada e a explicação
não é a que eu dei.

**Ressalva sobre a refutação anterior:** a revalidação de 2026-09-06 já havia refutado a
zona morta, mas com modelos nível 1, que **não têm condução sub-limiar alguma**. Aquela
refutação é vazia para esta pergunta. O teste com sky130 é o primeiro teste real.

---

## 3 · O que espero que mude nos números da etapa 0

Registrado para comparação, sem compromisso de precisão:

- **Ganho f–I:** governado por `T = Cfb·VDD/Iin`, que é capacitivo e não depende do modelo
  do transistor. Espero que **mude pouco** — dentro de ±20% dos 13,79 Hz/pA — desde que o
  reset continue incompleto do mesmo jeito.
- **Consumo:** o piso estático de 80,9 nW é corrente de curto-circuito do 2º inversor. Com
  modelos reais espero que **mude bastante**, e não sei em qual direção: a mobilidade
  degradada e a saturação de velocidade reduzem a corrente, mas o `V_th` mais baixo do
  sky130 (≈ 0,45 V contra 0,45 V do nível 1 — parecidos) mantém a janela de curto aberta.
- **As dimensões atuais são todas legais no sky130** (L mínimo 0,15 µm, W mínimo 0,42 µm;
  o menor W em uso é 0,5 µm). Nenhuma precisa mudar por regra de projeto — o que não quer
  dizer que sejam boas escolhas.
