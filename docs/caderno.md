# Caderno: decisões, descartes e coisas aprendidas

O `decisoes.md` registra *o que* mudou e *quando*. Este caderno é para o raciocínio mais
longo: alternativas consideradas e por que foram descartadas, intuições que se mostraram
erradas, e perguntas ainda em aberto.

---

## Intuições que se mostraram erradas

### "O capacitor de membrana define a constante de tempo do neurônio"

Falso nesta topologia, e a razão é bonita. Numa membrana biológica, ou num
integrador RC comum, aumentar a capacitância aumenta a constante de tempo. Aqui não.

A membrana precisa percorrer uma janela de histerese `ΔV` que é criada pelo próprio
degrau de realimentação através de `Cfb`. Esse degrau é um divisor capacitivo:
`ΔV = VDD · Cfb / (Cmem + Cfb + parasitas)`. A rampa, por sua vez, sobe a
`Iin / (Cmem + Cfb + parasitas)`.

O tempo de percurso é `ΔV` dividido pela inclinação — e o mesmo `Ctot` aparece no
numerador e no denominador:

```
T = Ctot · ΔV / Iin = Ctot · (VDD · Cfb / Ctot) / Iin = Cfb · VDD / Iin
```

`Cmem` desaparece. Não "quase se cancela": some. Quem manda na frequência é `Cfb`,
`VDD` e `Iin`.

A intuição errada tinha uma consequência de projeto errada junto: supunha-se que o
capacitor de membrana dominaria a área do neurônio no chip. Como ele deve ser pequeno,
a estimativa de área está invertida — o neurônio pode ser mais compacto que o previsto.

**O que `Cmem` de fato controla** é a excursão de sinal, e para pior: 25 fF dá 1,05 V de
excursão, 400 fF dá 0,079 V. Abaixo de ~0,2 V, descasamento entre transistores e ruído
de alimentação passam a dominar o comportamento. `Cmem` grande não compra lentidão;
compra fragilidade.

---

## Alternativas consideradas e descartadas

### Chips especializados por modalidade (um para áudio, outro para visão)

Descartado. Três motivos: (a) o gargalo real do sistema é a comunicação entre chips, e
separar modalidades encarece justamente as associações multissensoriais que se quer ter;
(b) a proporção necessária entre modalidades ainda é desconhecida, e chips fixos travam
essa proporção antes da hora; (c) três máscaras custam três vezes mais que uma.

Escolha adotada: um único chip com neurônios configuráveis por tensões de polarização,
replicado quantas vezes couber no orçamento de peso e energia. A modalidade vira
parâmetro de configuração, não silício. É a mesma escolha feita por Loihi, SpiNNaker e
Akida — o que é um bom sinal, mas não é prova.

Exceção legítima: a interface analógica de sensor (amplificador de microfone,
fotodiodos) é específica por modalidade e não configurável. Vai num chip de interface
pequeno e barato, separado do chip de neurônios homogêneo.

### Re-rodar a etapa 0 com nível 1 para refazer os números de física

Descartado em 2026-09-06. Os modelos nível 1 não descrevem a condução sub-limiar, então
qualquer número refeito com eles teria que ser refeito de novo na etapa 1.

Mas um re-rodar *de numérica* foi mantido: ver a pergunta em aberto sobre `abstol`
abaixo. Ele custa minutos, testa a ferramenta em vez do circuito, e as ressalvas 1 a 3
podem ser artefato de tolerância, não de física.

---

## Perguntas em aberto

- **De onde vem o fator 1,76×?** O modelo `T = Cfb·VDD/Iin` prevê 278 Hz em 10 pA;
  mediu-se 158 Hz. O modelo acerta *todas* as tendências — independência de `Cmem`,
  linearidade em `Iin`, escala com VDD dentro de 3% — e erra só a escala absoluta, o que
  aponta para um fator multiplicativo constante e não para um mecanismo faltando.
  Suspeita: a saída ultrapassa VDD no spike (visível no painel 1, ~1,9 V contra 1,8 V de
  alimentação) e o reset leva a membrana abaixo do ponto de equilíbrio; juntos, alargam
  a janela de histerese real além de `VDD · Cfb / Ctot`. Verificável medindo a janela
  diretamente em vez de inferi-la.

- **A curva f–I é mesmo linear?** Nunca foi testada — o R² era uma string. Com o
  intercepto observado, a reta prevê 181 Hz em 10 pA contra 158 Hz medidos. Ou há
  curvatura real, ou é o ruído numérico de ~10% do item 1 das ressalvas. Os dois casos
  têm consequências diferentes e precisam ser separados.

- **Quanto da frequência é rampa e quanto é reset?** Se o tempo de reset for uma fração
  grande do período, ele impõe um teto de frequência que a curva f–I ainda não alcançou,
  e a linearidade vai quebrar em correntes mais altas que 100 pA.

- **A dependência `f ∝ VDD` é fatal?** Ela é estrutural, não um ajuste ruim: sai direto
  da equação. Se a compensação exigir mudar a topologia (limitar a excursão de saída em
  vez de deixá-la ir de trilho a trilho), é melhor descobrir na etapa 1 do que na 8.

- **As ressalvas da etapa 0 são física ou são `abstol`?** O padrão do ngspice é
  `abstol = 1 pA`, e as simulações rodaram com `Iin` de 1 a 100 pA sem nenhum `.options`.
  No ponto de 1 pA, o sinal inteiro está dentro da tolerância de convergência; no ponto
  nominal de 10 pA, a tolerância é 10% do sinal — a mesma ordem do espalhamento
  observado entre execuções. O `gmin` padrão (1e-12 S) acrescenta mais ~0,9 pA de fuga
  parasita no nó `mem`. É uma explicação única e econômica para as ressalvas 1, 2 e 3,
  e é barata de testar. Enquanto não for testada, continua sendo hipótese: pode ser que
  o espalhamento venha só de `tstep` e a tolerância não tenha nada a ver.
