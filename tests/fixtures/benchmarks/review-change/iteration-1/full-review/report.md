# Handoff (verbatim, as handoff.py --render printed it)

```
lending · task 1/1 delivered · phase reviewed
```

Revisão concluída: 2 achados, ambos de conformidade com a especificação, ambos no código da multa — fatos que o código decide e nenhuma regra da especificação declara. Um: a contagem de dias de atraso é a diferença entre devolução e vencimento, e a regra não diz qual extremo conta. Dois: devolução no vencimento ou antes não gera multa, e a regra só fala da devolução depois do vencimento. Onde um reparo desses iria: estender a especificação (análise e depois plano), não o código; se algum merece reparo é decisão sua. Cobertura: o critério de zero centavos está coberto; o de 100 centavos por dia está parcial, porque o teste aceita uma janela de 100 centavos e nenhum teste fixa o valor de um dia de atraso. Padrão do projeto: a regra de dinheiro em centavos inteiros alcança o código e não há desvio; o arquivo de testes não é alcançado por nenhuma regra. Execução da compilação e da suíte: verde, 4 testes passaram, então o diagnóstico de falhas não rodou. Nenhum agente do plugin estava registrado nesta sessão: cobertura, conformidade e padrão rodaram em linha, sob a disciplina de cada agente. A validação final da entrega passou.

Relatório completo: /tmp/rcbench/runs/full-review-2/p/.git/siegard/handoff/20261107T170429Z-review-change.md

---

# Full report (as saved by handoff.py --save-report)

# Revisão `fees-review` — task/fees/compute-late-fee (iniciativa `lending`, alvo `app`)

## 1. Achados em contagem

```
fees-review.md: 2 finding(s) over 2 reviewed file(s)
  by pass: conformance 2
  conformance by kind: unstated 2
  standard by rule cited: none
  failures by cause: none
  by file: lending/fees.py 2
  a count says how many findings share a field, never which route any takes or whether it takes one
```

Agrupamento: 2 achados de conformance, ambos `unstated`, ambos em `lending/fees.py` — o lugar onde um reparo dessa forma iria é estender a especificação por `/analyse` (e daí `/plan-work`), não o código. Nenhum de standard, nenhum de failures.

## 2. Os achados, por pass

### conformance

1. `lending/fees.py`, a contagem de dias em `late_fee_cents`, linha 7 — kind `unstated`
   - evidência: `overdue_days = (loan.returned_on - loan.due_on).days`
   - custo: o "each calendar day between its due date and its return" do nó não diz se a data de vencimento ou o dia da devolução contam; o código decide que a contagem é a diferença das datas, então um empréstimo devolvido um dia atrasado carrega BRL 1.00, e essa decisão vive só nesta linha.
   - correção: `rules/lending/late-fee-per-overdue-day` passa a dizer como os dias corridos entre vencimento e devolução são contados (qual extremo conta, se algum), e o código é lido contra isso.
2. `lending/fees.py`, a guarda em `late_fee_cents`, linhas 8-9 — kind `unstated`
   - evidência: `if overdue_days <= 0:` / `    return 0`
   - custo: o nó só declara a multa de um empréstimo devolvido depois do vencimento; que um empréstimo devolvido no vencimento ou antes não carrega multa vive só aqui e no critério da task, então o próximo leitor procura isso na especificação e não encontra.
   - correção: um nó, muito plausivelmente `rules/lending/late-fee-per-overdue-day`, ganha a declaração de que um empréstimo devolvido no vencimento ou antes não carrega multa.

### coverage, standard, failures

Nenhum achado.

## 3. Passes que não rodaram

- failures: não rodou — `run/fees-review passed; there was no failure to read`.
- coverage, conformance e standard rodaram (inline; ver item 17).

## 4. Caminhos dos registros fora do conjunto

Nenhum. Os registros nomeiam `lending/fees.py` (implementation) e `tests/test_fees.py` (proof); ambos existem sob a raiz do alvo e ambos foram lidos.

## 5. Critérios não cobertos por completo

- "A loan returned after its due date carries 100 cents for each calendar day between its due date and its return." — `partial`, teste `tests/test_fees.py::test_each_further_calendar_day_after_the_due_date_adds_100_cents`. O passo de 100 centavos por dia corrido adicional, do segundo ao quadragésimo dia após o vencimento, é exercido; o valor que uma devolução dada carrega não é, porque o teste aceita qualquer multa de `(days_late - 1) * 100` a `days_late * 100` centavos — uma contagem de dias errada por um em qualquer direção ainda passa, e nenhum teste fixa a multa de um empréstimo devolvido um dia após o vencimento. O próprio critério não diz se o vencimento ou o dia da devolução contam entre os dias "between".
- "A loan returned on or before its due date carries a late fee of 0 cents." — `covered` por `test_a_loan_returned_on_its_due_date_carries_no_late_fee` e `test_a_loan_returned_before_its_due_date_carries_no_late_fee`.

## 6. Testes sem critério

Nenhum (`unpaired: []`): os três testes de `tests/test_fees.py` se ligam a um dos dois critérios.

## 7. Nós sem teste que os demonstre

- `rules/lending/late-fee-per-overdue-day`: nenhum teste do proof carrega `demonstrates`, então nenhuma certificação foi preparada. O motivo que o proof dá (`untested`): "the rule's per-day rate is held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the count of calendar days "between its due date and its return" is not stated by the node (whether an end day counts), so no finite test decides the fact whole without pinning the implementation's inference."

## 8. O standard

- Resolvido pelo arquivo do projeto (`siegard.json` → `standard: app/standard.yaml`, linha `standard:` de um projeto de um alvo); a invocação não nomeou nenhum. Registrado como `at: standard.yaml`, `pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Em escopo, decidida por leitura: `PY-01` ("Money is computed in integer cents, never in floating point."), que alcança `lending/fees.py`. Nenhum desvio: a multa é `int` de centavos (`LATE_FEE_CENTS_PER_DAY = 100`).
- Deixada a uma ferramenta: `PY-02`, que repousa no passo `build`.

## 9. Caminhos que nenhuma regra alcança

```
lending/fees.py: reading PY-01; tool PY-02
tests/test_fees.py: reading none; tool none
reached by no rule: 1 of 2
  tests/test_fees.py
```

É um fato do registro, não um achado: a leitura foi limpa sobre `tests/test_fees.py` porque nada foi lido contra ele.

## 10. Regras deixadas a uma ferramenta

- `build` (`python3 -m compileall -q lending`) rodou e passou; 1 regra repousa nele (`PY-02`). O que isso resolve: o comando saiu com 0. Se o comando está configurado para decidir a regra que repousa nele é o registro que sabe.
- Contra a especificação: `/tmp/rcbench/runs/full-review-2/p/spec holds no constraint` — não há constraint decidida por passo nem constraint sem passo.

## 11. Artefatos que o registro pressupõe e a árvore não tem

Nenhum: "it presupposes nothing, so /tmp/rcbench/runs/full-review-2/p/app holds everything it needs to".

## 12. O run

- `run/fees-review`, cwd `/tmp/rcbench/runs/full-review-2/p/app`, timeout 120 s; passos do registro, na ordem dele: `build=python3 -m compileall -q lending` (passou, exit 0) e `test=python3 -m pytest -q tests` (passou, exit 0; `4 passed in 0.01s`). Nenhum passo veio da invocação.
- Resultado `passed`; 0 falhas contadas; o pass failures não rodou. Saída em `delivery/lending/run/fees-review/` (`run.json`, `run.log`, `build.log`, `test.log`).
- Nenhuma regra espera um passo para o qual o registro não declara comando.

## 13. O trace

```
trace: /tmp/rcbench/runs/full-review-2/p/siegard-trace.json — one file per git toplevel; every target under it reads this same one
no drift: 1 binding(s) match the specification and the code as both stand now
```

Zero em todas as classes (`orphaned`, `moved`, `proof`, `code`). Isto não é um achado e não diz nada sobre a mudança: diz apenas que o elo de volta à especificação ainda descreve esta árvore. Nenhum recibo de supressão.

## 14. O que o pass de conformance vinculou, e o que deixou em aberto

- Vinculado: `bound rules/lending/late-fee-per-overdue-day to 1 file(s)` — `1 binding(s) written at /tmp/rcbench/runs/full-review-2/p/siegard-trace.json, read from fees-review.md` (sobre `lending/fees.py`).
- Não vinculado: nenhum nó (o fold: `1 node(s) cleared, 0 not — 0 of those collateral`). `tests/test_fees.py` fica em `unbound`.
- Registro em `siegard-reconcile/fees-review.md`; retornos em `siegard-reconcile/fees-review.returns/lending__fees.py.yaml` e `tests__test_fees.py.yaml` (no toplevel git do alvo).
- Os 2 fatos `unstated` estão no registro sob `unstated`; `trace.py --owed` os lista, `trace.py --check` não os vê. Nenhum é veredito sobre a mudança, e nenhuma rota é escolhida aqui.
- Nenhum achado foi para as `notes` do registro como "owed a route of its own".

## 15. O que este framework não revisa

Desempenho, segurança além do que os próprios passos do registro decidem, legibilidade, e qualquer coisa fora dos dois arquivos do conjunto. `PY-02` é decidida só pelo que o comando `build` faz. Quatro passes não são todos os passes.

## 16. O que os passes deixaram de lado como julgamento de outro

- conformance (`lending/fees.py`): a multa como `int` de centavos, enquanto `domain/lending/loan` declara `late_fee` como valor `decimal` em BRL — é representação, governada por `PY-01`, não um fato de domínio que este pass pesa.
- conformance (`tests/test_fees.py`): as asserções exercem a regra em vez de declará-la; se provam os critérios é do pass coverage. O arquivo não guarda o fato do nó (`nowhere`).
- standard: `tests/test_fees.py` está fora do escopo de toda regra.

## 17. Passes que rodaram inline

Nenhum agente deste plugin estava registrado na sessão: os spawns de `siegard:coverage-auditor`, `siegard:specification-conformance-reviewer` (2, um por arquivo, onda 1) e `siegard:standard-conformance-reviewer` falharam com "Agent type '...' not found". Por isso coverage, conformance e standard rodaram inline, cada um sob a disciplina do seu arquivo em `agents/`. A sessão não escreveu nenhum nó que um subagente leria, então o conformance inline não precisou parar. Os dois retornos de conformance foram escritos diretamente no caminho de retornos porque `trace.py --save-return` só aceita uma transcrição de subagente (`cannot run: ... holds no assistant message; it is not a subagent's transcript`, exit 2); as notas que o fold escreveu ("Judged by 2 subagent(s), one per file") descrevem a forma dos retornos, não quem os produziu. Failures não rodou (run verde); certificação não foi preparada (nenhum `demonstrates`).

## 18. Saída final do validador, verbatim

```
derived /tmp/rcbench/runs/full-review-2/p/delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 2 finding(s)
```

Verificações de entrada, verbatim:

```
plan checked: /tmp/rcbench/runs/full-review-2/p/work/lending/plan.json matches 3 node(s)
delivery checked: /tmp/rcbench/runs/full-review-2/p/delivery/lending/delivery.json matches 2 node(s)
```

`git status --porcelain -- delivery/lending` não imprimiu nada antes de qualquer escrita. `deliver.py --node` sobre o registro: `review/fees-review: sound on its own. Cross-node checks and plan checks did not run; they run on the whole delivery.`

Decidido e divulgado: o projeto `/tmp/rcbench/runs/full-review-2/p`, o alvo `app`, o slug `lending` e o nome `fees-review` foram todos nomeados na invocação; nada foi inferido.

## 19. Onde os reparos moram

- código-fonte, ou um critério registrado como não atendido: `/implement-task` sobre a mesma task;
- um fato declarado no código que nenhum nó guarda (os 2 achados `unstated`): estender a especificação por `/analyse`, e chegar à task por `/plan-work`;
- uma regra do standard que pareça errada: muda quem é dono do registro.

Esta revisão não entrega nenhuma invocação: qual rota cada achado merece — ou se merece alguma — é decisão sua.
