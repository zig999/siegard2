# /implement-task — task/fees/compute-late-fee (lending, target app)

## Registros escritos

- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md` (pin `sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b`)
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md` (pin `sha256:497b47d1084c9e83afeeab109352fdf9f72b1fd795b6f9b5db1b9fdcc719dc66`)

Primeira entrega: não é re-delivery (nenhum registro existia no caminho da task).

## Caminhos que a entrega criou ou alterou (relativos a `app/`)

- `lending/fees.py` — criado (implementation `files`)
- `tests/test_fees.py` — criado (proof `tests`)

`deliver.py --unrecorded` confirmou: "Every path this tree changed under app is named by the 2 record(s) given".
Fora do target, a entrega escreveu ainda `delivery/lending/` (registros, runs, `delivery.json`) e `siegard-trace.json`.

## Critérios registrados como unmet

Nenhum. Os dois critérios estão `met: true` no implementation record.

## Inferências e divergências registradas

- Inferência (implementation): "a loan not yet returned is refused with a ValueError rather than answered a fee." — de: "the rule states the fee of a loan returned after its due date and states nothing of a loan still out".
- Divergências: nenhuma, em nenhum dos dois registros.

## Nodes que nenhum teste demonstra

- `rules/lending/late-fee-per-overdue-day` — o proof o coloca em `untested`: "its fact holds for every overdue day count, an unbounded set the node does not enumerate, so no finite test decides it whole; the criterion tests exercise the first overdue day and several days across a month boundary without claiming the node." Nenhum teste carrega `demonstrates`; a certificação desse node fica para a leitura do `/review-change`.

## O que o proof deixou sem prova, casos de borda descartados, discordâncias

Sem prova (`untested`):
- o node acima;
- "the refusal of a loan not yet returned with a ValueError: an inference the implementation recorded about behavior that no node decides, so it is left unproven rather than pinned."

Casos de borda descartados (`not_applicable`):
- devolução datada antes do empréstimo — nenhum critério ou node diz o que esse loan carrega;
- loan ausente — o objetivo da task é um loan devolvido dado;
- valores fracionários ou arredondamento — dias inteiros a centavos inteiros;
- dependência que falha ou demora, e dois cálculos simultâneos — o cálculo lê um loan e nenhuma dependência.

Discordâncias (`contested`): nenhuma.

## O que a implementação adiou, e o que deve continuar funcionando

Nada adiado. O implementation record não declara nada que deva continuar funcionando além do que a suíte já cobre; `tests/test_loans.py` existente passou na suíte.

## Trace

- `rules/lending/late-fee-per-overdue-day` vinculado a `lending/fees.py` (1 binding em `siegard-trace.json`).
- Nenhum binding recusado. Nenhum stale-bindings receipt impresso, então não há invocação de `/reconcile` a entregar.

## Passos executados inline

Sessão sem subagentes: os passos 3 (Implement, disciplina de `agents/task-implementer.md`) e 5 (Prove, disciplina de `agents/test-author.md`) rodaram inline neste mesmo contexto, cada um aplicando o arquivo do seu agente. O retorno do test-author foi escrito em arquivo e passado ao writer por `--from-text`. Source e testes, portanto, não foram escritos em contextos separados — a revisão deve pesar isso.

## Validador (saída final, verbatim)

```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard

- Resolvido do arquivo do projeto (`siegard.json` → `standard: app/standard.yaml`), registrado como `standard.yaml` relativo ao target, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, nos dois registros.
- Departures: nenhuma.
- Presupposes: o `deliver.py --standard` passou limpo antes de qualquer escrita; a árvore satisfaz o que o registry pressupõe.
- `--outstanding` não imprimiu linhas sobre registros sem standard ou com outro standard.

## Runs capturados

- `delivery/lending/run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (build, depois test: `python3 -m pytest -q tests`).
- Nenhum run vermelho. Setup não rodou: o registry não declara nenhum passo com role `install`.

## Dependências instaladas

Nenhuma.

## O que o `/review-change` ainda faz

Roda os mesmos passos sobre a mudança inteira, não sobre uma task; julga se os testes provam os critérios, se o source diz só o que a especificação contém, se segue o standard (PY-01 é `decided_by: reading`) e por que algo falhou. A suíte verde aqui cobre uma task.

## Handoff

O `/review-change` recusa hoje: "git status --porcelain -- /tmp/it3/runs/compaction-resume--before-1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". Antes dele, a pessoa commita esta entrega: `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/` e `siegard-trace.json`. Commitar é decisão da pessoa; esta invocação não toca o git.

Depois do commit, pronto para colar (o nome da revisão fica como slot):

```
/review-change /tmp/it3/runs/compaction-resume--before-1/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard standard.yaml review <review-name>
```
