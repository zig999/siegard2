# Revisão `fees-review` — `task/fees/compute-late-fee` (iniciativa `lending`, target `app`)

## 1. Achados em números

```
fees-review.md: 1 finding(s) over 2 reviewed file(s)
  by pass: conformance 1
  conformance by kind: unstated 1
  standard by rule cited: none
  failures by cause: none
  by file: lending/fees.py 1
  a count says how many findings share a field, never which route any takes or whether it takes one
```

Agrupamento: 1 achado de `conformance` do tipo `unstated` em `lending/fees.py` — onde um reparo desse formato iria: estender a especificação por `/analyse` e levá-lo à tarefa por `/plan-work` (item 19). Nenhum achado de `standard`, nenhum de `failures`, nenhum de `coverage`. Uma contagem não é veredito.

## 2. Os achados, por pass

### conformance (1)

- `lending/fees.py` — `late_fee_cents, the branch on overdue_days` — kind `unstated`
  - evidence:
    ```
    if overdue_days <= 0:
            return 0
    ```
  - cost: The fee of a loan returned on or before its due date is decided in code and in no node, so a change to it answers to no rule a reader can open.

### coverage, standard, failures

Nenhum achado.

## 3. Passes que não rodaram

- `failures`: não rodou — `run/fees-review passed; there was no failure to read`.
- certificação: não rodou — o staging não tinha entradas em `certify` (os testes do proof não carregam `demonstrates`, e o `untested` do proof nomeia o nó).
- `coverage`, `conformance` e `standard` rodaram (inline; ver item 17).

## 4. Caminhos dos registros fora do conjunto

Nenhum: os dois caminhos que os registros nomeiam (`lending/fees.py`, `tests/test_fees.py`) existem sob o target source root e foram lidos.

## 5. Critérios não cobertos por inteiro

- «A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.» — `partial`, teste `tests/test_fees.py::test_each_further_calendar_day_after_the_due_date_adds_100_cents`. O que fica sem exercício: The fee of a loan returned exactly one calendar day after its due date is held to a range of 0 to 100 cents, not to 100 cents, so the first day of lateness is unexercised.
- O outro critério («A loan returned on or before its due date carries a late fee of 0 cents.») está `covered` por dois testes.

## 6. Testes sem critério

Nenhum (`unpaired: []`).

## 7. Nós que nenhum teste demonstra

- `rules/lending/late-fee-per-overdue-day` — nenhum teste o demonstra. Razão dada pelo proof: «the rule's per-day rate is held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the count of calendar days "between its due date and its return" is not stated by the node (whether an end day counts), so no finite test decides the fact whole without pinning the implementation's inference.»
- Nenhuma certificação foi pedida (nada em `certify`), portanto nenhum estado de certificação a reportar.

## 8. O standard

- `app/standard.yaml` (`lending-app`), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, nomeado por `siegard.json` (a invocação não nomeou nenhum).
- Em escopo por leitura sobre este conjunto: `PY-01` (em `lending/fees.py`).
- Deixada a uma ferramenta: `PY-02`, decidida pelo step `build`.

## 9. Caminhos que nenhuma regra alcança

```
lending/fees.py: reading PY-01; tool PY-02
tests/test_fees.py: reading none; tool none
reached by no rule: 1 of 2
  tests/test_fees.py
```

É um fato sobre o registro, não um achado: a leitura de `tests/test_fees.py` saiu limpa porque nenhuma regra foi lida contra ele.

## 10. Regras deixadas a uma ferramenta

- `build` rodou e passou (exit 0); 1 regra repousa nele (`PY-02`). O que isso assenta: que o comando `python3 -m compileall -q lending` saiu com 0. Se o comando está configurado para decidir a regra é do registro saber.
- `test` rodou e passou (exit 0); nenhuma regra repousa nele.
- Restrição decidida por step: `PY-02`. Restrição que nenhum step decide, mantida só por leitura: `PY-01` — uma execução verde não assenta nada sobre ela.

## 11. Artefatos pressupostos ausentes

Nenhum: `deliver.py --standard app/standard.yaml --against app --specification spec` saiu limpo, nada ausente.

## 12. A execução

- `run/fees-review`, cwd `app`, steps do registro (nenhum adicionado pela invocação): `build` (`python3 -m compileall -q lending`) passed, depois `test` (`python3 -m pytest -q tests`) passed. Outcome `passed`, 0 falhas contadas.
- Saída em `delivery/lending/run/fees-review/` (`run.json`, `run.log`, `build.log`, `test.log`).
- Nenhum step que uma regra espera ficou sem comando no registro.

## 13. O trace

- `trace.py --check app`, lido no situate e de novo após o bind: `no drift: 1 binding(s) match the specification and the code as both stand now`. Nenhuma classe de drift, portanto nenhuma rota (`--prune`, `/reconcile`, `--release`) se aplica. Nenhum recibo de supressão.
- Isso não é um achado e não assenta nada sobre a mudança: diz apenas que o elo de volta à especificação ainda descreve esta árvore.

## 14. O que o pass de conformance vinculou, e o que deixou em aberto

- Vinculado: `bound rules/lending/late-fee-per-overdue-day to 1 file(s)` — `lending/fees.py` (conforms: true). Nenhum nó deixou de ser escrito; nenhuma marca `collateral` nem contestada.
- `tests/test_fees.py` ficou sem vínculo (`unbound`).
- Registro: `siegard-reconcile/fees-review.md`; returns: `siegard-reconcile/fees-review.returns/` (na raiz git do target).
- `trace.py --check app` não reporta drift restante. `trace.py --owed app`:
  ```
  nothing owed: no reconciliation record under /tmp/rcbench/runs/compaction-resume/p/siegard-reconcile holds a finding against a node under app that no record cleared

  1 unstated fact(s) the records name, over 1 file(s) — the source states them and no node holds them. No bind closes one and none is counted above:
    lending/fees.py — late_fee_cents, the branch on overdue_days: The fee of a loan returned on or before its due date is decided in code and in no node, so a change to it answers to no rule a reader can open. [fees-review.md]
    each is the analysis's to close, through the node that gives the fact a home
  ```
  Nenhum dos dois é veredito sobre a mudança, e nenhuma rota é escolhida aqui.
- As `notes` do registro não trazem nenhum achado "owed a route of its own".

## 15. O que este framework não revisa

Os quatro passes são: se os testes provam os critérios da tarefa, se o código afirma só o que a especificação contém, se segue as regras de leitura do standard do projeto, e por que uma execução capturada falhou. Nada além disso é revisado — o que o standard não declara e o que nenhum step do registro executa fica fora.

## 16. O que os passes deixaram para outro julgamento

- standard: The tests' date arithmetic, which no rule in scope names.
- conformance sobre `tests/test_fees.py`: The tests assert the fee in cents per day, which is the coverage pass's to weigh.

## 17. Passes que rodaram inline

`coverage`, `conformance` (um julgamento por arquivo, uma onda, 2 arquivos) e `standard` rodaram inline nesta sessão: nenhum agente do plugin está registrado nesta sessão, e cada spawn (`siegard:coverage-auditor`, `siegard:specification-conformance-reviewer`, `siegard:standard-conformance-reviewer`) falhou. A disciplina de cada arquivo de agente foi aplicada no lugar.

## 18. Saída final do validador

```
derived delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 1 finding(s)
```
(exit 0)

## 19. Onde os reparos vivem

- código, ou um critério registrado como não atendido: `/implement-task` sobre a mesma tarefa;
- um fato afirmado no código que nenhum nó contém (o achado `unstated` acima): estender a especificação por `/analyse`, e chegar à tarefa por `/plan-work`;
- uma regra do standard que pareça errada: muda quem é dono do registro.

Esta revisão não entrega nenhuma invocação adiante: qual rota cada achado merece — ou se merece alguma — é decisão sua.

## Verificações executadas

- `plan.py --check work/lending spec` → `plan checked: work/lending/plan.json matches 3 node(s)` (exit 0)
- `deliver.py --check delivery/lending work/lending app spec` → `delivery checked: delivery/lending/delivery.json matches 2 node(s)` (exit 0)
- `git status --porcelain -- delivery/lending` → vazio
- `deliver.py --node delivery/lending/review/fees-review.md delivery/lending` → `review/fees-review: sound on its own. Cross-node checks and plan checks did not run; they run on the whole delivery.` (exit 0)

## Decidido e informado

- Project root, target `app`, slug `lending` e nome `fees-review` vieram da invocação; specification_root `spec`, work_root `work`, delivery_root `delivery` e standard `app/standard.yaml` vieram de `siegard.json` via `project.py`.
- Registro escrito: `delivery/lending/review/fees-review.md`; `delivery.json` derivado pelo validador.
