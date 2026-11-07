# /implement-task — task/fees/compute-late-fee (lending, alvo `app`)

## Registros escritos

- `delivery/lending/implementation/fees/compute-late-fee.md` (implementation) — pin `sha256` impresso pelo writer na etapa 4.
- `delivery/lending/proof/fees/compute-late-fee.md` (proof) — pin `sha256:20bc932c27e0cc17b5e6203132df6ca575b7b851cad5f8845f2ff57c2dcf46cb`.
- Primeira entrega: não é re-delivery (nenhum registro existia no caminho da tarefa; nenhum `stands`).

## Arquivos que a entrega criou (relativos ao target source root `app`)

- `lending/fees.py` — implementation `files`: responde a multa de um empréstimo devolvido, 100 centavos por dia corrido após o vencimento, 0 se devolvido no prazo.
- `tests/test_fees.py` — proof `tests`: os quatro testes abaixo.

`deliver.py --unrecorded` confirmou: `every path this tree changed under app is named by the 2 record(s) given`.

Fora do alvo, a etapa 8 escreveu `siegard-trace.json` na raiz do projeto.

## Critérios registrados como não atendidos

Nenhum. Os dois critérios estão `met: true` no registro de implementação.

## Inferências e divergências registradas

- Inferência (implementation): «a loan not yet returned is refused with a ValueError rather than answered a fee.» — de: «the rule states the fee of a loan returned after its due date and states nothing of a loan still out».
- Divergências: nenhuma, em nenhum dos dois registros.

## Nós que nenhum teste demonstra

- `rules/lending/late-fee-per-overdue-day` — nenhum teste carrega `demonstrates`. O `untested` da proof diz: «its fact holds over every pairing of a due date and a later return, a set nothing enumerates, so no finite test decides it whole; the tests above prove the task's criteria at their boundaries and one representative of each class, and claim no node.» A certificação desse nó fica para a revisão.

## O que a proof deixou sem prova, casos descartados e contestações

- `untested`: o nó acima; e a inferência do `ValueError` para empréstimo não devolvido — nenhum nó decide esse comportamento, então não é fixado por teste.
- `not_applicable`: empréstimo sem vencimento ou ausente; dois cálculos simultâneos sobre o mesmo empréstimo; dependência que falha ou demora; coleção vazia ou duplicata — cada um com o porquê no registro.
- `contested`: nenhum.

Testes escritos (`tests/test_fees.py`):
1. `test_a_loan_returned_on_its_due_date_carries_no_late_fee` — fronteira do critério 1 (devolução no dia do vencimento).
2. `test_a_loan_returned_before_its_due_date_carries_no_late_fee` — classe de devoluções antecipadas.
3. `test_a_loan_returned_one_day_after_its_due_date_carries_100_cents` — fronteira do critério 2 (primeiro dia de atraso).
4. `test_a_loan_returned_late_across_a_month_end_carries_100_cents_per_calendar_day` — vários dias, contados através da virada do mês (30/jan → 03/fev = 400).

## O que a implementação adiou e o que deve continuar funcionando

Nada adiado. `lending/loans.py` não foi alterado; `tests/test_loans.py` continua passando na suíte.

## Rastro (trace)

- Vinculado: `rules/lending/late-fee-per-overdue-day` a 1 arquivo (`lending/fees.py`), em `/tmp/it3/runs2/compaction-resume/p/siegard-trace.json`.
- Nenhuma vinculação recusada; nenhum recibo de vinculações obsoletas (stale-bindings) foi impresso, então nenhuma invocação de `/reconcile` é devida por esta entrega.

## Etapas executadas inline

Esta sessão não pode criar subagentes. A etapa 3 (Implement, disciplina de `agents/task-implementer.md`) e a etapa 5 (Prove, disciplina de `agents/test-author.md`) rodaram inline, na mesma sessão. Os testes foram escritos no mesmo contexto que escreveu o código — a separação entre os dois produtores não vale para esta entrega, e a nota da proof registra isso. A revisão é o que lê os dois de forma independente.

## Recomendação

A revisão (`/review-change`) é a próxima etapa, mas `door.py --check` a recusa como a árvore está:
`git status --porcelain -- /tmp/it3/runs2/compaction-resume/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make`.

- Recomendado (derivado): fazer o commit desta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`) e então rodar `/review-change`.
- Critério: uma porta que o próprio ponto de entrada recusa é `precondition unmet`; o commit é o ato que remove a recusa.
- Fato decisivo: a recusa acima, sobre a raiz de entrega não commitada.
- Fato que reverte: a raiz de entrega já estar commitada — então a revisão é a porta a tomar direto.
- `/reconcile`: não verificado por script; não é devido, pois nenhum recibo de vinculações obsoletas foi impresso. Também recusa arquivos não commitados.

O commit é da pessoa; esta skill nunca altera o estado do git.

## Saída final do validador (verbatim)

```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido

- Resolvido do arquivo do projeto: `siegard.json` → `app/standard.yaml` (`at: standard.yaml` relativo ao alvo), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Divergências declaradas contra ele: nenhuma.
- Pressupõe: nada que a tarefa produza; a tarefa não declara `produces`, e `deliver.py --standard --against app` passou limpo.
- `--outstanding` não imprimiu registros sem padrão ou com outro padrão.

## Execuções capturadas

- `delivery/lending/run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (build: `python3 -m compileall -q lending`; test: `python3 -m pytest -q tests`).
- Nenhuma execução falhou.
- Setup: não rodou — o registro não declara comando de papel `install`.

## Dependências instaladas

Nenhuma.

## O que `/review-change` ainda faz

Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se o código afirma só o que a especificação contém (e reestampa as vinculações que isso libera), se segue o padrão, e por que algo falhou. Uma suíte verde aqui cobre uma tarefa.

## Handoff

Depois do commit desta entrega, pronto para colar:

```
/review-change /tmp/it3/runs2/compaction-resume/p target app slug lending task task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```
