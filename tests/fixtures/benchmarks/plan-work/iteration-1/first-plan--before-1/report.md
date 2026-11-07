# /plan-work — lending (target app)

Projeto: /tmp/pwbench/runs/first-plan-prior1/p · alvo `app` · slug `lending` · work root `work/lending`.
Primeira execução: o work root estava vazio; `git status --porcelain -- work/lending spec` não imprimiu nada antes de qualquer escrita.

## Nós escritos (todos criados; nada alterado nem removido)

- `intake/scope.md` (o escopo, verbatim)
- `inventory/lending-service`
- `epic/loan-renewal`
- `task/loan-renewal/due-date-on-borrowing`
- `task/loan-renewal/renew-loan`
- `task/loan-renewal/reserved-copy-refuses-renewal` (depends_on `task/loan-renewal/renew-loan`)
- `plan.json` (derivado por `plan.py`)

## Conjunto de impacto lido

Vocabulário buscado (grep na raiz da especificação): `renew`, `due`, `reserv`, `fourteen`, `borrow`.
Nós `constraints/`: nenhum existe (`spec.py --digest` não lista nenhum; `deliver.py --standard` imprimiu "spec holds no constraint").
Candidatos nomeados: `rules/lending/loan-due-fourteen-days-after-borrowing`, `rules/lending/loan-renewed-at-most-once`, `rules/lending/renewal-extends-due-date-fourteen-days`, `rules/lending/reserved-copy-blocks-renewal`, `domain/lending/loan`.

```
impact set: 15 node(s) from 5 named, one hop, both directions.

rules/lending/loan-due-fourteen-days-after-borrowing
  declares  -> domain/lending/loan                              constrains[0]
  named by  <- scenarios/lending/overdue-member-refused-new-loan involves[2]

rules/lending/loan-renewed-at-most-once
  declares  -> domain/lending/loan                              constrains[0]

rules/lending/renewal-extends-due-date-fourteen-days
  declares  -> domain/lending/loan                              constrains[0]

rules/lending/reserved-copy-blocks-renewal
  declares  -> domain/lending/loan                              constrains[0]
  declares  -> domain/lending/reservation                       constrains[1]
  named by  <- rules/lending/reserved-copy-blocks-renewal.log   entries[0]

domain/lending/loan
  declares  -> domain/lending/member                            aggregate
  declares  -> domain/lending/copy                              relationships[0].target
  named by  <- domain/lending/loan.log                          entries[0]
  named by  <- domain/lending/loan.log                          entries[1]
  named by  <- domain/lending/loan.log                          entries[2]
  named by  <- domain/lending/loan.log                          entries[3]
  named by  <- domain/lending/member                            relationships[0].target
  named by  <- rules/lending/late-fee-per-overdue-day           constrains[0]
  named by  <- rules/lending/loan-due-fourteen-days-after-borrowing constrains[0]
  named by  <- rules/lending/loan-renewed-at-most-once          constrains[0]
  named by  <- rules/lending/member-holds-at-most-three-loans   constrains[1]
  named by  <- rules/lending/overdue-member-cannot-borrow       constrains[1]
  named by  <- rules/lending/renewal-extends-due-date-fourteen-days constrains[0]
  named by  <- rules/lending/reserved-copy-blocks-renewal       constrains[0]
  named by  <- rules/lending/returned-reserved-copy-notifies-reserver constrains[0]
  named by  <- scenarios/lending/overdue-member-refused-new-loan involves[1]

read:
  spec/domain/lending/copy.md
  spec/domain/lending/copy.log.md
  spec/domain/lending/loan.md
  spec/domain/lending/loan.log.md
  spec/domain/lending/loan.log.md
  spec/domain/lending/member.md
  spec/domain/lending/member.log.md
  spec/domain/lending/reservation.md
  spec/domain/lending/reservation.log.md
  spec/rules/lending/late-fee-per-overdue-day.md
  spec/rules/lending/late-fee-per-overdue-day.log.md
  spec/rules/lending/loan-due-fourteen-days-after-borrowing.md
  spec/rules/lending/loan-renewed-at-most-once.md
  spec/rules/lending/member-holds-at-most-three-loans.md
  spec/rules/lending/overdue-member-cannot-borrow.md
  spec/rules/lending/renewal-extends-due-date-fourteen-days.md
  spec/rules/lending/reserved-copy-blocks-renewal.md
  spec/rules/lending/reserved-copy-blocks-renewal.log.md
  spec/rules/lending/reserved-copy-blocks-renewal.log.md
  spec/rules/lending/returned-reserved-copy-notifies-reserver.md
  spec/rules/lending/returned-reserved-copy-notifies-reserver.log.md
  spec/scenarios/lending/overdue-member-refused-new-loan.md
```

Plano: primeira execução, não havia plano a fechar.

## Fatos decididos na especificação

Nenhum. Nenhum binder retornou nota `unstated`; nenhum decider foi acionado; `git status --porcelain -- spec` continua vazio. Nenhum item `noticed`.

## Notas `blocking`

Nenhuma.

## Notas dos binders, por tarefa

`task/loan-renewal/due-date-on-borrowing`:
- REMAINDER, from the specification — the clause 'until the loan is renewed' of rules/lending/loan-due-fourteen-days-after-borrowing reaches no criterion of this task; it belongs to the renewal act, task/loan-renewal/renew-loan. (Respondida: `task/loan-renewal/renew-loan` implementa a regra e o critério 1 dela responde à cláusula.)
- ADVISORY, from the specification — this task fixes the due date a loan is made with and does not deliver the borrow operation domain/lending/member declares.

`task/loan-renewal/renew-loan`:
- UNDERDETERMINED, from the specification — rules/lending/reserved-copy-blocks-renewal refuses a renewal while the loan's copy holds a reservation, and no criterion here excludes it. Implementação que passa: a renewal that moves the due date of an unrenewed loan whose copy holds a reservation. (A recusa é critério de `task/loan-renewal/reserved-copy-refuses-renewal`, que depende desta.)
- ADVISORY, from the specification — no candidate states whether a loan already returned may be renewed, and no criterion of this task rests on it.

`task/loan-renewal/reserved-copy-refuses-renewal`:
- ADVISORY, from the specification — rules/lending/reserved-copy-blocks-renewal is eventual, so the renewal reads the reservation as the copy last recorded it, not under one transaction with the loan.
- ADVISORY, from the specification — this task reads a copy's reservation and does not deliver the reserve operation domain/lending/copy declares.

## Nós com `rationale`

`epic/loan-renewal`, `task/loan-renewal/due-date-on-borrowing`, `task/loan-renewal/renew-loan`, `task/loan-renewal/reserved-copy-refuses-renewal` (o escopo não declara corte; todo corte foi decisão do planejamento).

## Padrão do projeto

Resolvido pelo arquivo do projeto, `/tmp/pwbench/runs/first-plan-prior1/p/siegard.json` (linha `standard:` → `app/standard.yaml`); a invocação não nomeou nenhum.
Pressupõe nada: "it presupposes nothing, so app holds everything it needs to". Nenhuma tarefa declara `produces`.
Constraints da especificação que nenhum step decide: nenhum ("spec holds no constraint").

## Passos executados inline

Nenhum agente deste plugin está registrado nesta sessão; cada spawn foi tentado e falhou, e o arquivo do agente sob `agents/` foi lido e aplicado no lugar:
- Inventory (`siegard:codebase-surveyor`): `Agent type 'siegard:codebase-surveyor' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, impeccable:impeccable-asset-producer, impeccable:impeccable-documenter, impeccable:impeccable-finish-reviewer, impeccable:impeccable-manual-edit-applier, Plan, statusline-setup, web-fetch`
- Decompose (`siegard:backlog-decomposer`): `Agent type 'siegard:backlog-decomposer' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, impeccable:impeccable-asset-producer, impeccable:impeccable-documenter, impeccable:impeccable-finish-reviewer, impeccable:impeccable-manual-edit-applier, Plan, statusline-setup, web-fetch`
- Implement against (`siegard:execution-contract-binder`, três spawns em paralelo, um por esqueleto): `Agent type 'siegard:execution-contract-binder' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, impeccable:impeccable-asset-producer, impeccable:impeccable-documenter, impeccable:impeccable-finish-reviewer, impeccable:impeccable-manual-edit-applier, Plan, statusline-setup, web-fetch`

Consequência: o isolamento que separa decomposição e binding não se sustentou — o mesmo contexto cortou as tarefas e decidiu o `implements`. O diff deve ser lido com isso em mente.

## Saída final do validador

```
derived work/lending/plan.json: 5 node(s), 21 edge(s), contract siegard-plan/3
  1 inventory, 1 epic, 3 task; 12 specification node reference(s) implemented (8 unique)
```

## Handoff

```
/implement-task /tmp/pwbench/runs/first-plan-prior1/p target app slug lending task <a tarefa>
```

A tarefa é a vaga aberta: escolhê-la é escolher o que se constrói. O conjunto entregável é lido de:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding /tmp/pwbench/runs/first-plan-prior1/p/delivery /tmp/pwbench/runs/first-plan-prior1/p/work/lending /tmp/pwbench/runs/first-plan-prior1/p/app /tmp/pwbench/runs/first-plan-prior1/p/spec
```

(Hoje esse comando sai com "cannot run: delivery root delivery is not a directory" — a raiz de entrega ainda não existe porque nada foi entregue.)
Onde o conjunto tiver mais de uma tarefa, `bin/deliver.py --help` descreve a entrega em paralelo, uma worktree por tarefa; essa rota, como tudo aqui, é escolha sua.
`git diff` sobre `work/lending` é a revisão, e ela é sua.

## Handoff entregue à pessoa (saída de handoff.py --render, verbatim)

```
lending · task 0/3 delivered · phase delivery
```

1. Escolha qual tarefa entregar: o plano tem 3, duas sem espera (prazo no empréstimo; renovar uma vez) e a recusa por reserva espera a renovação.
   - **Decisão sua**: Cada tarefa é o que se constrói a seguir; o relatório traz o comando que lista o que cada uma ainda espera.
   - `entregar`: Entrega uma tarefa; hoje recusa porque nenhuma tarefa foi nomeada e há mais de uma pronta — nomeie a tarefa na invocação.
   - Se nenhuma for tomada: O plano fica escrito e não commitado em work/lending, para você revisar com git diff.

   ```
   /implement-task /tmp/pwbench/runs/first-plan-prior1/p target app slug lending task <a tarefa>
   ```

Relatório completo: /tmp/pwbench/runs/first-plan-prior1/p/.git/siegard/handoff/20261107T161614Z-plan-work.md
