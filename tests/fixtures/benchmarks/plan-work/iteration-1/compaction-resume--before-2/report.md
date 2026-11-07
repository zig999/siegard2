# /plan-work — lending (target `app`)

Retomado após compactação; esta parte da invocação rodou `validate → report → stop`.

## Entradas

- project root: `/tmp/pwbench/runs/compaction-resume-prior2/p`
- `project.py`: specification_root `spec`, target `app` → `app`, work_root `work` → work root `work/lending`
- standard: `app/standard.yaml`, resolvido pela linha `standard:` do `siegard.json` (a invocação não nomeou nenhum)
- `spec.py spec`: passou limpo. A verificação da árvore (`git status --porcelain -- work/lending spec`) não imprimiu nada antes de qualquer escrita.

## Etapas

1. **situate**: `spec.py --digest` e `spec.py --impact` sobre as quatro regras de lending que o escopo nomeia; `deliver.py --standard app/standard.yaml --against app` não encontrou nada ausente, então nenhuma task declara `produces`.
2. **inventory**: o spawn do agente de survey falhou (nenhum agente deste plugin está registrado nesta sessão). Por isso a etapa rodou inline, seguindo o arquivo do agente → `inventory/lending-app.md`. O escopo foi gravado em `intake/scope.md`.
3. **decompose**: o spawn do agente de decomposição falhou pelo mesmo motivo, e a etapa rodou inline → `epic/renewals.md`, `task/renewals/compute-due-date.md`, `task/renewals/renew-loan.md`.
4. **implement-against**: o spawn do binder falhou pelo mesmo motivo, e a etapa rodou inline, uma vez por task. Nenhum binder devolveu nota, então nenhum fato foi decidido e nada foi escrito em `spec/`. `plan.py --node` passou em cada task.
5. **validate**:
   - `plan.py --standard app/standard.yaml --against app work/lending spec` → exit 0:
     ```
     derived work/lending/plan.json: 4 node(s), 9 edge(s), contract siegard-plan/3
       1 inventory, 1 epic, 2 task; 4 specification node reference(s) implemented (4 unique)
     ```
   - `plan.py --check work/lending spec` → exit 0: `plan checked: work/lending/plan.json matches 4 node(s)`
   - `plan.py --notes work/lending` → exit 0: `notes standing: blocking 0, underdetermined 0, uncovered 0`

## O plano

O epic `epic/renewals` cobre 4 regras, todas implementadas e nenhuma declarada `uncovered`.

| task | implements | depends_on |
|---|---|---|
| `task/renewals/compute-due-date` | `rules/lending/loan-due-fourteen-days-after-borrowing` | — |
| `task/renewals/renew-loan` | `rules/lending/loan-renewed-at-most-once`, `rules/lending/renewal-extends-due-date-fourteen-days`, `rules/lending/reserved-copy-blocks-renewal` | `task/renewals/compute-due-date` |

Decisões registradas: nenhuma. A especificação não mudou (`git diff -- spec` está vazio).

## Isolamento

As três etapas delegadas rodaram inline, após o spawn ter sido tentado e ter falhado. O binder não foi um contexto limpo: o mesmo contexto que cortou as tasks também as vinculou à especificação. Leia os `implements` sabendo disso.

## Revisão

Nada foi commitado. A revisão é `git diff` / `git status` sobre `work/lending` (todo o conteúdo é novo e não rastreado: intake, inventory, epic, 2 tasks, `plan.json`) e sobre `spec` (sem mudanças).

## Handoff

Portas:
1. **`/implement-task /tmp/pwbench/runs/compaction-resume-prior2/p target app slug lending task task/renewals/compute-due-date`** — **recomendada (derivada)**. `renew-loan` declara `depends_on: task/renewals/compute-due-date`, então esta é a única task da fronteira. Isso só mudaria se `compute-due-date` saísse do plano ou se a dependência fosse removida.
2. Revisar o plano (e, se quiser, rodar o binder em um contexto limpo antes de entregar), dado que as etapas 2–4 rodaram inline.

O commit do plano é decisão sua: `/plan-work` não faz commit.
