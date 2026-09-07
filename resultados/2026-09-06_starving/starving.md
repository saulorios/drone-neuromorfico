# Fome de corrente no 1º inversor — o consumo cai 64×, mas para em 218 nW

Data: 2026-09-06 · **ngspice 41** · modelos nível 1 (`generic_l1.mod`), inalterados
Netlist: derivado de `spice/neuronio.cir`, com o bloco `.options` obrigatório.

**Pergunta:** limitar a corrente do primeiro inversor reduz o consumo do neurônio para
≤ 100 nW **sem** destruir a curva f–I?

**Resposta: NÃO.** O melhor ponto dá **218 nW**, 2,2× acima do critério. A curva f–I
sobrevive (continua linear, R² = 0,99996) mas perde **3,6× de ganho**: 16,0 → 4,42 Hz/pA.

---

## Método

Duas fontes de 1,8 V independentes (`Vdd1` para o 1º inversor, `Vdd2` para o 2º), para
medir cada estágio separadamente. Duas fontes de corrente **ideais** em série com o 1º
inversor: `Ibp` de `vdd1` para o source de M1p, `Ibn` do source de M1n para o terra.

**Não foram alterados:** `Cmem` (100 fF), `Cfb` (20 fF), `Wrst` (0,5 µm), nem a dimensão
de nenhum transistor. `Iin` = 10 pA salvo indicação.

Corrente média: trapézio sobre |i| no tempo (passo variável), descartando os primeiros
20% da simulação. Frequência e CV do ISI por cruzamento ascendente de 0,5·VDD em `v(out)`.

---

## A · Linha de base — reprodução antes de qualquer coisa

Regra 1: se o ambiente não reproduz o resultado conhecido, nenhum número dele vale.

| Grandeza | Revalidação (ngspice 42) | Aqui (ngspice 41) | Desvio |
|---|---|---|---|
| Frequência nominal | 160,3 Hz | **160,35 Hz** | +0,03% |
| CV do ISI | 0,010% | 0,023% | — |
| Potência total | 12,6 µW | **13,99 µW** | **+11%** |

A frequência reproduz. A potência **não** — 11% acima. Ver pendência 1.

### Convergência da medida de potência em `tstep`

| tstep | f (Hz) | P 1º estágio | P 2º estágio | P total |
|---|---|---|---|---|
| 5 µs | 160,33 | 12,708 µW | 1,068 µW | 13,775 µW |
| 2 µs | 160,35 | 12,703 µW | 0,976 µW | 13,679 µW |
| 1 µs | 160,36 | 12,702 µW | 1,129 µW | 13,830 µW |
| 0,5 µs | 160,37 | 12,702 µW | **1,290 µW** | 13,992 µW |

**P do 1º estágio é convergente** (0,05% de espalhamento). **P do 2º estágio não é** —
sobe 32% ao refinar o passo, e ainda estava subindo em 0,5 µs. Na linha de base isso é
tolerável (o 1º estágio é 91% do total), mas o 2º estágio é justamente o termo sob
suspeita no experimento, então a varredura foi feita com `tstep` = 0,5 µs e a convergência
foi reverificada no ponto de teste (seção C).

---

## B · Varredura da corrente de polarização

`Iin` = 10 pA, `tstop` = 100 ms, `tstep` = 0,5 µs.

| IB | f (Hz) | CV do ISI (%) | P 1º est. (nW) | P 2º est. (nW) | **P total (nW)** | out máx. (V) |
|---|---|---|---|---|---|---|
| — (base) | 160,35 | 0,023 | 12 702 | 1 290 | **13 992** | 1,808 |
| 1 nA | 46,70 | 0,0022 | **1,68** | 235,00 | **236,7** | 1,622 |
| 10 nA | 46,34 | 0,0043 | 17,39 | 200,95 | **218,3** ← mínimo | 1,623 |
| 100 nA | 45,75 | 0,0015 | 176,24 | 196,36 | **372,6** | 1,629 |
| 1 µA | 45,72 | 0,0005 | 1 736 | 196,01 | **1 932** | 1,597 |

### Critérios, um a um

| Critério | Exigido | Obtido (melhor ponto, IB = 10 nA) | Veredito |
|---|---|---|---|
| Potência no ponto nominal | ≤ 100 nW | **218,3 nW** | **REPROVA** por 2,2× |
| CV do ISI | < 0,1% | 0,0043% | aprova, com folga de 23× |
| Pulso de saída | ≥ 90% de VDD (≥ 1,62 V) | 1,623 V = **90,2%** | aprova **raspando** |
| f–I linear pela origem | — | R² = 0,99996 | aprova (ganho cai 3,6×, ver C) |

---

## C · O melhor ponto (IB = 10 nA) em detalhe

### Convergência — aqui P do 2º estágio **é** convergente

| tstep | f (Hz) | P 1º est. (nW) | P 2º est. (nW) | P total (nW) |
|---|---|---|---|---|
| 1 µs | 46,34 | 17,40 | 200,95 | 218,35 |
| 0,5 µs | 46,34 | 17,39 | 200,95 | 218,35 |
| 0,25 µs | 46,34 | 17,39 | 200,97 | 218,36 |
| 0,1 µs | 46,34 | 17,39 | 201,06 | 218,45 |

0,05% de espalhamento sobre 10× em `tstep`. A não-convergência da linha de base era
específica dela: lá o pico do 2º estágio dura 35 µs; aqui a travessia é lenta e o
integrador a resolve bem. **O número de 218 nW é sólido dentro deste modelo.**

### Curva f–I

| Iin (pA) | 1 | 3 | 10 | 30 | 100 |
|---|---|---|---|---|---|
| f (Hz) | 4,81 | 14,21 | 46,34 | 136,13 | 443,34 |
| f/Iin (Hz/pA) | 4,811 | 4,736 | 4,634 | 4,538 | 4,433 |
| CV do ISI (%) | 0,0022 | 0,0015 | 0,0030 | 0,0006 | 0,0021 |
| P total (nW) | 317,1 | 239,1 | 285,2 | 288,3 | 308,6 |
| out máx. (V) | 1,608 | 1,614 | 1,623 | 1,631 | 1,641 |

Ajuste de intercepto livre: **f = 4,4235·Iin + 1,568 Hz**, **R² = 0,999956**.
Zona morta implícita: −354 fA (negativa, isto é, nenhuma). Continua linear e pela origem.

**Mas o ganho cai de 16,0 para 4,42 Hz/pA — fator 3,6.** E a razão f/`Iin` deriva 8% ao
longo da faixa (4,81 → 4,43), contra 5% na linha de base revalidada (15,3 → 16,04).
A linearidade se mantém; a sensibilidade, não.

Nota: a potência **não** cai com `Iin`. Continua sendo piso fixo, 239–317 nW, agora
imposto pelo 2º estágio em vez do 1º.

---

## D · Onde o consumo foi parar — o mecanismo

O modo de falha vigiado era: limitar o 1º estágio torna a transição de `n1` mais lenta e
**transfere** o curto-circuito para o 2º inversor, que é maior (W = 4 µm / 2 µm).

**A transferência aconteceu, mas não como esperado — o 2º estágio também melhorou.**

| | linha de base | IB = 10 nA | razão |
|---|---|---|---|
| Corrente média do 2º estágio | 716,5 nA | 111,6 nA | **÷ 6,4** |
| Pico de corrente do 2º estágio | 127,9 µA | 46,2 µA | ÷ 2,8 |
| `n1` dentro da janela 0,45–1,35 V | 25,4 µs/ciclo | **206,7 µs/ciclo** | **× 8,1** |
| Fração do período em curto | 0,56% | 0,24% | — |

A travessia de `n1` ficou 8,1× mais lenta, como previsto. Mas o 1º estágio faminto também
**dirige mais fraco**, então o pico de corrente do 2º inversor caiu 2,8×. O saldo é que o
2º estágio gasta 6,4× **menos** que na linha de base, não mais.

### Balanço do orçamento

| | P 1º est. (nW) | P 2º est. (nW) | total (nW) | 2º estágio é quanto do total |
|---|---|---|---|---|
| linha de base | 12 702 | 1 290 | 13 992 | 9,2% |
| IB = 1 nA | 1,68 | 235,0 | 236,7 | **99,3%** |
| IB = 10 nA | 17,39 | 201,0 | 218,3 | **92,0%** |
| IB = 100 nA | 176,2 | 196,4 | 372,6 | 52,7% |
| IB = 1 µA | 1 736 | 196,0 | 1 932 | 10,1% |

**O conceito funciona no estágio em que foi aplicado.** O 1º inversor cai de 12 702 para
1,68 nW — fator **7 560**. O total cai 64×. O que trava em ~200 nW é o 2º inversor, que
não foi limitado.

Existe um ótimo em IB ≈ 10 nA: abaixo dele o 1º estágio economiza pouco mais enquanto a
travessia mais lenta faz o 2º gastar mais; acima dele o 1º estágio domina de novo.

---

## E · Pendências e ressalvas

1. **A linha de base não reproduz a potência da revalidação: 13,99 µW contra 12,6 µW,
   +11%.** A frequência reproduz em 0,03%, então o circuito é o mesmo; a divergência está
   na *medida de corrente*. Candidatos não separados: versão do ngspice (41 aqui, 42 lá);
   a não-convergência do 2º estágio documentada na seção A, que sozinha explica ~0,3 µW;
   diferença de método de integração ou de janela de descarte. **Todas as comparações
   deste documento são contra a linha de base medida aqui, com o mesmo método**, então as
   razões (64×, 7 560×, 6,4×) são válidas; os valores absolutos carregam essa incerteza.

2. **As fontes de polarização ideais violam os trilhos, e isso é um artefato real.**
   Medido em IB = 10 nA: `sp1` chega a **2,14 V** (acima de VDD = 1,8 V) e `sn1` a
   **−0,36 V**. Quando o transistor corta, a fonte ideal não tem para onde escoar a
   corrente e empurra o nó até o diodo de corpo conduzir. Consequências:
   - `n1` passa a excursionar de **0,79 a 2,14 V** em vez de 0,12 a 1,80 V. O piso de
     0,79 V está **dentro** da janela de condução do 2º inversor, o que impede M2n de
     cortar limpo e **prolonga** o curto. **O artefato empurra P do 2º estágio para
     cima**, não para baixo — os 201 nW são provavelmente pessimistas.
   - A frequência é quase insensível a IB (46,70 → 45,72 Hz, 2%, sobre 1000× de IB).
     Isso não é o comportamento esperado de fome de corrente: quem está fixando a
     dinâmica são os grampos de diodo, não a polarização. **A queda de 160 → 46 Hz não
     pode ser atribuída à limitação de corrente com os dados atuais.**

   A instrução de usar fontes ideais tinha motivo correto (evitar artefato de
   sub-limiar dos modelos nível 1), mas troca um artefato por outro. Um teste limpo do
   conceito precisa de nós de source que não ultrapassem os trilhos.

3. **O pulso de saída passa raspando:** 1,623 V contra o mínimo de 1,62 V. Margem de
   3 mV, ou 0,2%. Qualquer degradação adicional reprova este critério.

4. **P do 2º estágio na linha de base não convergiu** (ainda subindo em `tstep` = 0,5 µs).
   O valor de 1 290 nW é um **limite inferior**. Isso só reforça a conclusão de que o 2º
   estágio melhorou com a fome de corrente.

5. **Tudo em modelos nível 1**, sem condução sub-limiar. O mecanismo de curto-circuito é
   estrutural e não some com a troca de modelos, mas os valores absolutos vão mudar.

6. **Não investigado, por estar fora do escopo desta tarefa:** limitar também o 2º
   inversor. O balanço da seção D mostra que é onde os 92% do orçamento restante estão.
   **Não testado — decisão do autor do projeto.**

---

## Arquivos

- `starving_resultados.png` — a figura (3 painéis)
- `raw/` — netlists gerados e saídas brutas do ngspice de cada ponto
- `../../scripts/run_starving.py` — bateria de simulações
- `../../scripts/plots_starving.py` — geração da figura
