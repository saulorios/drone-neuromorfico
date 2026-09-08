# Plano de etapas — v2.0

> **Substitui a Parte 7 do dossiê v1.0** (`docs/dossie_v1.0.pdf`, setembro de 2026).
> As Partes 1, 2, 3, 5 e 6 do dossiê continuam válidas e não foram reescritas.
> A Parte 4 (resultados) está superada por `resultados/` e pela §4 do `CLAUDE.md`.
>
> Data: 2026-09-07 · Escrito após o fechamento da etapa 1.
> Todo número aqui vem de simulação executada e registrada em `resultados/`,
> ou está explicitamente marcado como estimativa, projeção ou palpite.

---

## O que mudou desde a v1.0, em uma página

O dossiê v1.0 descrevia um neurônio de **7 transistores** cuja frequência era fixada
por `Cfb`, `VDD` e `Iin`, com `Cmem` irrelevante. Nada disso sobreviveu inteiro.

| | v1.0 (nível 1) | v2.0 (sky130, medido) |
|---|---|---|
| Dispositivos por neurônio | 7 | **9** (mais 2 espelhos de polarização) |
| Consumo por neurônio | não medido | **6,03 nW** · 43,2 pJ/disparo |
| Ganho f–I | 17,5 Hz/pA | **13,89 Hz/pA** |
| Frequência no nominal | 158 Hz | **139,58 Hz** |
| `Cmem` controla f? | não (84% de cancelamento) | **sim** (sobram 15%) |
| Quem mais fixa a frequência | `Cfb`, `VDD`, `Iin` | + `Mrst`, `Cmem`, `IB1` |
| Fator do modelo analítico | 1,76× | 1,99× |

Quatro coisas que o v1.0 não sabia e que mudam o planejamento das etapas seguintes:

1. **O `Mrst` fixa a frequência.** 32× em `Wrst` produz 2,3× em frequência. O dossiê
   o tratava como detalhe de implementação.
2. **A topologia precisou de fome de corrente assimétrica** (só o PMOS, nos dois
   estágios) para caber no orçamento de energia. Isso acrescentou dois espelhos, e
   espelho de corrente é dos dispositivos mais sensíveis a descasamento que existem.
3. **`Cmem` controla a frequência**, logo descasamento de capacitor vira dispersão
   de frequência — caminho que não existia no mapa de riscos.
4. **A membrana vai abaixo do terra** (−0,128 V), o que polariza diretamente a junção
   de dreno do `Mrst` e injeta portadores no substrato. Risco de acoplamento entre
   vizinhos, não previsto.

---

## Etapa 0 — Neurônio em ngspice · **CONCLUÍDA E REVALIDADA**

Fechou duas vezes: uma em 2026-09-06 com os números originais, outra depois da
revalidação que os derrubou.

**O que ela ensinou que não estava no plano:** que o `abstol` padrão do ngspice
(1e-12 A = 1 pA) é da ordem do próprio sinal, e que sem apertá-lo — junto com o
`trtol`, cujo padrão de 7 relaxa o controle de erro de truncamento — todo número é
ruído numérico com aparência de medida. O jitter interno era de 22% num circuito
determinístico onde o correto é 0,01%.

Esse erro é o **erro fundador do projeto**, e reapareceu duas vezes em outra forma:
como `reltol` comparado ao pico de um ramo, e como limiar fixo de detector de
disparo contra um pulso colapsado. A lição generalizada está no `CLAUDE.md` §7.

---

## Etapa 1 — PDK SkyWater 130 nm · **CONCLUÍDA em 2026-09-07**

Seis critérios de saída, todos fechados. Detalhes em `resultados/2026-09-07_*`.

**O que ela ensinou:** que a migração de modelo não é tradução. O consumo caiu 14×
por um mecanismo que ninguém previu (Vth maior desloca `n1` e fecha a janela de
curto do 2º estágio), e o achado central do projeto se inverteu.

**Ressalvas abertas, nenhuma bloqueante:**
- Curvatura de −2,53% da f–I em 1 pA, sem explicação. Duas hipóteses derrubadas por
  medida direta (fuga e janela de histerese). Não é critério de saída de etapa nenhuma.
- A projeção térmica usa só o patamar de fuga e ignora que a injeção de junção abaixo
  de zero também cresce com T, e mais rápido. Os dois termos crescem em sentidos
  opostos. Só a etapa 3 resolve.

---

## Etapa 2 — Monte Carlo · **PRÓXIMA · maior risco do projeto**

**Pergunta:** com variação de fabricação, qual a dispersão de frequência entre
neurônios nominalmente idênticos?

**O que mudou em relação ao plano v1.0.** O dossiê previa varrer o descasamento de
7 transistores. O circuito atual tem 9, e ganhou três caminhos que não estavam no mapa:

| Caminho | Por que importa | Descoberto em |
|---|---|---|
| Espelhos `Mbp1` / `Mbp2` | `IB1` fixa a taxa de `n1`; espelho descasado = corrente descasada = frequência descasada | etapa 0, fome de corrente |
| `Mrst` | Fixa a frequência (32× em `Wrst` → 2,3× em f) e é o dispositivo crítico do canto quente | etapa 0, varredura de `Wrst` |
| `Cmem` e `Cfb` | `Cmem` controla f no PDK; dispersão de capacitância vira dispersão de frequência | etapa 1, varredura de `Cmem` |

**Verificar antes de rodar:** se os modelos estatísticos do sky130 oferecem variação
de capacitância além da de dispositivo. Se não oferecerem, isso precisa ser dito
explicitamente como limitação do resultado, não silenciado.

**Instrumentação — o que a etapa 1 já obriga:**
- Bloco `.options` de tolerância. Sem ele o resultado é inválido.
- `.nodeset` nos nós de referência dos espelhos, com os valores calculados.
- Limiar adaptativo no detector de disparo, nunca fixo.
- Corrente estática por ponto de operação DC, nunca por média de transiente.

**O ponto de decisão, conforme dossiê §8.1.** Se a dispersão for pequena (~5%), o
projeto segue. Se for grande (≥40%), cada neurônio precisa de calibração individual,
o que muda a arquitetura do chip inteiro. Essa decisão **não é do executor**.

**O que a decisão agora tem de entrada, e não tinha:** três requisitos de área que se
somam — transistores maiores para casar, anel de guarda contra acoplamento por
substrato (etapa 8), e o mínimo de 14 neurônios por ramo de referência para o
consumo fechar.

---

## Etapa 3 — Cantos de processo

**Pergunta:** funciona nos cantos `ss`/`ff`/`sf`/`fs`, na faixa de temperatura, com
VDD ±10%?

**Pré-requisito não resolvido, e é decisão do Saulo:** a faixa térmica real. Os
−40 °C e 125 °C do dossiê v1.0 nunca foram justificados — são a faixa automotiva
herdada por convenção. Um drone de busca e resgate com chip abaixo de 1 mW
dificilmente chega a 125 °C de junção. **A resposta muda o veredito da etapa.**

**A tesoura.** Duas restrições apertam de lados opostos:

- Por cima, o consumo. No sky130 deixou de apertar: a potência fica entre 4,30 e
  13,67 nW de 1 a 100 pA, sem cruzar os 100 nW. O teto de 54 pA era artefato do
  nível 1 e foi revogado.
- Por baixo, a fuga térmica. Com os 56 fA medidos em operação, ela alcança 1 pA
  entre 60 e 69 °C, 10 pA entre 87 e 102 °C, 100 pA entre 113 e 135 °C.

**Como medir, e não como projetar:** a projeção acima escala só o patamar de fuga.
Ignora que a injeção de junção abaixo de zero cresce mais rápido, por ser condução
direta, e tem sinal oposto. A etapa 3 precisa medir a **curva inteira** de fuga em
temperatura, não escalar um número.

Vigiar aqui também a pendência 15a (latch-up): 3,7 pA está ~9 ordens de grandeza
abaixo do necessário a 27 °C, mas é condução direta de junção e cresce depressa.

---

## Etapa 4 — Dois neurônios e uma sinapse

**Pergunta:** um neurônio consegue fazer o outro disparar de forma confiável?

**A decisão que esta etapa carrega, e que o dossiê v1.0 não continha:** onde mora o
peso sináptico.

Um peso analógico é uma tensão num capacitor, e capacitores vazam — não pelo
dielétrico, mas pelos transistores ligados a eles. Um capacitor de 100 fF guarda
100 fC; com fuga de 1 pA ele se esvazia em 0,1 s, com 1 fA em 100 s. Reter por um
dia exigiria ~1 aA, da ordem de seis elétrons por segundo. Não existe transistor
comum que vaze tão pouco.

Três saídas, e só a terceira está disponível no sky130 padrão:
- **Porta flutuante** — carga presa atrás de isolante, retenção de anos. Exige tensão
  alta para escrever, escrita lenta, desgaste, e processo que suporte. Foi a solução
  histórica (Caltech, anos 90). Não disponível.
- **Dispositivos memristivos** — a resposta certa no papel, área de pesquisa ativa.
  Não disponível.
- **Peso digital de poucos bits ao lado da sinapse**, com um pequeno conversor
  gerando a corrente. Disponível.

**Por que a terceira não destrói as assembleias neurais.** O que a assembleia precisa
é que a regra de aprendizado seja **local** (a sinapse decide a partir da atividade
dos dois neurônios que liga, sem árbitro global), que o tempo siga **contínuo e
assíncrono**, e que haja **recorrência** suficiente. Nenhuma dessas três exige que o
peso seja analógico. Um contador de poucos bits ao lado da sinapse é tão local
quanto uma tensão num capacitor.

Há inclusive argumento de que a sinapse biológica seja discreta — potenciação
tudo-ou-nada em sinapses individuais, com a força graduada emergindo da média de
muitas. **Não verificado nesta investigação; conferir Fusi e a literatura de sinapse
binária antes de virar decisão.**

**O custo real não é a natureza do aprendizado — é a densidade.** Célula de memória
mais conversor ocupam muito mais área que um transistor com um capacitor. Assembleia
é fenômeno de conectividade densa; menos sinapses por neurônio significa assembleias
mais pobres. Isso é mensurável, e só aqui.

---

## Etapa 5 — Detector de coincidência

**Pergunta:** qual a janela temporal, e ela é estável nos cantos?

Sem mudanças em relação ao v1.0. Herda de tudo o que veio antes: a janela depende de
constantes de tempo, que dependem de correntes de polarização, que a etapa 2 dirá o
quanto variam entre neurônios.

---

## Etapa 6 — Arquitetura AER em FPGA · ~R$ 300

**Pergunta:** quantos spikes por segundo o barramento aguenta antes de saturar?

**Esclarecimento conceitual que vale registrar,** porque a intuição errada é comum:
não existe um "leitor de padrão" que fotografe o estado dos neurônios. Uma varredura
periódica consumiria energia com a cena parada, destruindo a premissa do projeto. O
padrão não é lido — é **continuado**. Cada disparo emite um pacote com o endereço de
origem; neurônio que não disparou não emite nada e não custa nada. A saída de um chip
é a entrada de outro, sem tradução no meio.

**Ordem de grandeza, palpite não medido:** mil neurônios a 100 Hz médios dariam 10⁵
eventos/s; endereçar mil neurônios pede 10 bits — cerca de 1 Mbit/s. Trivial em
vazão média. O problema do AER nunca é a média: é o **pico**, quando muitos disparam
ao mesmo tempo e a arbitragem engarrafa.

**Ponto de decisão (dossiê §8.1):** o limite de vazão define quantos neurônios por
chip fazem sentido, e precisa ser conhecido **antes do layout**.

---

## Etapa 7 — Localizador sonoro · ~R$ 500

**Pergunta:** o sistema aponta a direção de um som real?

Primeira etapa com mundo físico. Critério do dossiê: bater palma de um lado, o canal
correto responde.

**Ponto de decisão (dossiê §8.1):** se funcionar, decidir entre buscar silício ou
permanecer em FPGA. **FPGA é suficiente para muitas aplicações e evita todo o risco
de fabricação.** Esta é a rampa de saída legítima do projeto, e está no plano desde
a v1.0.

---

## Etapa 8 — Layout e verificação

**Pergunta:** o desenho respeita as regras, e os parasitas mudam o comportamento?

**Entradas novas, que o v1.0 não tinha:**
- **Anel de guarda** contra o acoplamento por substrato (pendência 15b). A membrana
  vai a −0,128 V, polarizando diretamente a junção de dreno do `Mrst`, que injeta
  3,7 pA no substrato. Em lógica digital, onde o sinal é µA, isso é ruído
  irrelevante; aqui **o sinal também é da ordem de pA**, então diafonia de pA é
  sinal inteiro no vizinho errado. Anel de guarda custa área.
- **Técnicas de casamento** — centroide comum, dummies — dimensionadas pelo que a
  etapa 2 exigir.
- **Capacitores reais.** `Cmem` e `Cfb` são ideais em todas as simulações até aqui.
  MiM fica nas camadas superiores de metal e **pode se sobrepor aos transistores**,
  possivelmente sem custar área extra — a confirmar lendo a densidade em fF/µm²
  direto do PDK.
- **Ctot medido é 129,71 fF** contra 120 fF de `Cmem` + `Cfb`: sobram 9,7 fF de
  porta e parasitas. O layout vai acrescentar mais, e agora isso muda a frequência.

---

## Etapa 9 — Tiny Tapeout · ~US$ 100–400

**Pergunta:** o neurônio funciona em silício fabricado?

**Estimativa de capacidade** (premissas explícitas, não medida): área ativa dos 9
dispositivos = 15,5 µm²; layout analógico com casamento multiplica por 3 a 5; o
crescimento por descasamento é a incógnita que a etapa 2 vai fixar. Apostando em
150 a 300 µm² por neurônio, e com um bloco analógico de 1×2 tiles (160×200 µm) a
50% de aproveitamento: **da ordem de 50 a 100 neurônios**.

O dossiê v1.0 dizia "dezenas de neurônios". Confere.

**O que esta etapa realmente compra**, e é mais que o silício: a bancada de medida.
Chegar à etapa 10 sem saber medir dispersão de frequência entre neurônios reais
seria pagar caro por dados que não se sabe ler.

---

## Etapa 10 — Shuttle MPW

**Pergunta:** a arquitetura completa funciona integrada?

**Custo corrigido.** O v1.0 estimava US$ 5–10 mil. Os preços atuais:
- **ChipFoundry** (herdou o chipIgnite da efabless): US$ 14 950 por projeto,
  incluindo 100 peças em QFN; +US$ 3 000 por 50 pastilhas nuas. Prazo ~5 meses.
  Dois shuttles em 2025, três em 2026.
- **Cadence + SkyWater:** US$ 10 000 a 12 000 por bloco, conforme a opção de processo.

Ordem de grandeza certa no v1.0, valor desatualizado por ~2×.

**Não incluído no preço, e costuma dobrar o orçamento de quem faz pela primeira
vez:** encapsulamento além das 100 peças, placa de avaliação, e principalmente
**a bancada de teste**.

**Capacidade estimada:** 10 mm² de área útil a 50% de aproveitamento, com 150 a
300 µm² por neurônio, dão **15 a 30 mil neurônios**. O v1.0 dizia "milhares".
Confere. Mas o que decide se a área é preenchida não é dinheiro — é a etapa 6 dizer
quantos o barramento consegue servir. O preço é por projeto, não por neurônio.

**Nó avançado está descartado**, com motivo: a área é dominada por capacitores e por
casamento, e nenhum dos dois encolhe com o nó; a fuga piora, e ela é a restrição que
aperta por baixo; a tensão de alimentação cai para ~0,7 V, insuficiente para a
excursão analógica; e o custo sobe três ordens de grandeza (máscaras de US$ 10–20
milhões em 3 nm).

---

## Três pontos de revisão humana externa

Revisão que chega no fim encontra os erros caros tarde demais. Os momentos são
**antes de cada compromisso irreversível**:

| Antes de | Por quê |
|---|---|
| Etapa 6 | Fixa a arquitetura de comunicação, e o resultado define neurônios por chip |
| Etapa 8 | Depois do layout, mudar topologia significa refazer tudo |
| Etapa 9 | Depois do tapeout não há correção naquele lote |

**Onde procurar:** comunidade sky130 / Tiny Tapeout (custo zero, alta taxa de
resposta a pergunta específica com dados); grupos acadêmicos de engenharia
neuromórfica; grupo de microeletrônica em universidade brasileira (presencial e
continuado, o mais valioso a médio prazo).

**O que preparar antes:** uma página do que o sistema faz e do que explicitamente não
faz; a escada de etapas com o estado atual; a lista de decisões com o motivo de cada
uma. Isso transforma "olha meu projeto" em "confira estas decisões".

**As perguntas que valem**, porque dependem de ter visto silício voltar da fábrica:
um chip homogêneo configurável se sustenta na prática ou faz tudo mal? A calibração
por polarização externa escala para milhares de neurônios, ou o roteamento das
tensões come a área? Quanta área o descasamento realmente exige?

---

## O que não mudou

O princípio de escopo do dossiê v1.0 sobreviveu a tudo e é o que fez este projeto
avançar: **uma pergunta por vez, respondida antes da próxima.** Cada etapa custa ~10×
a anterior e detecta uma classe de erro que a anterior não via. Nunca subir um degrau
com erro escondido no anterior.

E a regra que produziu todos os resultados desta série: **um resultado que ninguém
tentou derrubar não é um resultado.**
