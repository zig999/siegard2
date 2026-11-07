# /implement-task — task/fees/compute-late-fee (lending, target app)

## Registros escritos
- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md`
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md`
- Não foi uma re-entrega: não havia registro no caminho da tarefa.

## Caminhos que a entrega criou (conjunto de arquivos para `/review-change`)
- `lending/fees.py` (criado; `files` da implementação)
- `tests/test_fees.py` (criado; `tests` da prova)

`deliver.py --unrecorded` confirmou: «Every path this tree changed under app is named by the 2 record(s) given».

## Critérios registrados como não atendidos
Nenhum. Os dois critérios da tarefa estão registrados como `met: true`.

## Inferências e desvios registrados
- Inferência: «a loan not yet returned is refused with a ValueError rather than answered a fee.» — a partir de: «the rule states the fee of a loan returned after its due date and states nothing of a loan still out».
- Nenhum desvio declarado contra o padrão, em nenhum dos dois registros.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `tests/test_fees.py::test_each_further_calendar_day_after_the_due_date_adds_100_cents`. A prova não traz `untested`.

## O que a prova deixou sem provar, casos descartados, divergências
Nada registrado: a prova não traz `unproven`, casos descartados nem divergências.

## O que a implementação adiou e o que deve continuar funcionando
Nada registrado.

## Rastreabilidade
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 vínculo, em `siegard-trace.json` na raiz do projeto).
- `trace.py --bind-record` não recusou nenhum vínculo e não imprimiu recibo de vínculos desatualizados; portanto nenhuma invocação de `/reconcile` é devida por esta entrega.

## Etapas executadas inline
Implement (etapa 3) e Prove (etapa 5) rodaram inline, no contexto desta sessão, aplicando a disciplina de `agents/task-implementer.md` e `agents/test-author.md`: a sessão não pode criar subagentes. Por isso fonte e testes foram escritos no mesmo contexto — a revisão deve ler os testes sabendo disso.

## Saída final do validador (verbatim)
```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido pelo arquivo do projeto: `siegard.json` → `standard: app/standard.yaml` (em relação à raiz do target: `standard.yaml`).
- Pin: `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, o mesmo nos dois registros.
- Desvios divulgados: nenhum.
- Pressupostos: `deliver.py --standard ... --against app` passou limpo, isto é, a árvore já sustenta o que o padrão pressupõe; a tarefa não declara `produces`.
- `--outstanding` não imprimiu linhas sobre registros sem padrão, com outro padrão ou com versão anterior dele.

## Execuções capturadas
- `run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`, timeout 60 s).
- `run/fees-compute-late-fee-suite` — passed na primeira tentativa (build, depois test: `python3 -m pytest -q tests`, timeout 120 s).
- Nenhuma execução falhou; nenhum diagnóstico de suíte vermelha.
- Setup não rodou: o registro não declara comando com papel `install`.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se a fonte afirma só o que a especificação sustenta, se segue o padrão e por que algo falhou. A suíte verde aqui cobre uma tarefa só.

## Próximo passo
`/review-change` hoje recusa as entradas: «git status --porcelain -- /tmp/it3/runs2/compaction-resume-late-2/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make». A entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`) está sem commit; o commit é decisão da pessoa. Depois do commit, a invocação pronta para colar:

```
/review-change /tmp/it3/runs2/compaction-resume-late-2/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```
