# Drone Neuromórfico

Neurônio analógico em **SkyWater 130 nm** para detecção de eventos em tempo contínuo,
com consumo desprezível. Registro completo de projeto — incluindo o que foi refutado.

**Nada foi construído em hardware.** Todo número deste repositório vem de simulação ou de
literatura, e a origem está sempre indicada.

---

## O que o projeto é

Um neurônio *integra-e-dispara* de 9 dispositivos (topologia axon-hillock, Mead 1989, com
fome de corrente assimétrica), migrado para o PDK aberto sky130 e caracterizado com
denominador em cada número. A aplicação-alvo é **detecção de eventos em busca e resgate**:
voar por horas e sinalizar quando algo se destaca do padrão de fundo.

Estado medido no ponto nominal (`Iin` = 10 pA, canto `tt`, 27 °C):

| | |
|---|---|
| consumo por neurônio | **6,03 nW** |
| energia por disparo | **43,2 pJ** — dentro da faixa publicada de 1 a 100 pJ |
| ganho f–I | 13,89 Hz/pA, R² = 0,999996 |
| faixa útil | `Iin` de 1 a 100 pA → f de 14 Hz a 1,39 kHz |

## O que o projeto explicitamente NÃO é

O nicho é estreito de propósito. **Não** é reconhecimento de objetos, identificação de
pessoas, nem compreensão de cena — nessas tarefas uma GPU comum é largamente superior.

E uma ressalva que o próprio repositório registra contra si: o neurônio **não** é um
dispositivo orientado a evento. Dos 85,4 nW medidos no nível 1, ~95% eram piso estático.
O argumento de consumo deste projeto é "piso estático baixo o bastante", **não** "consumo
proporcional à atividade" — são justificativas diferentes, com implicações diferentes para
a arquitetura.

## Estado atual

| Etapa | | |
|---|---|---|
| 0 | Neurônio em ngspice, modelos nível 1 | **concluída e revalidada** |
| 1 | Migração para o PDK sky130 | **concluída** |
| 2 | Monte Carlo / descasamento | **em andamento** — instrumento validado, a medida não |
| 3–10 | Cantos, par acoplado, coincidência, AER/FPGA, layout, tapeout | não iniciadas |

A etapa 1 fechou **invertendo o achado central do projeto**: `Cmem` não controlava a
frequência nos modelos de nível 1, e controla no PDK. O registro da inversão — e do motivo
pelo qual a formulação antiga parecia certa — está preservado.

## Por onde começar

1. **[`docs/etapas.md`](docs/etapas.md)** — o plano de dez etapas, v2.0. Uma pergunta por
   etapa, respondida antes da próxima. Substitui a Parte 7 do dossiê.
2. **[`CLAUDE.md`](CLAUDE.md)** — a memória do projeto: resultados com denominador,
   decisões tomadas com o motivo, ressalvas abertas, e as armadilhas numéricas que já
   custaram caro.
3. **[`docs/decisoes.md`](docs/decisoes.md)** — log datado do que mudou e por quê.
4. **[`docs/dossie_v1.0.pdf`](docs/dossie_v1.0.pdf)** — o dossiê original de setembro
   de 2026, preservado como registro do que se acreditava. Duas de suas partes já não valem,
   e isso está marcado.

## Como o repositório é organizado

```
resultados/<AAAA-MM-DD_tag>/    uma pasta datada por rodada — nunca sobrescrita
  previsao_pre_registrada.md    o que se esperava, ANTES de rodar
  <relatorio>.md                o que se mediu, com o placar contra a previsão
  <figura>.png                  o gráfico
  raw/*.cir                     os netlists — versionados, e regeneram o bruto
spice/  scripts/  docs/  fpga/
```

**Saída bruta do ngspice nunca é versionada.** Os `.cir` ficam no repositório e regeneram
o bruto: rode o script de análise e ele executa o netlist que falta.

O PDK sky130 também não é versionado (~127 MB). A instalação enxuta está documentada no
`CLAUDE.md` §2.

## Duas regras que produziram estes resultados

**Nunca aceite um resultado de simulação sem antes tentar derrubá-lo.** Qual seria o valor
previsto por um modelo analítico independente? Sobrevive a mudar `tstep`, `tstop`, o método
de integração? Um resultado que ninguém tentou quebrar não é um resultado — é uma
expectativa com aparência de dado.

**Todo número precisa de unidade e de denominador.** "18% de deriva" não significa nada;
"18% pico-a-pico de f, denominador f em VDD nominal, VDD variado ±10%" significa.

## Refutações ficam registradas, não apagadas

O motivo de um descarte vale mais que o descarte, e este repositório trata isso como regra.
Já foram refutadas, com autor e data: corrente de fuga causando zona morta (era ruído
numérico); overshoot da saída como causa do fator 1,76× (era reset incompleto); fome de
corrente simétrica (destrói a razão entre as correntes); o cancelamento que tornava `Cmem`
irrelevante (não sobrevive ao PDK); e, na etapa 2, que `set rndseed` fixasse o sorteio do
Monte Carlo (não fixa — os `.model` são avaliados antes do `.control`).

Cada uma custou uma rodada. Cada uma está escrita com o motivo.

---

Autoria: Saulo Rios. Assistência de engenharia e execução das simulações: Claude (Anthropic).
