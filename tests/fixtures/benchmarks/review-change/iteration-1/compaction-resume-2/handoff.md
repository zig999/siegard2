# Revisão `fees-review` — `task/fees/compute-late-fee` (iniciativa `lending`, target `app`)

Esta revisão é evidência, não aprovação: o que os achados significam é decisão sua.

## 1. Achados, em contagens

```
fees-review.md: 1 finding(s) over 2 reviewed file(s)
  by pass: conformance 1
  conformance by kind: unstated 1
  standard by rule cited: none
  failures by cause: none
  by file: lending/fees.py 1
  a count says how many findings share a field, never which route any takes or whether it takes one
```

Agrupamento: 1 achado de `conformance`, `kind: unstated`, em `lending/fees.py` — rota onde um reparo iria: estender a especificação por `/analyse`, que chega à tarefa por `/plan-work` (item 19). Nenhum achado de `standard`, nenhum de `failures`, nenhum de `coverage`.

## 2. Cada achado, por passada

### conformance

- `lending/fees.py` — `late_fee_cents, the branch on overdue_days` — `kind: unstated`
  - evidência:
    ```
    if overdue_days <= 0:
            return 0
    ```
  - custo: The fee of a loan returned on or before its due date is decided in code and in no node, so a change to it answers to no rule a reader can open.

## 3. Passadas que não rodaram

- `failures` não rodou: `run/fees-review passed; there was no failure to read`.
- `coverage`, `conformance` e `standard` rodaram. Nenhuma certificação era devida: o staging não tem entradas em `certify` (os testes da prova não carregam `demonstrates`; seu `untested` nomeia o nó).

## 4. Caminhos dos registros fora do conjunto

Nenhum. Os registros nomeiam `lending/fees.py` e `tests/test_fees.py`, e a raiz `app` guarda os dois; ambos foram lidos.

## 5. Critérios não encontrados cobertos

- «A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.» — `partial`, com `tests/test_fees.py::test_each_further_calendar_day_after_the_due_date_adds_100_cents`. O que fica sem exercício: The fee of a loan returned exactly one calendar day after its due date is held to a range of 0 to 100 cents, not to 100 cents, so the first day of lateness is unexercised.

O outro critério, «A loan returned on or before its due date carries a late fee of 0 cents.», está `covered` por `test_a_loan_returned_on_its_due_date_carries_no_late_fee` e `test_a_loan_returned_before_its_due_date_carries_no_late_fee`.

## 6. Testes sem critério

Nenhum: `unpaired: []`.

## 7. Nós que nenhum teste demonstra

- `rules/lending/late-fee-per-overdue-day` — nenhum teste o demonstra. A razão que a prova dá, no seu `untested`: «the rule's per-day rate is held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the count of calendar days "between its due date and its return" is not stated by the node (whether an end day counts), so no finite test decides the fact whole without pinning the implementation's inference.» A prova também lista como não provado o valor de uma devolução exatamente um dia após o vencimento. Nenhuma certificação foi preparada, portanto nenhum estado de certificação a relatar.

## 8. O standard

`app/standard.yaml` (de `siegard.json`; a invocação não nomeou nenhum), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`. Em escopo por leitura sobre este conjunto: `PY-01`. Deixada a uma ferramenta: `PY-02` (passo `build`).

## 9. Caminhos que nenhuma regra alcança

```
lending/fees.py: reading PY-01; tool PY-02
tests/test_fees.py: reading none; tool none
reached by no rule: 1 of 2
  tests/test_fees.py
```

Fato sobre o registro, não achado: a leitura saiu limpa sobre `tests/test_fees.py` porque nada foi lido contra ele.

## 10. Regras deixadas a uma ferramenta

- `PY-02` repousa no passo `build`, que rodou e passou: isso estabelece que `python3 -m compileall -q lending` saiu com código 0. Se o comando estava configurado para decidir a regra é do registro saber. `build` carrega 1 regra; `test` carrega 0.
- Decidida por passo do registro: `PY-02`. Mantida só por leitura (uma execução verde nada decide sobre ela): `PY-01`.

## 11. Artefatos que o registro pressupõe e a árvore não tem

Nenhum: `deliver.py --standard app/standard.yaml --against app --specification spec` saiu limpo, sem nada ausente.

## 12. A execução

`run/fees-review`, em `delivery/lending/run/fees-review/` (`run.json`, `run.log`, `build.log`, `test.log`), cwd `app`. Passos, todos do registro e nenhum da invocação: `build` (`python3 -m compileall -q lending`, exit 0) e `test` (`python3 -m pytest -q tests`, exit 0). Resultado: `passed`; 0 falhas contadas (a passada `failures` não rodou). Nenhuma regra espera um passo que o registro não declare.

## 13. O trace

Na etapa de situar, `trace.py --check app` imprimiu `no drift: 1 binding(s) match the specification and the code as both stand now`, sem recibo de supressão. Isto não é achado e nada decide sobre a mudança: diz apenas que o vínculo de volta à especificação ainda descreve esta árvore. Nenhuma classe de drift, nenhuma rota a nomear.

## 14. O que a conformidade vinculou, e o que deixou devido

- Revinculado: `bound rules/lending/late-fee-per-overdue-day to 1 file(s)` (`lending/fees.py`). Nenhum nó deixado de escrever por um achado; nenhuma marca `collateral` ou contestada. `tests/test_fees.py` fica `unbound`.
- Registro: `siegard-reconcile/fees-review.md`; retornos: `siegard-reconcile/fees-review.returns/` (na raiz do git do target, `/tmp/rcbench/runs/compaction-resume-2/p`).
- Agora, `trace.py --check app`: `no drift: 1 binding(s) match the specification and the code as both stand now`.
- Agora, `trace.py --owed app`: `nothing owed: no reconciliation record under /tmp/rcbench/runs/compaction-resume-2/p/siegard-reconcile holds a finding against a node under app that no record cleared`, e lista à parte `1 unstated fact(s) the records name, over 1 file(s)` — o mesmo achado de `lending/fees.py`, `each is the analysis's to close, through the node that gives the fact a home`. Nenhum dos dois é veredito, e nenhuma rota é escolhida aqui.
- Achados que a dobra pôs nas `notes` do registro por nomearem nó a que nenhum arquivo revisado está vinculado: nenhum.

## 15. O que este framework não revisa

As quatro passadas julgam se os testes provam os critérios da tarefa, se o código declara só o que a especificação mantém, se o código segue as regras de leitura do standard e por que uma execução falhou. Fora disso nada é revisado: arquivos fora do conjunto listado, comportamento não exercido pela suíte, e se os passos de ferramenta estavam configurados para decidir as regras que repousam neles.

## 16. O que as passadas deixaram de lado como julgamento de outra

- `standard`: The tests' date arithmetic, which no rule in scope names.
- `conformance` sobre `tests/test_fees.py`: The tests assert the fee in cents per day, which is the coverage pass's to weigh.

## 17. Passadas em linha

`coverage`, `conformance` e `standard` rodaram em linha: nenhum agente deste plugin está registrado nesta sessão, e todo spawn (`siegard:coverage-auditor`, `siegard:specification-conformance-reviewer`, `siegard:standard-conformance-reviewer`) falhou; cada passada aplicou em linha o arquivo do seu agente.

## 18. Saída final do validador

```
derived delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 1 finding(s)
```

Verificações iniciais, verbatim, ambas exit 0:

```
plan checked: work/lending/plan.json matches 3 node(s)
delivery checked: delivery/lending/delivery.json matches 2 node(s)
```

`deliver.py --node delivery/lending/review/fees-review.md delivery/lending`: `review/fees-review: sound on its own. Cross-node checks and plan checks did not run; they run on the whole delivery.`

## 19. Onde os reparos moram

- código, ou um critério registrado como não atendido: `/implement-task` sobre a mesma tarefa;
- um fato declarado no código que nenhum nó mantém (o achado `unstated` acima): estender a especificação por `/analyse`, chegando à tarefa por `/plan-work`;
- uma regra do standard que pareça errada: quem é dono do registro a muda.

Esta revisão não entrega nenhuma invocação adiante: que rota cada achado merece — ou se merece alguma — é decisão sua. A cobertura parcial e o fato decidido só no código tocam a mesma pergunta (quanto vale a taxa no limite do vencimento), e o que a resolve é a especificação dizer como os dias se contam.

O registro escrito: `delivery/lending/review/fees-review.md`; `delivery/lending/delivery.json` foi derivado pelo validador. Nada foi commitado; `git diff` sobre `delivery/lending` é a revisão desta revisão.
