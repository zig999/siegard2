# Revisão `fees-review` — `task/fees/compute-late-fee` (initiative `lending`, target `app`)

## 1. Findings em contagem

```
fees-review.md: 1 finding(s) over 2 reviewed file(s)
  by pass: conformance 1
  conformance by kind: unstated 1
  standard by rule cited: none
  failures by cause: none
  by file: lending/fees.py 1
  a count says how many findings share a field, never which route any takes or whether it takes one
```

- `conformance` / `unstated` 1 — `lending/fees.py` 1. Onde um reparo dessa forma iria: um fato declarado no código que nenhum node da especificação contém é produzido estendendo a especificação via `/analyse`, e chega à task via `/plan-work`.
- `standard`: nenhum. `failures`: nenhum (o run passou).

## 2. Findings, por pass

### conformance

- **`lending/fees.py`**, `late_fee_cents`, linha 7, a contagem dos dias de atraso — `kind: unstated`
  - evidence: `overdue_days = (loan.returned_on - loan.due_on).days`
  - cost: o node `rules/lending/late-fee-per-overdue-day` cobra "for each calendar day between its due date and its return" e não diz se o dia da devolução conta; esta linha decide que um empréstimo devolvido um dia após o vencimento carrega um dia de multa, e não zero, e essa decisão vive só aqui — quem lê a especificação não consegue saber o que deve uma devolução com um dia de atraso.
  - correction: a especificação declarar como os dias de calendário entre o vencimento e a devolução são contados (se o dia da devolução conta), e a subtração da linha 7 ser então lida contra ela.

### coverage, standard, failures

Nenhum finding.

## 3. Passes que não rodaram

- `failures`: não rodou — `missing: run/fees-review passed; there was no failure to read`.
- `coverage`, `conformance` e `standard` rodaram (inline; ver item 17).
- A certificação não foi staged: nenhum proof record afirma `demonstrates` para um node.

## 4. Paths dos records fora do file set

Nenhum. Os records nomeiam `lending/fees.py` (implementation) e `tests/test_fees.py` (proof); ambos existem sob a target source root `app` e ambos estão no file set.

## 5. Criteria não `covered`

- "A loan returned after its due date carries 100 cents for each calendar day between its due date and its return." — `partial`, por `test_each_further_calendar_day_after_the_due_date_adds_100_cents`. O teste garante os 100 cents somados a cada dia de calendário adicional, do segundo ao quadragésimo dia de atraso, e limita a multa de uma devolução com n dias de atraso entre (n-1)*100 e n*100 cents; nenhum teste afirma a multa de uma devolução em valor absoluto. Uma implementação que responde (n-1)*100 cents — sem contar o dia da devolução — passa nele tanto quanto a que responde n*100, então quais dias contam como "between its due date and its return" (e, portanto, se um empréstimo devolvido um dia após o vencimento carrega 100 ou 0 cents) fica sem exercício. O próprio criterion deixa essa contagem em aberto.
- "A loan returned on or before its due date carries a late fee of 0 cents." — `covered`, por `test_a_loan_returned_on_its_due_date_carries_no_late_fee` e `test_a_loan_returned_before_its_due_date_carries_no_late_fee`.

## 6. Testes sem criterion

`unpaired: []` — os três testes de `tests/test_fees.py` correspondem a um criterion desta task.

## 7. Nodes que nenhum teste demonstra

- `rules/lending/late-fee-per-overdue-day` — nenhum teste o demonstra; nenhuma certificação foi staged. Razão que o proof dá (`untested`): "rules/lending/late-fee-per-overdue-day as a whole: the rule's per-day rate is held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the count of calendar days "between its due date and its return" is not stated by the node (whether an end day counts), so no finite test decides the fact whole without pinning the implementation's inference."

## 8. O standard

- Standard: `standard.yaml` (target `app`), resolvido pela linha `standard:` que `project.py` imprime para um projeto de um target; o invocation não nomeou nenhum. Pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Em escopo por leitura: `PY-01` ("Money is computed in integer cents, never in floating point."), que alcança `lending/fees.py` e não `tests/test_fees.py`. Nenhum desvio encontrado.
- Deixada a uma ferramenta: `PY-02`, que alcança `lending/fees.py`.

## 9. Paths que nenhuma regra do standard alcança

```
lending/fees.py: reading PY-01; tool PY-02
tests/test_fees.py: reading none; tool none
reached by no rule: 1 of 2
  tests/test_fees.py
```

Isto é um fato sobre o registry, não um finding: a leitura saiu limpa sobre `tests/test_fees.py` porque nada foi lido contra ele.

## 10. Regras deixadas a uma ferramenta

- `PY-02` repousa no step `build` (1 regra), que rodou e passou. O que isso estabelece: o comando `python3 -m compileall -q lending` saiu com 0. Se ele está configurado para decidir a regra que repousa sobre ele é o registry quem sabe.
- Constraints: `spec holds no constraint` — nenhuma constraint decidida por step, nenhuma deixada só à leitura.

## 11. Artefatos que o registry pressupõe e a árvore não tem

Nenhum: `it presupposes nothing, so app holds everything it needs to`.

## 12. O run

- `run/fees-review`, em `delivery/lending/run/fees-review/`, cwd `app`, timeout 120 s, outcome `passed`.
- Steps, todos do registry (o invocation não acrescentou nenhum): `build` = `python3 -m compileall -q lending` (passed, exit 0); `test` = `python3 -m pytest -q tests` (passed, exit 0; `4 passed in 0.01s`).
- Failures contadas: nenhuma (o pass `failures` não rodou porque o run passou).
- Nenhum step que uma regra espera ficou sem comando no registry.

## 13. O trace

```
trace: /tmp/rcbench/runs/full-review/p/siegard-trace.json — one file per git toplevel; every target under it reads this same one
no drift: 1 binding(s) match the specification and the code as both stand now
```

Nenhum drift em nenhuma classe; sem suppression receipt. Isto não é um finding e não decide nada sobre a mudança: diz apenas se o vínculo de volta à especificação ainda descreve esta árvore. Rotas por classe, para referência: `orphaned` → `trace.py --prune`; `moved` e `code` em arquivos fora desta revisão → `/reconcile`; arquivo vinculado que a árvore não tem mais → `trace.py --release`.

## 14. O que o pass de conformance vinculou e o que deixou devido

- Nada foi vinculado nem restampado. `trace.py --save-return` recusou cada retorno inline:
  ```
  cannot run: /tmp/rcbench/runs/full-review/inline/lending__fees.py.yaml holds no assistant message; it is not a subagent's transcript
  cannot run: /tmp/rcbench/runs/full-review/inline/tests__test_fees.py.yaml holds no assistant message; it is not a subagent's transcript
  ```
  e, sem retornos salvos, `trace.py --fold` recusou:
  ```
  cannot fold: lending/fees.py: no return at /tmp/rcbench/runs/full-review/p/siegard-reconcile/fees-review.returns/lending__fees.py.yaml (wave 1 has not finished)
  cannot fold: tests/test_fees.py: no return at /tmp/rcbench/runs/full-review/p/siegard-reconcile/fees-review.returns/tests__test_fees.py.yaml (wave 1 has not finished)

  2 problem(s); each names a subagent to run again with its prompt fixed — an unusable return is never repaired here, and a follow-up question to the subagent that already answered is not a fresh judgment.
  ```
  `--reconciliation` e `--bind-record` não rodaram; não existe `siegard-reconcile/fees-review.md`, e `siegard-trace.json` não foi alterado. O staging deixou o diretório vazio `siegard-reconcile/fees-review.returns/` na raiz git do target, e o workspace em `/tmp/rcbench/runs/full-review/ws.4HQb` (manifest, packs, `premise.yaml`).
- O review record não carrega `reconciliation`; o validator emitiu o receipt correspondente (item 18).
- `trace.py --check` sobre o target relata o drift que resta; `trace.py --owed` relata o que este pass encontrou e nenhum bind fecharia. Nenhum dos dois é veredito sobre a mudança.
- Notas do fold: nenhuma (o fold não rodou).

## 15. O que este framework não revisa

Segurança, desempenho, estilo e qualquer regra que o standard do projeto não declare. O standard deste projeto declara duas regras (PY-01 por leitura, PY-02 por ferramenta); quatro passes sobre ele não são todos os passes possíveis.

## 16. O que os passes deixaram passar, por ser de outro julgamento

- conformance (`lending/fees.py`): a multa é respondida como int de cents enquanto `domain/lending/loan` declara `late_fee` como valor decimal em BRL, e a função não grava nada no record; como dinheiro é representado é questão do standard, não um fato de domínio.
- conformance (`tests/test_fees.py`): o arquivo afirma a taxa diária da regra através de `late_fee_cents` em vez de contê-la; se essas asserções provam os criteria é julgamento do pass de coverage.
- standard: nada.

## 17. Passes que rodaram inline

`coverage`, `conformance` (os dois arquivos da wave 1) e `standard` rodaram inline. Nenhum agent deste plugin está registrado nesta sessão: cada spawn falhou com `Agent type 'siegard:<agent-name>' not found` (tentados `siegard:coverage-auditor`, `siegard:specification-conformance-reviewer` ×2 e `siegard:standard-conformance-reviewer`). A sessão leu o arquivo de cada agent em `agents/` e aplicou sua disciplina. Esta sessão não escreveu nenhum node que um subagent leria. Fora da leitura prescrita, a sessão abriu `app/lending/loans.py` (fora do file set) para conferir os campos de `Loan`; nenhum finding se apoia nele.

## 18. Saída final do validator, verbatim

```
derived delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2
  review/fees-review: the conformance pass ran over a traced target and names no reconciliation record; it judged the plan's nodes alone, and every other binding of the files it reviewed stands as it stood before the delivery — `trace.py --check` reports those as `code` drift, and a /reconcile over those files is what closes them
  1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 1 finding(s)
```

Checks antes da revisão, com saída verbatim:

```
plan checked: work/lending/plan.json matches 3 node(s)
delivery checked: delivery/lending/delivery.json matches 2 node(s)
```

`git status --porcelain -- delivery/lending` não imprimiu nada antes da primeira escrita.

## 19. Onde os reparos vivem

- código, ou um criterion registrado como não atendido: `/implement-task` sobre a mesma task;
- um fato declarado no código que nenhum node contém: estender a especificação via `/analyse`, chegando à task via `/plan-work`;
- uma regra do standard que pareça errada: muda quem é dono do registry.

Esta revisão não entrega nenhuma invocation adiante: qual rota cada finding merece — ou se merece alguma — é decisão sua. O que o finding e o criterion `partial` significam, e se a contagem de dias deve ser decidida na especificação, é seu.
