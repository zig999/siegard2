# Report — /implement-task task/fees/compute-late-fee

## Handoff (exactly what `handoff.py --render` printed)

```
lending · task 1/1 delivered · phase review
```

1. A taxa de atraso está entregue com a suíte verde; para a revisão rodar, falta o commit desta entrega.
   - **Recomendado** `commit`: Você faz o commit da entrega (código, testes, registros e trace) e depois roda a revisão. Derivada: a revisão recusa enquanto a entrega estiver sem commit, e o commit é seu. Mudaria se a entrega já estiver commitada.
   - `reconciliar`: Confere código contra especificação; nada pede isto agora.
   - `revisar`: Excluída: recusa enquanto a entrega estiver sem commit.
   - Se nenhuma for tomada: A entrega fica sem commit e sem revisão.

   ```
   /review-change /tmp/it3/runs2/first-delivery/p target app slug lending task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard standard.yaml
   ```

Relatório completo: /tmp/it3/runs2/first-delivery/p/.git/siegard/handoff/20261107T184438Z-implement-task.md

## Full report (saved through `handoff.py --save-report` at /tmp/it3/runs2/first-delivery/p/.git/siegard/handoff/20261107T184438Z-implement-task.md)

# /implement-task — task/fees/compute-late-fee (lending)

## Registros escritos
- `implementation/fees/compute-late-fee` e `proof/fees/compute-late-fee`, sob `/tmp/it3/runs2/first-delivery/p/delivery/lending`. Primeira entrega, não uma re-entrega.
- Entradas decididas por singleton, divulgadas: target `app` (único em `targets`); slug `lending` (única iniciativa em `work_root`, sem `closure.md`). O delivery root `delivery/lending` estava ausente e foi criado vazio.

## Caminhos que a entrega criou (conjunto de arquivos para /review-change)
- `lending/fees.py` (implementação)
- `tests/test_fees.py` (prova)
- `deliver.py --unrecorded`: every path this tree changed under /tmp/it3/runs2/first-delivery/p/app is named by the 2 record(s) given

## Critérios registrados como não atendidos
Nenhum.

## Inferências e divergências registradas
- Inferência: a função recebe o registro `Loan` e lê `due_on` e `returned_on`, em vez de receber as duas datas separadas — a partir da entrada `must_not_duplicate` do inventário (`lending/loans.py`) e do objetivo "Given a returned loan".
- Inferência: a taxa vive num módulo novo `lending/fees.py`, não em `lending/loans.py` — o inventário nomeia `lending/loans.py` como módulo do qual a área depende, e o epic `fees` é uma preocupação própria.
- Divergências: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre
Nenhum: `rules/lending/late-fee-per-overdue-day` é demonstrado por `test_a_loan_returned_days_late_across_a_month_end_carries_100_cents_per_calendar_day`.

## O que a prova deixou sem provar, casos descartados, discordâncias
- `untested`: nada.
- `not_applicable`: empréstimo ainda não devolvido (`returned_on` ausente) — o objetivo é um empréstimo devolvido e nenhum nó diz a taxa de um não devolvido; empréstimo renovado — a renovação move `due_on`, mesma classe; concorrência e dependência que falha — função pura sem dependência nem estado.
- `contested`: nada.

## Adiado e o que deve continuar funcionando
- Adiado: um `Loan` com `returned_on` igual a `None` não é tratado; `late_fee_cents` sobre ele levanta o `TypeError` da subtração de datas — o objetivo é um empréstimo devolvido e nenhum nó diz a taxa de um empréstimo não devolvido.
- `preserved`: ausente — a tarefa não alterou comportamento existente.

## Trace
- `trace.py --bind-record`: bound rules/lending/late-fee-per-overdue-day to 1 file(s); 1 binding(s) written at /tmp/it3/runs2/first-delivery/p/siegard-trace.json. Nenhuma ligação recusada; nenhum recibo de stale-bindings, portanto nenhuma porta `/reconcile` é devida por este bind.

## Passos executados inline
Os passos 3 (implementar) e 5 (provar) rodaram inline nesta sessão, que não pode criar subagentes: as disciplinas de `agents/task-implementer.md` e `agents/test-author.md` foram aplicadas no mesmo contexto, então o código e os testes foram escritos num único contexto. Os dois registros dizem isso em `## Notes`.

## Portas
- `/review-change`: excluída por enquanto — `door.py` respondeu `refuses`: "git status --porcelain -- /tmp/it3/runs2/first-delivery/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". O que a muda: a pessoa fazer o commit desta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`). O commit é da pessoa.
- `/reconcile`: não verificada por script; sem recibo de stale-bindings, nada aqui a pede.

## Saída final do validador
```
derived /tmp/it3/runs2/first-delivery/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard seguido
- Resolvido pelo arquivo do projeto (`siegard.json` → `standard: /tmp/it3/runs2/first-delivery/p/app/standard.yaml`), `at: standard.yaml`, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- 2 regras: PY-01 (decidida por leitura), PY-02 (decidida pela ferramenta, passo `build`). Nenhuma divergência divulgada contra elas.
- Pressupõe nada; a árvore tem tudo o que precisa. Autoriza 0 dependências diretas.
- `--outstanding` não imprimiu nenhum registro sem pin de standard ou com outro standard.

## Execuções capturadas
- `run/fees-compute-late-fee-build` — passed (`build=python3 -m compileall -q lending`).
- `run/fees-compute-late-fee-suite` — passed (`build`, depois `test=python3 -m pytest -q tests`).
- Setup não rodou: o registro não declara nenhum passo com papel `install`.
- Nenhuma execução vermelha.

## Dependências instaladas
Nenhuma.

## O que /review-change ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se o código afirma só o que a especificação contém, se segue o standard e por que algo falhou. Uma suíte verde aqui cobre uma tarefa.

## Handoff
Depois do commit desta entrega pela pessoa:

```
/review-change /tmp/it3/runs2/first-delivery/p target app slug lending task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard standard.yaml
```
