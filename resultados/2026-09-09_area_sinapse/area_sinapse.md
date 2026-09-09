# A área da sinapse, e a contagem real de neurônios por chip

Data: 2026-09-09 · **Sem simulação.** Leitura do PDK + aritmética.
Previsões pré-registradas em `previsao_pre_registrada.md`, commit `dd8c75e`,
**antes de qualquer cálculo**.

---

## Placar

| previsão | previsto | obtido | veredito |
|---|---|---|---|
| razão área_sinapse/área_neurônio, 4 bits | **0,4×** (faixa 0,15–1,5×) | **1,28 a 3,79×** | ❌ **REFUTADA** — acima do teto da faixa |
| razão, 1 bit | 0,05–0,23× | 0,11 a 0,25× | ✅ |
| razão, 2 bits | 0,10–0,47× | 0,22 a 0,50× | ✅ |
| neurônios com S=100, 4 bits | 100 a 400 | **88 a 130** | ⚠️ pouco abaixo |
| queda na contagem | 50 a 100× | **~150 a 250×** | ❌ **subestimei** |
| sinapse domina a partir de | ~3 sinapses/neurônio | **0,5** (4 bits) | ❌ subestimei |
| densidade do MiM | 1 a 3 fF/µm² | **2,00 fF/µm²** | ✅ |
| MiM pode se sobrepor a transistor | sim | **sim, sem regra que proíba** | ✅ |

**O modo de falha que eu havia pré-registrado é exatamente o que aconteceu:** "subestimar".
E a causa também estava pré-registrada — eu escrevi que o conversor de bits para corrente
precisa entregar **picoamperes casados** e que, se cada bit exigisse área de casamento, o
conversor dominaria a sinapse. Dominou. Escrevi o aviso e mesmo assim previ 0,4×.

---

## As âncoras — lidas, não estimadas

| grandeza | valor | fonte |
|---|---|---|
| sítio da célula padrão `sky130_fd_sc_hd` | 0,460 × 2,720 µm = **1,2512 µm²** | `libs.tech/openlane/sky130_fd_sc_hd/config.tcl` |
| latch `dlxtp_1` (1 bit) | 5,52 × 2,72 = **15,014 µm²** | LEF, `SIZE 5.520000 BY 2.720000` |
| flip-flop `dfxtp_1` (1 bit) | 7,36 × 2,72 = **20,019 µm²** | LEF, `SIZE 7.360000 BY 2.720000` |
| bitcell SRAM 1RW (6T) de fundição | **1,896 µm²** | OpenRAM/sky130, Fig. 1 |
| bitcell SRAM 1RW1R (8T) | **6,162 µm²** | idem |
| `vth0_slope` do pfet | 5,856 mV·µm | PDK, verificado na etapa 2 |
| `n·Ut` medido | 38,95 a 44,17 mV | etapa 2, rodada 1 |

**A biblioteca de células padrão NÃO está instalada nesta máquina** — a instalação enxuta de
2026-09-07 baixou só `common` e `sky130_fd_pr`. As áreas de célula acima vieram dos LEF
públicos do `google/skywater-pdk-libs-sky130_fd_sc_hd`; o sítio veio do PDK local.

**A área do LEF já é área de LAYOUT.** Não se aplica multiplicador 3–5× a ela — esse era o
erro que pré-registrei como armadilha. O multiplicador 3–5× vale só para o bloco analógico.

**A bitcell de fundição não é utilizável avulsa.** Ela usa regras "core memory" com OPC
pré-fabricado e "impõe restrições ao layout da matriz". Serve para uma matriz de memória em
bloco, não para uma célula de peso espalhada ao lado de cada sinapse. Por isso a conta
principal usa **latch**, e a coluna SRAM é o piso otimista.

---

## O termo que domina: o DAC casado

O conversor de bits para corrente precisa entregar corrente **casada** na faixa de pA. A área
exigida sai do descasamento medido do próprio PDK, não de um palpite:

`σ(I)/I = σ(Vth)/(n·Ut)`, com `σ(Vth) = 5,856 mV·µm / √A`

Critério de monotonicidade: `3·√(2^(n−1))·σ_u < 0,5 LSB`.

| peso | unidades | σ_u máximo | área por unidade | **área ativa do DAC** |
|---|---|---|---|---|
| 1 bit | 1 | 10,00% (exatidão de peso) | 2,143 µm² | **2,14 µm²** |
| 2 bits | 3 | 11,79% | 1,543 µm² | **4,63 µm²** |
| 4 bits | 15 | **5,89%** | 6,173 µm² | **92,59 µm²** |

**20× de área para 2 bits a mais.** A área do DAC casado escala como ~4ⁿ: o número de
unidades dobra a cada bit *e* a tolerância por unidade aperta por √2, e área vai com 1/σ².
Este é o resultado clássico de DAC casado, e aqui ele sai dos números medidos do projeto.

---

## Área da sinapse

Multiplicador: **1,0× no digital** (o LEF já é layout), **3 a 5× no DAC analógico casado**.

| peso | armazenamento (latch) | lógica de atualização | DAC (3× a 5×) | **TOTAL** | **razão / neurônio** |
|---|---|---|---|---|---|
| 1 bit | 15,01 µm² | 11,26 µm² | 6,4 a 10,7 | **32,7 a 37,0 µm²** | **0,11 a 0,25×** |
| 2 bits | 30,03 µm² | 22,52 µm² | 13,9 a 23,2 | **66,4 a 75,7 µm²** | **0,22 a 0,50×** |
| 4 bits | 60,06 µm² | 45,04 µm² | **277,8 a 463,0** | **382,9 a 568,1 µm²** | **1,28 a 3,79×** |

Denominador da razão: neurônio = 150 a 300 µm² (estimativa corrente do projeto).
Lógica de atualização estimada em 0,75 latch por bit — **é o termo mais fraco desta conta**,
e é o único sem âncora medida.

**Com 4 bits a sinapse é maior que o neurônio.** Entre 1,3 e 3,8 vezes maior.

---

## Quantos neurônios cabem em 10 mm²

Premissas: 10 mm² úteis, **50% de aproveitamento** → 5×10⁶ µm². Sinapse com latch.
Faixa = melhor caso (neurônio 150 µm², DAC 3×) a pior caso (neurônio 300 µm², DAC 5×).

| sinapses/neurônio | 1 bit | 2 bits | **4 bits** |
|---|---|---|---|
| 10 | 7 464 a 10 480 | 4 730 a 6 139 | **836 a 1 257** |
| 30 | 3 547 a 4 420 | 1 945 a 2 333 | **288 a 430** |
| **100** | 1 250 a 1 462 | 635 a 736 | **88 a 130** |
| 300 | 439 a 502 | 217 a 249 | **29 a 43** |

**Referência atual do `etapas.md`, contando só neurônios: 15 000 a 33 000.**

### Qual célula corresponde ao que a Parte 5 precisaria

**Achado que precisa ser dito primeiro: a Parte 5 do dossiê não especifica conectividade.**
Ela descreve quatro camadas com graus diferentes de plasticidade e o mecanismo de modulação
por surpresa (§5.2), mas **em nenhum ponto declara sinapses por neurônio**. Não existe,
portanto, uma célula que "a Parte 5 pede" — existe uma célula que a *função* descrita exige,
e essa inferência é minha, não do dossiê.

A camada "Associação e novidade" é memória associativa. Para esse tipo de rede a capacidade
cresce com a conectividade — a regra clássica de Hopfield dá ~0,14 padrões por sinapse por
neurônio. Isso põe o piso útil na casa de **S = 100** (≈14 padrões) e o confortável em
**S = 300**. Com 4 bits de peso, essas duas linhas dão **88 a 130** e **29 a 43** neurônios.

**Comparado aos 15 000 a 33 000 que circulam no projeto: fator de 150 a 250× para menos.**

### Onde a sinapse passa a dominar a área

Caso central (neurônio 225 µm², DAC 4×):

| peso | a sinapse domina a partir de |
|---|---|
| 1 bit | 6,5 sinapses/neurônio |
| 2 bits | 3,2 sinapses/neurônio |
| **4 bits** | **0,5 sinapses/neurônio** |

Com 4 bits, **uma única sinapse já pesa o dobro do neurônio**. Acima de 10 sinapses por
neurônio o neurônio é ruído na conta em qualquer resolução: 61% a 96% da área é sinapse.

---

## Parte B · o capacitor MiM

### Densidade — CONFERIDA, e o palpite estava certo

O "2 fF/µm², a conferir" que circula desde 2026-09-06 está **confirmado**.
Fonte: `libs.tech/ngspice/r+c/res_*__cap_*__lin.spice`.

| canto | `camimc` (área) | `cpmimc` (perímetro) |
|---|---|---|
| **típico** | **2,00 fF/µm²** | 0,19 fF/µm |
| `cap_low` | 1,778 fF/µm² | 0,03 fF/µm |
| `cap_high` | 2,231 fF/µm² | 0,35 fF/µm |

Variação global de ±11% sobre o típico. Áreas de placa no canto típico:
**`Cmem` = 47,38 µm²**, **`Cfb` = 8,87 µm²**, **`Cload` = 1,97 µm²** — soma **58,2 µm²**.

### Sobreposição — o PDK PERMITE, mas não de graça

O que o PDK diz, e não o que é plausível:

- `cap_mim_m3_1` é a interseção de **MET3** com **CAPM**; o contato `mimcc` sobe para
  **METAL4** (`sky130A.tech`, linhas 338, 558, 3437). Fica muito acima de poli e difusão.
- **Não existe nenhuma regra de DRC que proíba MiM sobre difusão, poli ou nwell.** Procurei;
  não há. **A sobreposição física é permitida.**
- **Mas o MiM consome as camadas por onde ele passa.** Três regras cobram isso:

| regra | o que exige |
|---|---|
| `capm.3` | metal3 deve **circundar** o MiM por 0,14 µm — a placa inferior **é** metal3 |
| `capm.11` | metal3 **não relacionado** tem de ficar a **0,5 µm** do MiM |
| `capm.1` / `capm.2a` | largura mínima 1,0 µm; espaçamento MiM–MiM 0,84 µm |

**Consequência.** O capacitor não gasta área de **transistor**, mas apaga **metal3 e metal4**
na sua sombra, mais um halo de 0,5 µm. Para o neurônio, 58,2 µm² de placa sobre um bloco de
transistores de 46,5 a 77,5 µm² significa que met3/met4 ficam praticamente indisponíveis
naquela célula — para o roteamento dela e para qualquer passagem por cima.

| cenário | área do neurônio |
|---|---|
| capacitor **não** se sobrepõe | 105 a 136 µm² |
| capacitor se sobrepõe **por inteiro** | ~78 µm² |
| estimativa atual do projeto | 150 a 300 µm² |

**A estimativa de 150–300 µm² parece conservadora**, e a sobreposição pode reduzi-la. Mas
registro a dúvida que pré-registrei e que continua de pé: **"pode se sobrepor fisicamente"
não é "não custa área"**. O custo migra de área de silício para congestionamento de
roteamento, que este levantamento não sabe quantificar. Só o layout da etapa 8 responde.

**E isto não muda a conclusão da Parte A.** A sinapse é dominada pelo DAC casado, não por
capacitor. Mesmo que o neurônio encolhesse para 78 µm², a razão sinapse/neurônio de 4 bits
**subiria** para 4,9 a 7,3×, e a contagem com S=100 mudaria de 88–130 para 87–129. O termo
do neurônio já é irrelevante.

---

## Ressalvas

1. **A lógica de atualização é o termo sem âncora.** Estimada em 0,75 latch por bit. Se um
   contador incremento/decremento com carry custar 2 latches por bit, a sinapse de 4 bits vai
   a 443–628 µm² e a razão a 1,48–4,19×. **Não muda a conclusão, muda a margem.**
2. **O critério de monotonicidade é uma escolha.** Usei 3σ. Um projeto que aceite DNL de
   1 LSB em vez de 0,5 corta a área do DAC por 4×, levando a sinapse de 4 bits a 174–198 µm²
   e a razão a 0,58–1,32×. **Isso é decisão de projeto, não de executor.**
3. **DAC binário não é a única topologia.** Um DAC termométrico ou de unidades iguais casa
   melhor por área em resoluções baixas; não avaliei. Também não avaliei divisão de corrente,
   que troca área por sensibilidade a fuga — e fuga é restrição conhecida deste circuito.
4. **A biblioteca padrão não está instalada localmente.** As áreas de célula vêm dos LEF
   públicos. Reprodutível, mas não verificado contra o PDK desta máquina.
5. **Aproveitamento de 50% é herdado, não medido.** Um bloco analógico com anel de guarda
   (risco R2) provavelmente aproveita menos.

---

## O que este levantamento NÃO decide

A conta mostra que a arquitetura da Parte 5, com conectividade de assembleia, **cabe em
10 mm² apenas na casa de dezenas a centenas de neurônios**, não de milhares.

**Encolher a arquitetura — reduzir bits de peso, reduzir sinapses por neurônio, ou aceitar
menos neurônios — é decisão do Saulo.** Este documento relata; não decide.
