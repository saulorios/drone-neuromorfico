# Drone Neuromórfico

Neurônios analógicos de pulsos em silício para detecção de eventos com consumo muito
baixo, aplicados a busca e resgate aérea. Registro de projeto em estágio inicial:
**nada foi fabricado**. Todo número aqui vem de simulação ou de literatura.

O contexto completo está em [`CLAUDE.md`](CLAUDE.md) (estado, decisões, convenções) e
no dossiê técnico em [`docs/dossie.pdf`](docs/dossie.pdf).

## Estado

Etapa 0 concluída: neurônio axon-hillock de 7 transistores simulado em ngspice, curva
f–I linear com ganho de 17,5 Hz/pA. Modelos MOSFET genéricos de nível 1 — **não** o PDK
SkyWater, portanto sem condução sub-limiar. Há ressalvas abertas sobre esses resultados:
ver `CLAUDE.md` §5 antes de citá-los.

Etapa 1 (migração para o PDK SkyWater 130 nm) em planejamento.

## Como rodar

Pré-requisitos (nenhum está instalado nesta máquina em 2026-09-06):

```bash
sudo apt install ngspice          # ngspice 42 nos repositórios do Ubuntu 24.04
pip install numpy matplotlib
```

Bateria completa de simulações e gráficos:

```bash
RUN_TAG=$(date +%F)_minha_rodada python3 scripts/run_sims.py
RUN_TAG=$(date +%F)_minha_rodada python3 scripts/plots.py
```

Os resultados vão para `resultados/$RUN_TAG/`. Simulação avulsa do netlist:

```bash
ngspice -b spice/neuronio.cir
```

Variáveis de ambiente reconhecidas: `NGSPICE_BIN` (padrão `ngspice` do PATH) e
`RUN_TAG` (padrão `rodada_atual`).

## Estrutura

```
CLAUDE.md      contexto do projeto, lido automaticamente pelo Claude Code
docs/          dossiê, caderno de decisões, log datado
spice/         netlist, modelos/PDK, testbenches
scripts/       execução das simulações e geração de gráficos
resultados/    dados brutos e figuras, uma pasta datada por rodada
fpga/          Verilog do roteador AER (etapa 6)
```

## As duas regras

1. Nunca aceite um resultado de simulação sem antes tentar derrubá-lo.
2. Todo número precisa de unidade e de denominador.
