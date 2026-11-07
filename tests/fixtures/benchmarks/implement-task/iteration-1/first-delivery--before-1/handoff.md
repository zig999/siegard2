# /implement-task — task/fees/compute-late-fee (lending)

## Nós escritos

- `implementation/fees/compute-late-fee` (pin `sha256:9fd898ce6460f6ca63d7a9b075f82333fa44022962010552f74b048492b35b1c`)
- `proof/fees/compute-late-fee` (pin `sha256:cd9330ccce5647f21aa31a986562e3cb46ac03167a6b10923097cdef389e09f8`)
- Primeira entrega, não é re-entrega.

Decidido e divulgado, sem pergunta:
- slug `lending`: a invocação não nomeou nenhum e `work/` contém exatamente uma iniciativa, sem `closure.md`.
- target `app`: `siegard.json` declara exatamente um target.
- a raiz de entrega `delivery/lending` não existia e foi criada vazia, como a skill determina.
- a tarefa foi nomeada na invocação: `task/fees/compute-late-fee`.

## Arquivos que a entrega criou, modificou ou apagou (o file set do /review-change)

Relativos à raiz do target `app`:
- `lending/fees.py` (criado; `files` da implementação)
- `tests/test_fees.py` (criado; `tests` da prova)

`deliver.py --unrecorded` confirmou que os dois registros nomeiam todo caminho alterado sob `app`.
Fora do target: `delivery/lending/` (registros, runs, `delivery.json`) e `siegard-trace.json` (o bind).

## Critérios registrados como não atendidos

Nenhum. Os dois critérios estão `met: true`.

## Inferências e desvios

Inferências (implementação):
- Um empréstimo sem `returned_on` é recusado com `ValueError` em vez de receber uma multa — de: o objetivo da tarefa nomeia um empréstimo devolvido como entrada, e nenhum nó diz qual é a multa de um empréstimo não devolvido.
- A multa é respondida como `int` em centavos, e não como o `decimal` que o atributo `late_fee` da entidade Loan declara — de: o objetivo e os critérios da tarefa falam em centavos, e a regra PY-01 do standard exige dinheiro em centavos inteiros.
- A função recebe o registro `Loan` existente, e não um par de datas — de: o `must_not_duplicate` do inventário nomeia o registro Loan e suas datas em `lending/loans.py`.

Desvios: nenhum, em nenhum dos dois registros.

## Nós sem teste que os demonstre

Nenhum. `rules/lending/late-fee-per-overdue-day` é nomeado em `demonstrates` pelo teste `test_a_loan_returned_late_carries_100_cents_per_calendar_day_across_a_month_end`. A reivindicação é do autor da prova; quem a certifica é a revisão.

## O que a prova deixou sem provar, casos descartados, discordâncias

- `untested`: a recusa de um empréstimo sem `returned_on` por `ValueError` é comportamento inferido pela implementação que nenhum nó decide; registrada como não provada, sem teste que a fixe.
- `not_applicable`: empréstimo sem data de devolução (o objetivo e os critérios respondem só por um empréstimo devolvido); duas computações simultâneas sobre um empréstimo (função pura, nenhum nó fala de concorrência); valores grandes a ponto de transbordar (inteiros Python não transbordam e nenhum nó limita os dias de atraso).
- `contested`: nenhuma discordância.

## O que a implementação adiou e o que precisa continuar funcionando

- Adiado: o registro `Loan` em `lending/loans.py` não tem atributo `late_fee`, embora `domain/lending/loan` declare um — guardá-lo no registro vai além do objetivo da tarefa e entra num nó que a tarefa não implementa.
- Preservado: o registro `Loan` de `lending/loans.py` mantém seus campos e defaults, e `tests/test_loans.py` continua passando sobre ele.

## Trace

- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 binding, em `/tmp/itbench/runs/first-delivery-base1/p/siegard-trace.json`).
- Nenhum binding recusado. O bind não imprimiu recibo de bindings obsoletos, então não há invocação `/reconcile` a entregar.

## Passos executados inline

Os passos 3 (implement) e 5 (prove) rodaram inline, aplicando `agents/task-implementer.md` e `agents/test-author.md` no lugar, porque esta sessão não pode criar subagentes. Os dois registros dizem isso em `## Notes`. A separação entre quem escreveu o código e quem escreveu os testes, portanto, não existiu nesta entrega: a revisão é o primeiro olhar independente.

## Saída final do validador

```
derived /tmp/itbench/runs/first-delivery-base1/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard

- `app/standard.yaml` (`at: standard.yaml` a partir da raiz do target), resolvido pelo campo `standard` de `/tmp/itbench/runs/first-delivery-base1/p/siegard.json` — a invocação não nomeou nenhum.
- Pin: `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, nos dois registros.
- Desvios divulgados: nenhum.
- Pressupõe: nada; a árvore contém tudo o que ele precisa.
- Autoriza 0 dependências diretas.
- `--outstanding` (com `--scope`) imprimiu: `standard.yaml (target app): pinned by 1 record(s); an invocation naming no standard now writes source these rules will still be read against`. Nenhum registro sem pin ou com outro standard.

## Runs capturados

- `delivery/lending/run/fees-compute-late-fee-build` — passed (`build=python3 -m compileall -q lending`).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (`build`, depois `test=python3 -m pytest -q tests`).
- Nenhum run vermelho; nenhum diagnóstico.
- Não rodou: a fase setup — o registry não declara passo com papel `install` ("setup: nothing runs — no step carries the role this phase needs").

## Dependências instaladas

Nenhuma.

## O que o /review-change ainda faz que esta invocação não fez

Roda os mesmos passos de novo sobre a mudança inteira, não sobre uma tarefa só, e julga: se os testes provam os critérios, se o código declara só o que a especificação contém, se segue o mesmo standard (PY-01, decidida por leitura), e por que algo falhou. Um suite verde aqui é verde sobre uma tarefa.

## Handoff

O `/review-change` hoje recusa: `git status --porcelain -- /tmp/itbench/runs/first-delivery-base1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make`. Ele só abre depois que você commitar o estado pendente desta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`). Commitar é decisão sua.

`/review-change` invocation ready to paste (depois do commit):

```
/review-change /tmp/itbench/runs/first-delivery-base1/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard /tmp/itbench/runs/first-delivery-base1/p/app/standard.yaml
```

Depois disso, pare: `git diff` sobre a raiz do target e a raiz de entrega é a revisão, e pertence a uma pessoa.
