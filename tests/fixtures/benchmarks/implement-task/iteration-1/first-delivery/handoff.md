# /implement-task — task/fees/compute-late-fee (lending, target app)

## Nós escritos

- `implementation/fees/compute-late-fee` — pin `sha256:a14ffddc9e7212182107b45dfc299997791824e08164890aa412902396e0d8ac`
- `proof/fees/compute-late-fee` — pin `sha256:79e39a7b7aca6900373304d6f67a0ae11bc7fa50a3919636ba014cf1c6dca5e0`
- Primeira entrega, não uma re-entrega.

Entradas decididas, não perguntadas: a invocação não nomeou target nem slug. `siegard.json` declara um único target, `app`, e o `work_root` contém uma única iniciativa sem `closure.md`, `lending`. Assim os dois foram decididos e são declarados aqui. A raiz de entrega `delivery/lending` não existia e foi criada vazia.

## Caminhos alterados (relativos à raiz do target `app`)

- `lending/fees.py` — criado (implementation `files`)
- `tests/test_fees.py` — criado (proof `tests`)

`deliver.py --unrecorded`: `every path this tree changed under /tmp/itbench/runs/first-delivery-cand1/p/app is named by the 2 record(s) given`.

Fora do target, esta invocação escreveu ainda a raiz de entrega `delivery/lending/` (registros, `delivery.json`, duas runs) e `siegard-trace.json` na raiz do projeto (o bind).

## Critérios registrados como não atendidos

Nenhum. Os dois critérios estão com `met: true`.

## Inferências e divergências

Inferências (implementation):
1. O valor é computado sobre o registro `Loan` existente, lendo `due_on` e `returned_on`, num módulo novo `lending/fees.py` ao lado de `lending/loans.py` — de: o inventory nomeia `lending/loans.py` como dependência e o `Loan` e suas datas como o que não deve ser duplicado.
2. Os dias corridos entre o vencimento e a devolução são a diferença das duas datas em dias, então devolver no dia seguinte ao vencimento é um dia — de: o texto da regra ("each calendar day between its due date and its return") e os critérios da task.
3. `late_fee_cents` só é definido para um empréstimo com `returned_on` preenchido; um empréstimo não devolvido está fora do domínio e não recebe resposta própria — de: o objective da task ("Given a returned loan") e nenhum nó afirmando o que um empréstimo não devolvido carrega.

Divergências: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre

Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `tests/test_fees.py::test_a_loan_returned_across_a_month_end_carries_100_cents_per_calendar_day`. A demonstração é uma alegação; a certificação é da review.

## Não provado, casos descartados, discordâncias

- `untested`: a inferência de que um empréstimo não devolvido está fora do domínio de `late_fee_cents` é comportamento que nenhum nó decide; fica sem prova em vez de fixada por teste.
- `not_applicable`: empréstimo ainda não devolvido (objective restrito a empréstimo devolvido); entrada ausente ou vazia (a função recebe um `Loan`); duas computações simultâneas (lê um registro frozen e não escreve nada); dependência que falha ou demora (não chama nenhuma).
- `contested`: nenhuma.

## Adiado e preservado

Nada adiado. Nada preservado: a task não alterou comportamento existente.

## Trace

- `bound rules/lending/late-fee-per-overdue-day to 1 file(s)` — `app/lending/fees.py`, em `/tmp/itbench/runs/first-delivery-cand1/p/siegard-trace.json`.
- Nenhum binding recusado. Nenhum recibo de bindings desatualizados foi impresso, então não há invocação de `/reconcile` a entregar.

## Passos executados inline

Os passos 3 (implement) e 5 (prove) rodaram inline nesta sessão, que não pode criar subagentes: os arquivos `agents/task-implementer.md` e `agents/test-author.md` foram aplicados no lugar. Fonte e testes foram, portanto, escritos no mesmo contexto — a separação entre os dois produtores não existiu nesta entrega, e a review é quem a supre. As duas notas dos registros dizem o mesmo.

## Portas e recomendação

Esta invocação não parou num BLOCKING nem numa contradição. Das portas: `/review-change` hoje recusa — `git status --porcelain -- /tmp/itbench/runs/first-delivery-cand1/p/delivery/lending is not empty`, porque a entrega ainda não foi commitada (precondition unmet). `/reconcile` não tem trabalho: o bind não imprimiu recibo de bindings desatualizados. Nenhuma porta é recomendada agora. O próximo passo é da pessoa: commitar esta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`); depois disso a recusa do `/review-change` deixa de valer, e ele é a porta seguinte.

## Saída final do validador

```
derived /tmp/itbench/runs/first-delivery-cand1/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard

- Resolvido pelo arquivo do projeto (`siegard.json`, campo `standard`): `standard.yaml` relativo ao target (`/tmp/itbench/runs/first-delivery-cand1/p/app/standard.yaml`), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, nos dois registros.
- Regras: PY-01 (dinheiro em centavos inteiros; decidida por leitura) e PY-02 (todo módulo compila; decidida pelo step `build`). Nenhuma divergência declarada contra elas.
- Pressupõe nada; o tree tem tudo de que precisa. Autoriza 0 dependências.
- Nenhum registro desta raiz fixa outro standard ou outra versão.

## Runs capturadas

- `delivery/lending/run/fees-compute-late-fee-build` — passed (`build=python3 -m compileall -q lending`)
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (`build`, depois `test=python3 -m pytest -q tests`)

Nenhuma run falhou. O setup não rodou: o registry não declara step com papel `install` ("setup: nothing runs — no step carries the role this phase needs").

## Dependências instaladas

Nenhuma.

## O que o `/review-change` ainda faz

Roda os mesmos steps de novo sobre a mudança inteira, não sobre uma task; e julga — se os testes provam os critérios, se a fonte afirma só o que a especificação contém, se segue o mesmo standard (PY-01 é de leitura) e por que algo falhou. Uma suite verde aqui é verde sobre uma task. Nesta entrega, como fonte e testes foram escritos no mesmo contexto, a review é também o único juízo separado do produtor.

## Handoff

`/review-change` invocation ready to paste, depois de a pessoa commitar a entrega:

```
/review-change /tmp/itbench/runs/first-delivery-cand1/p --target app --slug lending --task task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard standard.yaml
```

Preencher e invocar são da pessoa; esta invocação parou aqui.
