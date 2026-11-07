# /plan-work — lending (target app)

Projeto: /tmp/pwbench/runs/first-plan-new1/p · raiz de trabalho: /tmp/pwbench/runs/first-plan-new1/p/work/lending · modo: rota ordinária (nenhum modo nomeado; primeira execução sobre raiz vazia).
Entradas: escopo, raiz do projeto, target `app` e slug `lending` nomeados na invocação. `project.py` resolveu `specification_root`, `targets` e `work_root`; `spec.py` limpo; `git status --porcelain` sobre `work/lending` e `spec` não imprimiu nada.

## Nós escritos

- `intake/scope.md` (escopo verbatim)
- `inventory/lending-loans-module`
- `epic/loan-renewal`
- `task/loan-renewal/loan-due-date`
- `task/loan-renewal/renew-loan`
- `task/loan-renewal/refuse-second-renewal`
- `task/loan-renewal/reservation-blocks-renewal`
- `plan.json` (derivado por `plan.py`)

## Conjunto de impacto lido

Termos buscados na raiz da especificação: `renew`, `due`, `fourteen`, `reserv`. Nenhum nó `constraints/` existe (a raiz não tem o diretório). Escopo nomeado, não aberto, então `plan.py --unplanned` não rodou. Candidatos: as quatro regras de vencimento/renovação e `domain/lending/loan`.

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
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/copy.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/copy.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/loan.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/loan.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/loan.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/member.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/member.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/reservation.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/domain/lending/reservation.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/late-fee-per-overdue-day.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/late-fee-per-overdue-day.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/loan-due-fourteen-days-after-borrowing.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/loan-renewed-at-most-once.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/member-holds-at-most-three-loans.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/overdue-member-cannot-borrow.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/renewal-extends-due-date-fourteen-days.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/reserved-copy-blocks-renewal.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/reserved-copy-blocks-renewal.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/reserved-copy-blocks-renewal.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/returned-reserved-copy-notifies-reserver.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/rules/lending/returned-reserved-copy-notifies-reserver.log.md
  /tmp/pwbench/runs/first-plan-new1/p/spec/scenarios/lending/overdue-member-refused-new-loan.md
```

## Fatos decididos na especificação

Nenhum. Nenhuma nota `unstated` foi devolvida; a raiz da especificação não foi escrita.

## Notas bloqueantes

Nenhuma.

## Notas do binder, por tarefa (como escritas em `## Notes`)

- `task/loan-renewal/loan-due-date`: `REMAINDER, from the specification — the clause "until the loan is renewed" of rules/lending/loan-due-fourteen-days-after-borrowing reaches no criterion here; it belongs to task/loan-renewal/renew-loan, which moves the due date.` — destino: `task/loan-renewal/renew-loan`, cujos critérios movem o vencimento (2026-01-15 → 2026-01-29).
- `task/loan-renewal/renew-loan`: `ADVISORY, from the specification — no candidate states whether a loan already returned may be renewed, and no criterion of this task rests on it.`
- `task/loan-renewal/refuse-second-renewal`: nenhuma.
- `task/loan-renewal/reservation-blocks-renewal`: `ADVISORY, from the specification — rules/lending/reserved-copy-blocks-renewal is eventual: the renewal reads the reservation as domain/lending/copy last recorded it, and no criterion tests how promptly a new reservation takes effect.`

## Nós com `rationale`

- `task/loan-renewal/loan-due-date`
- `task/loan-renewal/renew-loan`
- `task/loan-renewal/refuse-second-renewal`
- `task/loan-renewal/reservation-blocks-renewal`

## Padrão do projeto

Resolvido pelo arquivo do projeto (`siegard.json`, linha `standard:` de `project.py`): `/tmp/pwbench/runs/first-plan-new1/p/app/standard.yaml`. Não pressupõe nenhum artefato — `deliver.py` imprimiu "it presupposes nothing, so /tmp/pwbench/runs/first-plan-new1/p/app holds everything it needs to"; nenhuma tarefa de substrato foi cortada. A especificação não tem nenhum nó `constraints/` ("holds no constraint"), então nenhuma constraint implementada fica mantida só por leitura.

## Passos executados inline

Todos os spawns foram tentados e falharam; cada passo aplicou o arquivo do agente no lugar, na mesma sessão (o isolamento do binder em relação ao corte foi perdido).

- Passo 2, Inventário (`siegard:codebase-surveyor`): `Agent type 'siegard:codebase-surveyor' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, impeccable:impeccable-asset-producer, impeccable:impeccable-documenter, impeccable:impeccable-finish-reviewer, impeccable:impeccable-manual-edit-applier, Plan, statusline-setup, web-fetch`
- Passo 3, Decomposição (`siegard:backlog-decomposer`): `Agent type 'siegard:backlog-decomposer' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, impeccable:impeccable-asset-producer, impeccable:impeccable-documenter, impeccable:impeccable-finish-reviewer, impeccable:impeccable-manual-edit-applier, Plan, statusline-setup, web-fetch`
- Passo 4, Implementar contra (`siegard:execution-contract-binder`, 4 spawns juntos): `Agent type 'siegard:execution-contract-binder' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, impeccable:impeccable-asset-producer, impeccable:impeccable-documenter, impeccable:impeccable-finish-reviewer, impeccable:impeccable-manual-edit-applier, Plan, statusline-setup, web-fetch` (idêntico nos quatro)

## Saída final do validador

```
derived /tmp/pwbench/runs/first-plan-new1/p/work/lending/plan.json: 6 node(s), 23 edge(s), contract siegard-plan/3
  1 inventory, 1 epic, 4 task; 13 specification node reference(s) implemented (8 unique)
```

## Handoff

Próximo passo, uma tarefa por invocação; a tarefa é o espaço aberto:

```
/implement-task /tmp/pwbench/runs/first-plan-new1/p target app slug lending task <task>
```

Onde ler o conjunto entregável (o que não tem registro e do que cada tarefa depende):

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding /tmp/pwbench/runs/first-plan-new1/p/delivery /tmp/pwbench/runs/first-plan-new1/p/work/lending /tmp/pwbench/runs/first-plan-new1/p/app /tmp/pwbench/runs/first-plan-new1/p/spec
```

Onde o conjunto tiver mais de uma tarefa, `bin/deliver.py --help` descreve entregá-las em paralelo, uma worktree por tarefa, integradas por merge — escolha da pessoa. A revisão é `git diff` sobre `work/lending`, e pertence à pessoa; nada foi commitado.
