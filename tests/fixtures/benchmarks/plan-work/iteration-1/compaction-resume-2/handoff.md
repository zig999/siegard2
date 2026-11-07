# /plan-work — lending (target app)

Invocação: `/plan-work /tmp/pwbench/runs/compaction-resume-new2/p target app slug lending — Members renew their loans. …` (rota ordinária; nenhum modo nomeado). A sessão passou por uma compactação depois do passo 4; os passos 5 e 6 rodaram depois dela.

## Nós escritos (raiz vazia: todos criados)

- `work/lending/intake/scope.md` (escopo, como fornecido)
- `inventory/lending-app`
- `epic/renewals`
- `task/renewals/compute-due-date`
- `task/renewals/renew-loan` (depends_on `task/renewals/compute-due-date`)

Nenhum nó alterado ou removido.

## Conjunto de impacto lido

Termos buscados na raiz da especificação para nomear os candidatos: `loan`, `due`, `renew`, `reservation`. Nenhum nó `constraints/` existe em `spec/`.

Saída de `spec.py --impact` (re-executada após a compactação, mesmos quatro candidatos; somente leitura):

```
impact set: 8 node(s) from 4 named, one hop, both directions.

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

read:
  spec/domain/lending/loan.md
  spec/domain/lending/loan.log.md
  spec/domain/lending/reservation.md
  spec/domain/lending/reservation.log.md
  spec/rules/lending/loan-due-fourteen-days-after-borrowing.md
  spec/rules/lending/loan-renewed-at-most-once.md
  spec/rules/lending/renewal-extends-due-date-fourteen-days.md
  spec/rules/lending/reserved-copy-blocks-renewal.md
  spec/rules/lending/reserved-copy-blocks-renewal.log.md
  spec/rules/lending/reserved-copy-blocks-renewal.log.md
  spec/scenarios/lending/overdue-member-refused-new-loan.md
```

## Fatos escritos pela rota de fato decidido

Nenhum. Nenhum binder devolveu nota `unstated`; nada foi escrito na especificação. Nenhum item `noticed`.

## Notas bloqueantes

Nenhuma.

## Notas devolvidas pelos binders

Nenhuma: o binder de `task/renewals/compute-due-date` e o de `task/renewals/renew-loan` não devolveram nota. `## Notes` de ambas as tarefas é `None.`

## Nós com `rationale`

Nenhum.

## Padrão do projeto

- Resolvido do arquivo do projeto: `siegard.json` → `standard: app/standard.yaml` (a invocação não nomeou nenhum).
- Pressupõe: nada — `deliver.py --standard app/standard.yaml --against app --specification spec` imprimiu "it presupposes nothing, so app holds everything it needs to". Nenhum artefato a ser produzido por tarefa.
- Restrições que as tarefas implementam e que nenhum passo decide: nenhuma — "spec holds no constraint".

## Passos executados inline

Os passos 2, 3 e 4 rodaram inline, cada um após uma tentativa de spawn que falhou. O texto literal das falhas se perdeu na compactação; o que ficou registrado é a causa: nenhum agente deste plugin está registrado nesta sessão.

- Passo 2, Inventory — spawn de `siegard:codebase-surveyor` falhou: agente não registrado nesta sessão.
- Passo 3, Decompose — spawn de `siegard:backlog-decomposer` falhou: agente não registrado nesta sessão.
- Passo 4, Implement against — spawn de `siegard:execution-contract-binder` (um por skeleton, dois) falhou: agente não registrado nesta sessão.

Consequência: o isolamento do binder (ler a especificação sem memória do corte) não foi obtido; o binding foi feito na mesma sessão que cortou as tarefas.

## Saída final do validador

`plan.py --check work/lending spec` (antes da derivação; nenhuma linha `MOVED`):

```
STALE: work/lending/plan.json does not exist; the plan has never been derived
```

`plan.py --standard app/standard.yaml --against app work/lending spec` (exit 0):

```
derived work/lending/plan.json: 4 node(s), 9 edge(s), contract siegard-plan/3
  1 inventory, 1 epic, 2 task; 4 specification node reference(s) implemented (4 unique)
```

## Handoff

Invocação de `/implement-task` pronta para colar (o padrão já é respondido por `siegard.json`; a tarefa é o único espaço em aberto — escolhê-la é escolher o que se constrói):

```
/implement-task /tmp/pwbench/runs/compaction-resume-new2/p target app slug lending task <tarefa>
```

Onde ler o conjunto entregável, por tarefa, com o que cada uma espera:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding /tmp/pwbench/runs/compaction-resume-new2/p/delivery/lending /tmp/pwbench/runs/compaction-resume-new2/p/work/lending /tmp/pwbench/runs/compaction-resume-new2/p/app /tmp/pwbench/runs/compaction-resume-new2/p/spec
```

Onde o conjunto tiver mais de uma tarefa, `bin/deliver.py --help` descreve entregá-las em paralelo, um worktree por tarefa, integradas por merge — escolha da pessoa. A rota inteira também pode ser entregue por `/deliver-scope`.

Estado da porta `/implement-task` agora: **excluída** — `refuses`:

> refused: git status --porcelain -- /tmp/pwbench/runs/compaction-resume-new2/p/delivery/lending /tmp/pwbench/runs/compaction-resume-new2/p/app /tmp/pwbench/runs/compaction-resume-new2/p/work/lending/task/renewals/compute-due-date.md is not empty — the entry point writes there, and stops on a change it did not make

O plano em `work/lending/` não está commitado. A revisão é `git diff` / `git status` sobre `work/lending`, e é da pessoa; commitar é o ato que libera `/implement-task`. Recomendação (tipo **derivado**: um fato em disco decide — a única porta de implementação é recusada pelo seu próprio ponto de entrada enquanto o plano estiver pendente): revisar e commitar `work/lending/`. Mudaria se a revisão achar um corte de tarefa errado — então a volta é `/plan-work` sobre o mesmo slug.
