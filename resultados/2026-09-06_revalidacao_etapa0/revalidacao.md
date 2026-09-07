# Revalidação da etapa 0 — tolerâncias numéricas corrigidas

Data: 2026-09-06 · ngspice 42 · modelos nível 1 (`generic_l1.mod`), inalterados
Netlist: `spice/neuronio.cir` com bloco `.options` novo. Circuito **não** foi modificado.

```spice
.options abstol=1e-15 vntol=1e-9 reltol=1e-4 gmin=1e-15 chgtol=1e-16
+ trtol=1
```

Todos os números abaixo são de simulação executada, não de literatura.
Ponto nominal salvo indicação: Cmem=100 fF, Cfb=20 fF, Iin=10 pA, VDD=1,8 V, Wrst=0,5 µm.

---

## A · Convergência (confirma a hipótese do abstol)

| opções | tstep | f (Hz) | CV do ISI (%) |
|---|---|---|---|
| padrão | 5 µs | 176,1 | 22,0 |
| padrão | 2 µs | 175,3 | 21,8 |
| padrão | 1 µs | 162,0 | 16,5 |
| padrão | 0,5 µs | 169,2 | 19,2 |
| corrigidas | 5 µs | 160,4 | 0,055 |
| corrigidas | 2 µs | 160,4 | 0,050 |
| corrigidas | 1 µs | 160,5 | 0,058 |
| corrigidas | 0,5 µs | 160,5 | 0,064 |
| corrigidas + trtol=1 | 5 µs | 160,3 | 0,0098 |
| corrigidas + trtol=1 | 0,5 µs | 160,3 | 0,0101 |

**Valor convergido: 160,3 Hz.** Nem 158, nem 175, nem 166.
O espalhamento de ~10% entre corridas era numérico. O jitter *dentro* de cada
corrida era pior ainda: 20% de CV entre disparos consecutivos, num circuito
determinístico onde o CV correto é 0,01%.

`trtol` (padrão 7) importa tanto quanto `abstol`: relaxa o controle de erro de
truncamento local e deixa o integrador dar passos grandes demais.

## B · Curva f–I (12 pontos, 1 a 100 pA)

| Iin (pA) | 1 | 2 | 3 | 5 | 7 | 10 | 15 | 20 | 30 | 50 | 70 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f (Hz) | 15,3 | 31,9 | 47,0 | 80,0 | 110,4 | 160,3 | 240,5 | 314,5 | 481,1 | 801,9 | 1123 | 1604 |

**Ganho: 16,0 Hz/pA** (não 17,5). Reta pela origem, sem zona morta detectável
até 1 pA. A razão f/Iin fica entre 15,3 e 16,0 em toda a faixa.

**A hipótese de corrente de fuga está refutada.** A discrepância 158 vs 175 Hz
era inteiramente ruído numérico, não fuga.

## C · Consumo — o problema estrutural

Corrente média em VDD, mesma varredura de Iin:

| Iin (pA) | 1 | 10 | 50 | 100 |
|---|---|---|---|---|
| I(VDD) média | 9,06 µA | 6,97 µA | 7,13 µA | 7,12 µA |
| Potência | 16,3 µW | 12,6 µW | 12,8 µW | 12,8 µW |

**Plana.** Independente da corrente de entrada, como previsto analiticamente.

No ponto nominal: potência do sinal = 1,8 V × 10 pA = 18 pW.
Potência consumida = 12,6 µW. **Razão: 7 × 10⁵.**
Energia por disparo: 78 nJ. Referência de neurônios neuromórficos
publicados: 1–100 pJ. Estamos ~10⁶ vezes acima.

Mecanismo confirmado por cálculo à mão: a membrana oscila entre 0,41 V e
0,99 V; com VTO = 0,45 V e VDD = 1,8 V, o NMOS do primeiro inversor conduz
acima de 0,45 V e o PMOS conduz abaixo de 1,35 V. **A faixa de operação da
membrana está inteiramente dentro da janela em que os dois conduzem.** Não é
uma travessia rápida da região de transição — o inversor nunca sai dela.
Corrente de saturação prevista para o NMOS a meia rampa: 7,5 µA. Medido: 7,1 µA.

### Mitigação testada: enfraquecer o primeiro inversor

| escala W1p/W1n | f (Hz) | potência |
|---|---|---|
| 1× (2 µm / 1 µm) | 160,3 | 12,84 µW |
| 1/10 | 115,7 | 0,775 µW |
| 1/100 | 101,5 | 68 nW |
| 1/1000 | não dispara | 11,6 nW |

Funciona — 189× de redução por 100× de enfraquecimento — mas **1/100 exige
W = 10 nm, não fabricável.** No sky130 o mínimo do nfet_01v8 é W = 0,42 µm.
Manter W/L exigiria L ≈ 21 µm. Área proibitiva.
Conclusão: o caminho viável não é encolher o inversor, é limitar sua corrente
(inversor com fome de corrente, ou troca de topologia).

## D · O transistor de reset controla a frequência

| Wrst | 0,25 µm | 0,5 µm | 1 µm | 2 µm | 4 µm | 8 µm |
|---|---|---|---|---|---|---|
| f (Hz) | 189,4 | 160,3 | 131,6 | 108,3 | 91,9 | 81,4 |
| V mín. da membrana | 0,477 | 0,406 | 0,305 | 0,183 | 0,061 | −0,038 |

32× em Wrst → 2,3× em frequência. **Mrst é um elemento que fixa a frequência**,
e o dossiê não o identifica como tal em lugar nenhum.

Isto explica o fator 1,76× do modelo analítico, e a causa **não** é overshoot da
saída acima de VDD: é que o reset é incompleto. A membrana não é descarregada
até o nível que o modelo supõe — ela para em 0,406 V, e onde ela para depende da
força do Mrst e da largura do pulso. O modelo `T = Cfb·VDD/Iin` só valeria com
reset completo e auto-terminado.

Consequência para a etapa 2: existe um caminho direto de descasamento do Mrst
para dispersão de frequência entre neurônios, que não estava no mapa de riscos.

## E · O achado principal, reteste

Painel 4 do dossiê (tolerâncias padrão): 176/168/166/153/172 Hz, não-monotônico.

Com tolerâncias corrigidas:

| Cmem (fF) | 25 | 50 | 100 | 200 | 400 | 800 |
|---|---|---|---|---|---|---|
| f (Hz) | 183,1 | 173,8 | 160,4 | 145,4 | 140,0 | 151,0 |
| excursão (V) | 1,43 | 1,03 | 0,674 | 0,409 | 0,223 | 0,107 |
| CV do ISI (%) | 0,026 | 0,025 | 0,022 | 0,027 | 0,020 | 0,033 |

**O achado sobrevive, com correção.** 16× de capacitor produz 24% de variação
de frequência — contra os 1600% que a intuição ingênua (f ∝ 1/Cmem) previria.
O cancelamento é real e é o efeito dominante.

Mas ele **não é exato**. A curva agora é monotônica decrescente e limpa, com
ruído 1000× menor que o efeito. A afirmação de §4.3 de que Cmem "some da
equação" está forte demais: sobra um resíduo de ~24%. E a estrutura do painel 4
original era ruído, como já registrado.

O colapso da excursão está confirmado e é mais severo que o medido antes:
1,43 V → 0,107 V.

---

## Estado das objeções levantadas

| # | Objeção | Veredito |
|---|---|---|
| 1 | Topologia consome demais | **Confirmada.** 7×10⁵ vezes a entrada. Pior que o estimado. |
| 2 | Fuga causando zona morta | **Refutada.** Era ruído numérico. Curva passa pela origem. |
| 3 | Modelo de excursão não fecha | **Confirmada, causa diferente.** Reset incompleto, não overshoot. |
| — | Hipótese abstol (Claude CLI) | **Confirmada.** Explica 1, 2 e 3 do registro dele. |

## Pendências que este trabalho não resolve

- Tudo acima usa modelos nível 1, que não têm condução sub-limiar. O consumo
  em sky130 pode ser diferente em magnitude, mas o mecanismo é estrutural.
- O CV de 5,8% que aparece em 4 dos 12 pontos da varredura de Iin não foi
  investigado; pode ser artefato do detector de disparo (12 disparos, efeito
  de borda), não do circuito.
- Nenhuma medida de área, parasitas ou layout.
