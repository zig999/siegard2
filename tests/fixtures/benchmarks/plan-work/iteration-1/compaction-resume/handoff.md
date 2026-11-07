# /plan-work — relatório completo · lending (alvo app)

Invocação: `/plan-work /tmp/pwbench/runs/compaction-resume-new1/p target app slug lending — Members renew their loans. A loan is due fourteen calendar days after the copy was borrowed. A member may renew a loan once, and a renewal moves the due date fourteen calendar days later. A loan cannot be renewed while its copy holds a reservation.`

Modo: rota ordinária (nenhum modo nomeado). Raiz de trabalho vazia no início: primeira execução; nada alterado nem removido.

## Nós escritos (todos criados)

- `work/lending/intake/scope.md` (o escopo, verbatim)
- `inventory/lending-app`
- `epic/renewals`
- `task/renewals/compute-due-date`
- `task/renewals/renew-loan` (depends_on `task/renewals/compute-due-date`)
- `plan.json` derivado por `plan.py`

## Conjunto de impacto lido

Termos buscados na raiz da especificação: `loan`, `due`, `renew`, `reservation`. A especificação não tem nós `constraints/` (`spec` holds no constraint). Candidatos: as quatro regras que o escopo nomeia.

Saída de `spec.py --impact` (reexecutada após a compactação sobre os mesmos quatro candidatos; a especificação não mudou):

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

Plano: raiz de trabalho vazia no início, sem `plan.json` a fechar.

## Fatos decididos na especificação

Nenhum. Nenhum binder retornou nota `unstated`; nada foi escrito na raiz da especificação. Nenhum item `noticed`.

## Notas bloqueantes

Nenhuma.

## Notas dos binders

Nenhuma: o binder de `task/renewals/compute-due-date` e o de `task/renewals/renew-loan` não retornaram nota; o `## Notes` de cada tarefa diz `None.`

## Nós com `rationale`

Nenhum.

## Padrão do projeto

Resolvido do arquivo do projeto, `siegard.json` (`standard: app/standard.yaml`). Não pressupõe nenhum artefato — saída de `deliver.py --standard app/standard.yaml --against app --specification spec`: "it presupposes nothing, so app holds everything it needs to". Restrições que as tarefas deste plano implementam e que nenhum passo decide: nenhuma (`spec holds no constraint`). O registro declara 2 regras: 1 decidida por leitura, 1 por ferramenta (passo `build`).

## Passos executados inline

Os passos 2, 3 e 4 rodaram inline, aplicando a disciplina de `agents/codebase-surveyor.md`, `agents/backlog-decomposer.md` e `agents/execution-contract-binder.md`, depois que cada spawn foi tentado e falhou: nenhum agente deste plugin está registrado nesta sessão (`siegard:codebase-surveyor`, `siegard:backlog-decomposer`, `siegard:execution-contract-binder` — um por esqueleto). O texto literal de cada falha foi perdido na compactação do contexto; o resumo da sessão registra apenas que cada spawn falhou por não haver agente do plugin registrado. Nenhum decisor foi necessário.

## Saída final do validador

`plan.py --check work/lending spec` (exit 1, esperado antes da primeira derivação; nenhuma linha `MOVED`):

```
STALE: work/lending/plan.json does not exist; the plan has never been derived
```

`plan.py --standard app/standard.yaml --against app work/lending spec` (exit 0):

```
derived work/lending/plan.json: 4 node(s), 9 edge(s), contract siegard-plan/3
  1 inventory, 1 epic, 2 task; 4 specification node reference(s) implemented (4 unique)
```

## Próximo passo

```
/implement-task /tmp/pwbench/runs/compaction-resume-new1/p target app slug lending task <tarefa>
```

A tarefa é a vaga aberta: escolhê-la é escolher o que se constrói. O conjunto entregável se lê com:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding /tmp/pwbench/runs/compaction-resume-new1/p/delivery/lending /tmp/pwbench/runs/compaction-resume-new1/p/work/lending /tmp/pwbench/runs/compaction-resume-new1/p/app /tmp/pwbench/runs/compaction-resume-new1/p/spec
```

Hoje ele recusa (`cannot run: delivery root /tmp/pwbench/runs/compaction-resume-new1/p/delivery/lending is not a directory`): a raiz de entrega ainda não existe; `/implement-task` a cria vazia. Onde o conjunto tiver mais de uma tarefa, `bin/deliver.py --help` descreve a entrega em paralelo, uma worktree por tarefa, integrada por merge — escolha da pessoa.

A porta `/implement-task` está hoje excluída: `door.py` responde `refuses`, refused: `git status --porcelain -- /tmp/pwbench/runs/compaction-resume-new1/p/delivery/lending /tmp/pwbench/runs/compaction-resume-new1/p/app /tmp/pwbench/runs/compaction-resume-new1/p/work/lending/task/renewals/compute-due-date.md is not empty — the entry point writes there, and stops on a change it did not make`. O plano escrito por esta invocação está não commitado em `work/lending/`; revisar `git diff`/`git status` sobre a raiz de trabalho e commitá-lo é da pessoa.
