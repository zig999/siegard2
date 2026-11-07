# /review-change fees-review — relatório

Revisão de `task/fees/compute-late-fee` (iniciativa `lending`, target `app`), registrada em `delivery/lending/review/fees-review.md`. É evidência: nenhum veredito, severidade ou decisão sobre a mudança.

## Entradas e como foram resolvidas
- project root: `/tmp/rcbench/runs/compaction-resume--before-1/p` (nomeado na invocação)
- `project.py` resolveu: specification_root `spec`, target `app` → `app`, work_root `work`, delivery_root `delivery`
- standard: `app/standard.yaml`, resolvido a partir de `siegard.json` (a invocação não nomeou nenhum); registrado como `at: standard.yaml`, `pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`
- file set (das implementation e proof records): `lending/fees.py`, `tests/test_fees.py`
- review name: `fees-review` (run `run/fees-review`, reconciliation `siegard-reconcile/fees-review.md`)

## Verificações executadas (saída literal)
- `plan.py --check work/lending spec` → `plan checked: work/lending/plan.json matches 3 node(s)` (exit 0)
- `deliver.py --check delivery/lending work/lending app spec` (antes da escrita) → `delivery checked: delivery/lending/delivery.json matches 2 node(s)` (exit 0)
- `git status --porcelain -- delivery/lending` antes de qualquer escrita → saída vazia
- `deliver.py --standard app/standard.yaml --against app --specification spec` → limpo: PY-01 decidida por leitura, PY-02 pelo step `build`; steps `build` e `test` declarados; nada ausente
- `trace.py --check app` → `no drift: 1 binding(s) match the specification and the code as both stand now` (sem suppression receipt)
- `deliver.py --review fees-review delivery/lending work/lending app spec` → `derived delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2` / `1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 1 finding(s)` (exit 0)
- `deliver.py --check --review fees-review delivery/lending work/lending app spec` → `delivery checked: delivery/lending/delivery.json matches 3 node(s)` (exit 0)

## Run capturado
`run/fees-review`, steps do registry `build` (`python3 -m compileall -q lending`, exit 0) e `test` (`python3 -m pytest -q tests`, exit 0); outcome `passed`.

## Passes
- coverage — rodou **inline** (o spawn de `siegard:coverage-auditor` falhou: nenhum agente deste plugin está registrado na sessão)
- conformance — rodou **inline** (o spawn de `siegard:specification-conformance-reviewer` falhou pelo mesmo motivo); staged por `trace.py --stage --review` sobre 2 arquivos, 1 nó, uma onda, sem certificação; fold em `siegard-reconcile/fees-review.md`, aceito por `trace.py --reconciliation`; `trace.py --bind-record` → `bound rules/lending/late-fee-per-overdue-day to 1 file(s)`
- standard — rodou **inline** (o spawn de `siegard:standard-conformance-reviewer` falhou pelo mesmo motivo); em escopo: PY-01; nenhuma finding; `looked_past`: a aritmética de datas dos testes, que nenhuma regra em escopo nomeia
- failures — **não rodou**: o run capturado passou, então não havia falha a diagnosticar

## Coverage
| criterion | state | testes |
|---|---|---|
| A loan returned on or before its due date carries a late fee of 0 cents. | covered | `test_a_loan_returned_on_its_due_date_carries_no_late_fee`, `test_a_loan_returned_before_its_due_date_carries_no_late_fee` |
| A loan returned after its due date carries 100 cents for each calendar day between its due date and its return. | partial | `test_each_further_calendar_day_after_the_due_date_adds_100_cents` |

Por que `partial`: a taxa de um empréstimo devolvido exatamente um dia corrido após o vencimento é mantida numa faixa de 0 a 100 cents, e não em 100 cents, então o primeiro dia de atraso não é exercitado. (A proof record já declara isso em `untested`: nenhum nó decide se o dia de vencimento ou o de devolução conta.)

`unpaired`: nenhum.

## Findings (`deliver.py --findings`: 1 finding sobre 2 arquivos)
1. conformance, `kind: unstated` — `lending/fees.py`, `late_fee_cents`, o ramo sobre `overdue_days`:
   ```
   if overdue_days <= 0:
           return 0
   ```
   Custo: a taxa de um empréstimo devolvido no vencimento ou antes é decidida no código e em nenhum nó, então uma mudança nela não responde a nenhuma regra que um leitor possa abrir.

## Trace
`trace.py --check app`: sem drift (1 binding). Após o bind-record desta revisão, `rules/lending/late-fee-per-overdue-day` está ligado a `lending/fees.py`; `tests/test_fees.py` ficou `unbound` no registro de reconciliação.

## O que esta invocação escreveu (nada foi commitado)
- `delivery/lending/review/fees-review.md` (novo)
- `delivery/lending/delivery.json` (rederivado: 3 nós)
- `delivery/lending/run/fees-review/` (run capturado)
- `siegard-reconcile/fees-review.md` e `siegard-reconcile/fees-review.returns/`
- `siegard-trace.json` (restamp do bind-record)

## Handoff
A revisão terminou e não bloqueia nada: «A finding stops nothing» (SPEC-006 R4). Portas:

1. **Commitar os registros desta revisão**: os cinco caminhos acima, pathspec-scoped, numa única commit. Esta skill não commita; isso depende das suas palavras na sessão.
2. **`/analyse` sobre `rules/lending/late-fee-per-overdue-day`**: dar um nó ao fato `unstated` (taxa 0 no vencimento ou antes) e decidir se o dia de vencimento conta na contagem de dias, que é o que deixa o segundo critério `partial`. Feito isso, um teste que fixe 1 dia de atraso = 100 cents passa a provar um fato da especificação, em vez de fixar uma inferência da implementação.
3. **Deixar como está**: as duas lacunas continuam registradas nesta revisão e na proof record.

Recomendação: nenhuma, **a escolha é só sua**. Decidir se essas findings merecem uma rota é julgar o valor de uma finding, e esse valor cabe a você, não à revisão. O que decide cada lado: se a contagem de dias "between its due date and its return" deve ser fixada na especificação (porta 2) ou se a inferência registrada na implementation record basta (porta 3). A porta 1 independe dessa escolha e pode vir antes de qualquer uma das outras.
