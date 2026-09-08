# Pré-registro — Etapa 2, rodada 1: VALIDAÇÃO DO INSTRUMENTO

Data: 2026-09-08 · **ngspice 42** (`~/opt/ngspice42/bin/ngspice42`, extraída de
`42+ds-3build1` do Ubuntu noble) · **sky130A**, `.temp 27`
Autor das previsões: Claude · **escrito e commitado ANTES de qualquer execução**

> Esta rodada **não mede dispersão**. Ela responde a uma pergunta só: o motor
> estatístico existe, sorteia por instância, muda entre amostras, e tem a magnitude
> que o PDK declara? Nenhum histograma de frequência desta rodada vale como resultado
> da etapa 2.
>
> Motivo: as três falhas caras deste projeto (§5 item 1, §7 `reltol`, §7 detector de
> limiar fixo) foram **todas de instrumento e nenhuma de conceito**, e todas as três
> produziram números limpos. A etapa 2 introduz um gerador aleatório — e gerador
> aleatório quebrado não parece quebrado, parece um histograma estreito.

---

## Ordem de execução — é fixa e o motivo importa

**V0 antes de V4.** V0 prova que o **zero é alcançável**; V4 prova que o **não-zero
aparece quando deve**. Na ordem inversa, um V4 que passasse esconderia a possibilidade de
que algo mais varia entre amostras e que a variação medida não é descasamento.

V5 → V0 → V1 → V2 → V3 → V4.

---

## V5 · Integridade do ambiente

**O quê:** reproduzir o ponto nominal da etapa 1 nesta máquina, na ngspice 42.
Netlist: o `cm_100.cir` de `resultados/2026-09-07_cmem_sky130/raw/`, sem modificação —
`Cmem` = 100 fF, `Cfb` = 20 fF, `Iin` = 10 pA, `IB1` = 10 nA, `IB2` = 3 µA, canto `tt`.

| | |
|---|---|
| **Previsão** | f dentro de **1%** de **139,58 Hz** (denominador: f nominal da etapa 1, `resultados/2026-09-07_migracao_sky130/`) |
| **Falha** | desvio > 1% |
| **Modo de falha mais provável** | nenhum — o DC já bate bit a bit entre 41 e 42 nos dois dispositivos. Se falhar, a suspeita nº 1 é `set ngbehavior=hsa` (o `spinit` do PDK o define; os netlists deste projeto não, e a etapa 1 rodou sem) |

**Papel:** o V5 mudou de função. Não é mais "41 contra 42" — é prova de que **este
ambiente reproduz a etapa 1**. Sem ele, toda dispersão da rodada 2 seria normalizada
contra um nominal que esta máquina nunca produziu.

---

## V0 · CONTROLE NEGATIVO — o zero é alcançável?

**O quê:** o mesmo laço de N = 6 amostras do neurônio completo, variando `set rndseed`
de 1 a 6, com o descasamento **DESLIGADO** — canto `tt`, não `tt_mm`.

| | |
|---|---|
| **Previsão** | σ(f) = **exatamente zero**. Não "pequeno": zero absoluto, bit a bit, nas 6 amostras |
| **Falha** | **qualquer** σ ≠ 0 |
| **Modo de falha mais provável** | o `rndseed` alcançar algo que não deveria alcançar — ruído injetado pelo solver, ou reinicialização de estado entre execuções |

**Por que este é o teste mais importante da rodada.** Se algo varia entre amostras com o
descasamento desligado, essa mesma coisa varia com ele ligado, e **contaminaria a rodada 2
inteira** sem aparecer em lugar nenhum: apareceria somada em quadratura dentro do σ de
frequência, indistinguível de descasamento real. Um σ de fundo de 3% faria uma dispersão
verdadeira de 4% ser lida como 5%.

---

## V1 · O sorteio é por INSTÂNCIA?

**O quê:** um netlist com arrays de transistores idênticos, mesma polarização, canto
`tt_mm`, ponto de operação DC, medindo Id de cada instância.

| array | dispositivo | geometria | por que esta geometria |
|---|---|---|---|
| A | `nfet_01v8` | W=1 L=0.5 (0,5 µm²) | é o `M1n` |
| B | `pfet_01v8` | **W=5 L=1** (5 µm²) | é `Mbp2` **e** `Mref2` — o par do 2º espelho, **geometria idêntica entre si** |
| C | `nfet_01v8` | W=4 L=0.5 (2 µm²) | 4× a área de A, para o teste de Pelgrom em V3 |

N = 100 instâncias por array.

| | |
|---|---|
| **Previsão** | as 100 correntes de cada array **distintas entre si** |
| **Falha** | todas iguais dentro de um array |

**Modo de falha mais provável, e é o perigoso.** Que o `AGAUSS` seja avaliado **uma vez por
conjunto único de parâmetros do subcircuito**, e não por instância. Nesse caso `M1p` (W=2) e
`M2p` (W=4) variariam de forma independente — parecendo funcionar — mas **`Mbp2` e `Mref2`,
que têm `W=5 L=1` idênticos, receberiam exatamente o mesmo desvio e o espelho ficaria
perfeitamente casado.** O caminho de maior sensibilidade do circuito morreria em silêncio, e
o histograma sairia bonito.

**É por isso que o array B tem geometria idêntica ao par real do espelho.** Um array de
cópias quaisquer não distinguiria os dois casos.

---

## V2 · O sorteio muda entre EXECUÇÕES?

**O quê:** rodar o netlist de V1, canto `tt_mm`, três vezes: (a) duas vezes sem `rndseed`;
(b) com `set rndseed=1` e `set rndseed=2`. Comparar as correntes.

| | |
|---|---|
| **Previsão** | **sem `rndseed`: idênticas.** A ngspice tende a semente fixa; com `rndseed` explícito: diferentes |
| **Falha** | `rndseed` explícito não mudar nada → não há como gerar amostras independentes por execução, e a rodada 2 precisa de outro mecanismo (N cópias num netlist só, em vez de N execuções) |

**Consequência se a previsão se confirmar:** um laço ingênuo de 200 execuções produziria
**200 cópias da mesma amostra**, com σ = 0 ou, pior, com σ pequeno vindo de outra coisa.
Esta é a versão etapa-2 do erro fundador do projeto: o instrumento em silêncio.

---

## V3 · A MAGNITUDE bate com um modelo analítico independente?

**O quê:** dos arrays de V1, extrair σ(Id)/Id; converter a σ(Vth) equivalente dividindo por
`gm`, medido no mesmo netlist por um segundo ponto de polarização (Vgs = 1,20 e 1,25 V,
Vds = 1,8 V — inversão forte, onde a extração é limpa).

**Previsão para o array A** (`nfet_01v8`, W=1 L=0.5, W·L = 0,5 µm²), a partir dos próprios
slopes do PDK e **sem olhar a medida**:

| termo | cálculo | contribuição a σ(Vth_eq) |
|---|---|---|
| `vth0_slope` | 3,356e-3 V·µm ÷ √0,5 µm² | **4,75 mV** |
| `toxe_slope` | 3,443e-3 ÷ √0,5 = 0,487% em Cox, × (Id/gm ≈ 0,32 V) | 1,6 mV |
| **soma em quadratura** | | **≈ 5,0 mV** |

| | |
|---|---|
| **Previsão** | σ(Vth_eq) do array A entre **4,2 e 6,0 mV** |
| **Falha** | fora de **2×** em qualquer direção (< 2,5 mV ou > 10 mV) |
| **Modo de falha mais provável** | subestimar, como já aconteceu duas vezes na etapa 1 (fuga 8,5× acima do previsto, `n` de 1,53 e não 1,3). A extração de `gm` em inversão forte com velocidade de saturação é onde a conta é mais frágil |

**V3b · a lei de Pelgrom — o caso-limite que deveria falhar.** O array C tem 4× a área do
array A. Se o modelo é σ ∝ 1/√(W·L), então:

| | |
|---|---|
| **Previsão** | σ(A)/σ(C) = **2,00 ± 10%** |
| **Falha** | razão fora de 1,7–2,3, ou — sinal de que a área não está sendo lida — razão ≈ 1,0 |

Este é o teste que separa "o PDK está aplicando a fórmula" de "alguma coisa está variando".
Um σ com a magnitude certa mas que **não escala com a área** não é descasamento de Pelgrom:
é outra coisa com o valor certo por acidente.

---

## V4 · O que varia AFETA o que deveria afetar?

**O quê:** neurônio completo, canto `tt_mm`, N = 12 execuções com `rndseed` de 1 a 12.
Medir σ(f)/f. Detector de disparo com **limiar adaptativo** (§7); potência **não** medida
nesta rodada.

| | |
|---|---|
| **Previsão** | σ(f)/f > **2%** (denominador: f média das 12 amostras) |
| **Falha** | σ(f)/f < **0,1%** → instrumento morto |
| **Modo de falha mais provável** | não disparar em parte das amostras. Com σ(Vth) de ~5 mV em `M1n` e o circuito em sub-limiar, uma amostra de cauda pode sair do regime integra-e-dispara e o detector reportar "não dispara" — que é resultado, não falha, **desde que a forma de onda seja inspecionada e não só o contador** |

**O que V4 NÃO é.** Não é a medida da etapa 2. N = 12 é pequeno demais para um σ com
denominador confiável, e o valor que sair aqui **não deve ser citado** como dispersão do
circuito. V4 responde "sim/não", não "quanto".

---

## Pré-registro do TERMO DO CAPACITOR — rodada 2

Decisão do Saulo em 2026-09-08: opção (a), `C` ideal com σ injetado à mão. A opção (b)
(trocar por `sky130_fd_pr__cap_mim_m3_1`) fica para a etapa 8, junto com os parasitas de
layout, porque ela muda o circuito — o subcircuito traz resistência série — e mudar circuito
e estatística no mesmo experimento impede separar os dois efeitos.

**O σ é CÁLCULO NOSSO a partir do modelo MiM. NÃO é dado do PDK.** O PDK fornece a fórmula
e as densidades; a aplicação a um `C` ideal é nossa, e a área é inferida da densidade, não
desenhada. Rotular como dado do PDK seria dar ao número uma procedência que ele não tem.

**A conta, com denominador** (densidades do canto típico, `r+c/res_typical__cap_typical__lin.spice`:
`camimc` = 2,00 fF/µm², `cpmimc` = 0,19 fF/µm; fórmula `σ = 2,8% ÷ √(área em µm²)` do
subcircuito `cap_mim_m3_1`):

| | `Cmem` = 100 fF | `Cfb` = 20 fF |
|---|---|---|
| lado do quadrado equivalente | 6,88 µm | 2,98 µm |
| área | 47,4 µm² | 8,87 µm² |
| **σ(C)/C** | **0,407%** | **0,940%** |
| σ(C) absoluto | 0,407 fF | 0,188 fF |

σ(`Ctot`) = √(0,407² + 0,188²) = **0,448 fF** sobre `Ctot` = 129,71 fF medido → **0,345%**.
Com `f ∝ Ctot^-0,85` (§3): **σ(f) pelos capacitores = 0,293%.**

**O PAPEL deste termo — não é medida, é VERIFICAÇÃO FALSIFICÁVEL.** Contra os ~11% de piso
dos espelhos, 0,293% soma em quadratura para 11,0039%: o capacitor **muda o total em
0,004%**. Ele é **numericamente incapaz de alterar a conclusão da etapa 2**, e por isso não
pode ser lido como contribuição.

O que ele testa é outra coisa:

| resultado | leitura |
|---|---|
| contribuição isolada ≈ **0,3%** (0,15 a 0,6%) | ✅ confirma que a cadeia `Cmem` → `Ctot` → frequência **está sendo exercitada** pelo motor estatístico — que o σ injetado chega mesmo à frequência, com o expoente −0,85 medido na etapa 1 |
| contribuição isolada **> ~1%** | ⚠️ **isto é o resultado, não um detalhe.** Significa que a sensibilidade de f a `Ctot` é maior que o expoente −0,85 medido, ou que existe um caminho de `Cmem` à frequência que não é via `Ctot`. Nos dois casos, o entendimento do circuito registrado na §3 está errado |
| contribuição isolada ≈ **0** | ❌ o σ injetado não está chegando à frequência — falha de instrumento, não capacitor bem casado |

**Reportar a contribuição do capacitor SEPARADA das demais.** Três configurações na
rodada 2: (i) só transistores variando, (ii) só capacitores variando, (iii) ambos. A
verificação de quadratura entre as três é ela própria um teste do motor.

---

## Placar — preenchido em 2026-09-08 após a execução. Nada acima foi editado.

| teste | previsto | medido | veredito |
|---|---|---|---|
| V5 | f a menos de 1% de 139,58 Hz | 139,5821 Hz, +0,002% | ✅ confirmada |
| V0 | σ(f) = zero exato | 0,000 Hz; 6 arquivos, 1 SHA-256 | ✅ confirmada |
| V1 | 100 distintos por array | 100/100 nos três, inclusive o par do espelho | ✅ confirmada |
| V2 | sem semente: idênticas | **diferentes** | ❌ **REFUTADA** |
| V3 (array A) | σ(Vth_eq) 4,2 a 6,0 mV | 6,200 mV | ⚠️ 3,3% acima da faixa |
| V3b | σ(A)/σ(C) = 2,00 ± 10% | 1,944 e 1,952 | ✅ confirmada |
| V4 | σ(f)/f > 2% | 1,762% | ❌ **REFUTADA** (passa o critério de falha, < 0,1%) |
| convergência | < 1% com `tstep`/4 | −0,0006% e −0,0018% | ✅ confirmada |

**As duas refutações, e o que cada uma custou.**

**V2** — previ que a ngspice repetiria o sorteio sem semente e que `set rndseed` o
controlaria. As duas metades erradas: `set rndseed` no `.control` **não fixa nada**, porque
os `.model` com `AGAUSS` são avaliados na leitura do netlist, antes do `.control` rodar.
`.option seed=N` fixa. Isto **mudou o procedimento da rodada 2** e invalidou o primeiro
teste de convergência, que acusou +4,84% quando o valor real é −0,0006%.

**V4** — previ σ(f)/f > 2%, medido 1,762%. O erro em si é pequeno; o que ele expõe não é:
1,76% é **6,2× menor** que os ~11% de piso estimados para o descasamento de corrente dos
espelhos. A corrente descasa muito mais que a frequência.

**V3** — o modo de falha que registrei ("subestimar, como já aconteceu duas vezes na
etapa 1") **aconteceu de novo**, pelo motivo que eu mesmo escrevi e não segui: dispensei o
`voff` com uma frase, e o `voff_slope` do nfet é **2,1× maior** que o do `vth0`.

Detalhes em `instrumento.md`.
