# /implement-task — task/fees/compute-late-fee (lending, target app)

## Registros escritos
- `implementation/fees/compute-late-fee` — `/tmp/it3/runs/first-delivery--before-1/p/delivery/lending/implementation/fees/compute-late-fee.md` (pin `sha256:64715d1a5999ec2b5ccad9f932bd7ddd8e9cd72ef4ff7c6a5ad4f5edb38507ac`)
- `proof/fees/compute-late-fee` — `/tmp/it3/runs/first-delivery--before-1/p/delivery/lending/proof/fees/compute-late-fee.md` (pin `sha256:71abe737a77c005de920446c7de2712d883b9f334605f1737e99a2e2dda527f0`)
- Primeira entrega, não é re-entrega. A raiz de entrega `delivery/lending` foi criada vazia, como a skill prevê.
- Entradas decididas e divulgadas: target `app` (único em `targets`); slug `lending` (única iniciativa em `work_root`, sem `closure.md`); a task foi nomeada na invocação.

## Caminhos criados, modificados ou removidos (sob a raiz `app`)
- `lending/fees.py` — criado (implementation `files`)
- `tests/test_fees.py` — criado (proof `tests`)

`deliver.py --unrecorded` confirmou que os dois registros nomeiam todo caminho alterado.

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true`.

## Inferências e divergências
Inferências (implementation):
- BRL 1.00 é guardado como 100 centavos inteiros, e a função responde centavos, não um valor decimal — a partir do objetivo da task (taxa em centavos) e da regra PY-01 do `standard.yaml`.
- A função lê `due_on` e `returned_on` do registro `Loan` existente em vez de receber datas próprias — a partir da entrada `must_not_duplicate` do inventário (`lending/loans.py`).

Divergências: nenhuma, em nenhum dos registros.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `tests/test_fees.py::test_a_loan_returned_across_a_month_end_carries_100_cents_per_calendar_day`.

## O que a proof deixou sem prova, casos de borda descartados e discordâncias
- `untested`: "The amount BRL 1.00 is held as 100 integer cents; the rule is stated in BRL and the cents form follows the task's objective and PY-01, which is an inference of the implementation and not pinned here beyond the criteria's own 100 cents."
- `not_applicable`: empréstimo ainda não devolvido (task e regra só falam de empréstimo devolvido); entrada ausente no lugar de um empréstimo; dois cálculos simultâneos sobre o mesmo empréstimo; dependência que falha ou demora (o cálculo não chama nenhuma).
- `contested`: nenhum.

## Adiado pela implementação, e o que deve continuar funcionando
- Adiado: o nó `domain/lending/loan` lista um atributo `late_fee` que o registro `Loan` em `lending/loans.py` não carrega — a task pede uma função que responde a taxa, não a taxa guardada no registro.
- Adiado: o que `late_fee_cents` responde para um empréstimo não devolvido não está declarado em lugar nenhum — task e regra falam só de empréstimo devolvido.
- `preserved`: ausente — a task não alterou nada que já existia.

## Trace
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 binding, em `/tmp/it3/runs/first-delivery--before-1/p/siegard-trace.json`).
- Nenhuma vinculação recusada. Nenhum recibo de stale-bindings impresso, então nenhuma invocação `/reconcile` é entregue.

## Passos executados inline
Esta sessão não pode criar subagentes. Os passos 3 (task-implementer) e 5 (test-author) rodaram inline, aplicando `agents/task-implementer.md` e `agents/test-author.md` no contexto da sessão. Por isso o código e os testes foram escritos no mesmo contexto — a separação entre os dois produtores não vale para esta entrega, e a revisão deve ler os testes sabendo disso.

## Portas
- `/review-change` — recusada como a árvore está: "git status --porcelain -- /tmp/it3/runs/first-delivery--before-1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". Ela passa a valer depois que a pessoa fizer commit desta entrega.
- `/reconcile` — não verificada por script; sem recibo de stale-bindings, não há o que reconciliar.
- Recomendado (derivado): fazer o commit desta entrega (os dois arquivos sob `app` e a raiz `delivery/lending`, mais `siegard-trace.json`) e então rodar `/review-change`. Critério: a única porta que segue é recusada enquanto a raiz de entrega não está commitada. Fato decisivo: a recusa acima. Fato que mudaria: `git status --porcelain` sobre a raiz de entrega não imprimir nada.

## Saída final do validador
```
derived /tmp/it3/runs/first-delivery--before-1/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard
- Resolvido pelo arquivo do projeto (`siegard.json`, linha `standard:`): `/tmp/it3/runs/first-delivery--before-1/p/app/standard.yaml`, registrado como `standard.yaml` relativo à raiz `app`, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Nenhuma divergência declarada contra ele.
- Não pressupõe nada; a árvore tem tudo de que precisa.
- `--outstanding` não imprimiu nenhuma linha sobre registros sem standard ou com outro standard.

## Execuções capturadas
- `delivery/lending/run/fees-compute-late-fee-build` — passed (`build=python3 -m compileall -q lending`, 60s)
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (`build`, depois `test=python3 -m pytest -q tests`, 120s)
- Setup não rodou: o registro não declara nenhum passo com o papel de install.

## Dependências instaladas
Nenhuma. O registro autoriza 0 dependências diretas.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma task, e julga se os testes provam os critérios, se o código declara só o que a especificação contém, se segue o standard (PY-01 é lida, não decidida por ferramenta) e por que algo falhou. Uma suíte verde aqui cobre uma task.

## Handoff
Depois do commit desta entrega:

```
/review-change /tmp/it3/runs/first-delivery--before-1/p --target app --slug lending --tasks task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard standard.yaml
```

---

# Handoff (handoff.py --render, verbatim)

```
lending · task 1/1 delivered · phase review
```

1. A taxa de atraso foi escrita e testada; falta o seu commit antes da revisão.
   - **Recomendado** `c`: Você faz o commit desta entrega e depois cola a revisão abaixo. A revisão recusa enquanto delivery/lending tem mudanças sem commit. Mudaria se delivery/lending já estiver commitada.
   - `r`: Revisar agora: excluída, recusa por mudanças sem commit.
   - `s`: Reconciliar: nada a fazer, nenhum vínculo desatualizado.
   - Se nenhuma for tomada: A entrega fica no disco, sem commit e sem revisão.

   ```
   /review-change /tmp/it3/runs/first-delivery--before-1/p --target app --slug lending --tasks task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard standard.yaml
   ```

Relatório completo: /tmp/it3/runs/first-delivery--before-1/p/.git/siegard/handoff/20261107T183539Z-implement-task.md
