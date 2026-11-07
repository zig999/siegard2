# Handoff (verbatim from handoff.py --render)

```
lending · task 1/1 delivered · phase reviewed
```

Nada espera por você; a revisão do cálculo da multa por atraso terminou com 1 achado, que é seu para encaminhar ou não.

O achado: o código conta um dia de atraso como a diferença entre a devolução e o vencimento (devolver no dia seguinte custa 100 centavos), e a especificação não diz se o dia da devolução entra na conta. Se quiser fechá-lo, o reparo iria pela análise da especificação e depois pelo plano.

Os testes provam a multa zero para devolução em dia ou antecipada; para devolução atrasada, provam os 100 centavos por dia adicional, mas aceitam tanto n quanto n-1 dias cobrados, então o valor exato de um atraso fica sem prova.

Compilação e testes do projeto rodaram e passaram (4 testes), por isso a leitura de falhas não rodou. A regra de dinheiro em centavos inteiros foi lida e não há desvio; o arquivo de testes não é alcançado por regra nenhuma do padrão do projeto. O vínculo da regra da multa com o código foi renovado. As leituras foram feitas nesta própria sessão, porque os agentes do plugin não estavam disponíveis.

O relatório completo, com as evidências e as saídas dos comandos, está no caminho abaixo.

Relatório completo: /tmp/rcbench/runs/full-review--before-1/p/.git/siegard/handoff/20261107T163844Z-review-change.md

---

# Full report (as saved at the handoff's report path)

# Revisão `fees-review` — task/fees/compute-late-fee (iniciativa `lending`, target `app`)

## Achados, em contagens (saída de `deliver.py --findings`, verbatim)

```
fees-review.md: 1 finding(s) over 2 reviewed file(s)
  by pass: conformance 1
  conformance by kind: unstated 1
  standard by rule cited: none
  failures by cause: none
  by file: lending/fees.py 1
  a count says how many findings share a field, never which route any takes or whether it takes one
```

- conformance / `unstated`: 1 (lending/fees.py) — rota onde um reparo iria: estender a especificação por `/analyse`, chegando à task por `/plan-work`.
- standard: 0. failures: 0 (a pass não rodou; ver abaixo). coverage: nenhum achado; um critério `partial` (ver abaixo).

## Todos os achados, por pass

### conformance (1)

- **lending/fees.py**, linha 7, a contagem de dias de atraso em `late_fee_cents` — `kind: unstated`, nó `rules/lending/late-fee-per-overdue-day`.
  - Evidência: `overdue_days = (loan.returned_on - loan.due_on).days`
  - Custo: o nó cobra BRL 1.00 "for each calendar day between its due date and its return" e não diz se o dia da devolução conta; a contagem que esta linha adota (devolução um dia após o vencimento = um dia, 100 cents) é uma decisão que vive só no código. Quem procurar a regra na especificação não a encontra, e uma leitura que conte só os dias estritamente entre as duas datas cobraria 100 cents a menos em toda devolução atrasada.
  - Correção: a especificação declarar como se contam os dias corridos entre o vencimento e a devolução, como fato decidido de `rules/lending/late-fee-per-overdue-day`, e o código ser lido contra isso.
  - O próprio registro de implementação declara isso como `inferred`, e o proof o lista em `untested`.

### coverage (0 achados)
### standard (0 achados) — PY-01 em escopo sobre lending/fees.py; nenhum desvio (o valor é `int` de cents, sem float).
### failures — não rodou.

## Passes que não rodaram, e o que faltou

- **failures**: não rodou — `run/fees-review passed; there was no failure to read`. Nenhum input ausente.
- coverage, conformance e standard rodaram (inline; ver abaixo). Nenhuma certificação foi staged.

## Caminhos dos registros que não foram lidos (apagados ou fora do root)

Nenhum: os dois caminhos que os registros nomeiam (`lending/fees.py`, `tests/test_fees.py`) existem sob `app`.

## Critérios não cobertos

- "A loan returned after its due date carries 100 cents for each calendar day between its due date and its return." — **partial** (test: `test_each_further_calendar_day_after_the_due_date_adds_100_cents`). O que fica sem exercício: os 100 cents que cada dia corrido adicional soma são exercidos do 2º ao 40º dia de atraso, mas o valor de uma devolução específica não é fixado — o teste aceita qualquer taxa entre (n-1)*100 e n*100 cents para n dias de atraso, então uma implementação que cobre (n-1)*100 passa tanto quanto uma que cobre n*100, e a taxa de uma devolução um dia após o vencimento nunca é afirmada.
- "A loan returned on or before its due date carries a late fee of 0 cents." — **covered** por `test_a_loan_returned_on_its_due_date_carries_no_late_fee` e `test_a_loan_returned_before_its_due_date_carries_no_late_fee`.

## Testes sem critério

Nenhum (`unpaired: []`): os três testes de tests/test_fees.py se apoiam em algum critério da task.

## Nós sem teste que os demonstre, e certificações

- `rules/lending/late-fee-per-overdue-day`: nenhum teste do proof carrega `demonstrates`, então nenhuma certificação foi staged. Razão dada pelo proof (`untested`): "rules/lending/late-fee-per-overdue-day as a whole: the rule's per-day rate is held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the count of calendar days "between its due date and its return" is not stated by the node (whether an end day counts), so no finite test decides the fact whole without pinning the implementation's inference."

## O standard

- Resolvido pelo arquivo do projeto (`siegard.json` → `standard: app/standard.yaml`); a invocação não nomeou nenhum. Registro em `standard.yaml` (relativo a `app`), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- 2 regras: 1 decidida por leitura (PY-01), 1 por ferramenta (PY-02, sobre o step `build`).
- Em escopo por leitura sobre este conjunto: PY-01 ("Money is computed in integer cents, never in floating point."), alcançando `lending/fees.py`.
- `--reach` (verbatim):
  ```
  lending/fees.py: reading PY-01; tool PY-02
  tests/test_fees.py: reading none; tool none
  reached by no rule: 1 of 2
    tests/test_fees.py
  ```
  `tests/test_fees.py` não é alcançado por nenhuma regra: a leitura foi limpa ali porque nada foi lido contra ele — um fato sobre o registro, não um achado.
- PY-02 repousa sobre o step `build` (1 regra), que rodou e passou. Isso estabelece que `python3 -m compileall -q lending` saiu com 0; se esse comando está configurado para decidir PY-02 é do registro saber, não deste framework.
- Contra a especificação: "spec holds no constraint" — nenhuma constraint decidida por step, nenhuma deixada só à leitura.
- O registro não pressupõe artefato algum ("it presupposes nothing"). Nenhuma regra espera um step que o registro não declare.

## A execução

- `run/fees-review` (em `delivery/lending/run/fees-review/`), cwd `app`, timeout 120 s, steps do registro: `build` = `python3 -m compileall -q lending` (passed, exit 0) e `test` = `python3 -m pytest -q tests` (passed, exit 0; "4 passed in 0.01s"). Nenhum step do chamador. Resultado: `passed`; 0 falhas contadas. Saída em `build.log`, `test.log`, `run.log`.
- Nenhum step que uma regra espere ficou sem comando.

## O trace

- `trace.py --check app` na fase situate: "no drift: 1 binding(s) match the specification and the code as both stand now". Zero em todas as classes (`orphaned`, `moved`, `proof`, `code`); sem recibo de supressão. Rotas, se aparecessem: `--prune` para `orphaned`, `/reconcile` para `code` e `moved` fora desta revisão, `--release` para arquivo vinculado que a árvore não tem mais. Isto não é achado e nada diz sobre a mudança.

## O que a conformance pass vinculou, e o que deixou devido

- Restampado (recibo do bind, verbatim): "bound rules/lending/late-fee-per-overdue-day to 1 file(s)" / "1 binding(s) written at /tmp/rcbench/runs/full-review--before-1/p/siegard-trace.json, read from fees-review.md" — `rules/lending/late-fee-per-overdue-day` em `lending/fees.py`.
- Não escritos: nenhum; nenhum nó `collateral`, nenhum contestado; nenhuma release deixada devida.
- `tests/test_fees.py` ficou em `unbound` (lido, sem vínculo).
- Registro: `siegard-reconcile/fees-review.md`; retornos em `siegard-reconcile/fees-review.returns/` (na raiz git `/tmp/rcbench/runs/full-review--before-1/p`).
- `trace.py --check app` após o bind: "no drift". `trace.py --owed app`: "nothing owed" sobre nós; lista 1 fato `unstated` em lending/fees.py (o achado acima), que é da análise fechar.
- Nenhuma nota do fold termina em "owed a route of its own".
- Nota: o texto de `notes` do registro diz "Judged by 2 subagent(s)"; na verdade os dois julgamentos foram feitos inline nesta sessão (ver abaixo), e os retornos foram gravados diretamente no diretório de retornos, sem `--save-return`, porque não há transcript de subagente para ele ler.

## O que este framework não revisa

Desempenho, segurança além do que o registro declara a uma ferramenta, concorrência, estilo fora das regras do standard, e qualquer arquivo fora de `lending/fees.py` e `tests/test_fees.py`. O standard deste projeto tem uma única regra de leitura; a revisão é estreita nessa medida.

## O que as passes deixaram de lado como de outro julgamento

- conformance (lending/fees.py): a taxa é devolvida como `int` de cents enquanto `domain/lending/loan` declara `late_fee` como `decimal` em BRL — representação governada por PY-01 e forma que este arquivo não declara.
- conformance (tests/test_fees.py): o que os testes afirmam é da coverage pass, não um fato que o arquivo guarde.

## Passes que rodaram inline, e por quê

coverage, conformance e standard rodaram inline: nenhum agente deste plugin está registrado nesta sessão, e o spawn de `siegard:coverage-auditor`, `siegard:specification-conformance-reviewer` e `siegard:standard-conformance-reviewer` falhou. Apliquei a disciplina de cada arquivo em `agents/`. Esta sessão não escreveu nenhum nó que um juiz leria, então a conformance pass não precisou parar.

## Checagens que rodaram (verbatim)

```
plan checked: work/lending/plan.json matches 3 node(s)
delivery checked: delivery/lending/delivery.json matches 2 node(s)
```
`git status --porcelain -- delivery/lending`: vazio antes de qualquer escrita.

## Saída final do validador (verbatim)

```
derived delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 1 finding(s)
```

## Onde os reparos moram (rotas, não leitura dos achados)

- Código, ou critério registrado como não atendido: `/implement-task` sobre a mesma task.
- Fato no código que nenhum nó guarda (o achado `unstated`): estender a especificação por `/analyse`, chegando à task por `/plan-work`.
- Regra do standard que pareça errada: muda quem é dono do registro.

Esta revisão não entrega nenhuma invocação adiante: qual rota cada achado merece, se alguma, é decisão da pessoa.
