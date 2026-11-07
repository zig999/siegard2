# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos
- `implementation/fees/compute-late-fee` (delivery/lending/implementation/fees/compute-late-fee.md) e `proof/fees/compute-late-fee` (delivery/lending/proof/fees/compute-late-fee.md, pin sha256:14c6462da7c5c4b6c8a3515371a6a7194e155dba9bda7654aebe1e4c1b2b2e5a).
- Primeira entrega: não é re-entrega (não havia registro no caminho da tarefa).

## Caminhos criados, modificados ou removidos (relativos a `app/`)
- `lending/fees.py` — criado (registro de implementação, `files`).
- `tests/test_fees.py` — criado (registro de prova, `tests`).
`deliver.py --unrecorded` confirmou: "every path this tree changed under .../app is named by the 2 record(s) given".

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true` no registro de implementação.

## Inferências e divergências registradas
- Inferência (implementação): "a loan not yet returned is refused with a ValueError rather than answered a fee." — de: "the rule states the fee of a loan returned after its due date and states nothing of a loan still out". Nenhum nó a decide; não foi fixada por teste.
- Divergências: nenhuma, em nenhum dos dois registros.

## Nós implementados sem teste que os demonstre
- `rules/lending/late-fee-per-overdue-day` — nenhum teste carrega `demonstrates`. O `untested` da prova diz: "its fact is BRL 1.00 for every count of overdue days, a totality over a set the node does not enumerate, so no finite test decides it whole; the criterion tests sample its boundary and one representative."

## O que a prova deixou sem provar, casos descartados e discordâncias
- `untested`: o nó acima; e "a loan not yet returned is refused with a ValueError, a behavior the implementation inferred and no node decides."
- `not_applicable`: devolução datada antes do empréstimo (nenhum critério ou nó a declara); fração de dia de atraso (empréstimos carregam datas sem horário); dois cálculos simultâneos sobre um empréstimo (o cálculo lê um empréstimo imutável e não escreve nada).
- `contested`: nenhuma.
- Testes escritos (tests/test_fees.py): devolução na data de vencimento → 0; devolução antes → 0; um dia de atraso → 100; atraso de 13 dias atravessando fim de mês → 1300.

## O que a implementação adiou e o que deve continuar funcionando
O registro de implementação não declara nada adiado nem nada que deva continuar funcionando além do que já está em `files`.

## Rastreabilidade
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `app/lending/fees.py` ("bound rules/lending/late-fee-per-overdue-day to 1 file(s); 1 binding(s) written at .../siegard-trace.json").
- Nenhum vínculo recusado. Nenhum recibo de vínculos desatualizados foi impresso, então não há invocação de `/reconcile` a entregar.

## Passos executados inline
Esta sessão não pode criar subagentes. Os passos 3 (Implement, disciplina de `agents/task-implementer.md`) e 5 (Prove, disciplina de `agents/test-author.md`) rodaram inline, no mesmo contexto: código e testes foram escritos pela mesma sessão. A revisão deve pesar isso — a separação entre quem decide o comportamento e quem decide o que o prova não existiu nesta entrega.

## Saída final do validador (verbatim)
```
derived /tmp/it3/runs/compaction-resume-2/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido do arquivo do projeto (`siegard.json` → `standard: app/standard.yaml`), registrado como `standard.yaml` relativo a `app/`, pin sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6, nos dois registros.
- Regras: PY-01 (dinheiro em centavos inteiros, leitura) e PY-02 (todo módulo compila, decidida pelo passo build). Nenhuma divergência divulgada.
- Pressupostos: a tarefa não declara `produces`; o padrão pressupõe a árvore como está, e ela o satisfaz (`deliver.py --standard` limpo).
- `--outstanding` não listou registros sem padrão nem com outro padrão ou versão anterior.

## Execuções capturadas
- `run/fees-compute-late-fee-build` — passed (build=python3 -m compileall -q lending).
- `run/fees-compute-late-fee-suite` — passed (build, depois test=python3 -m pytest -q tests: "5 passed").
- Nenhuma execução vermelha; nenhum diagnóstico.
- Setup não rodou: o registro não declara comando de papel `install`.

## Dependências instaladas
Nenhuma.

## O que /review-change ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa; julga se os testes provam os critérios, se o código afirma só o que a especificação contém, se segue o padrão (PY-01 é de leitura) e por que algo falhou. Uma suíte verde aqui cobre uma tarefa. Também restampa os vínculos do rastro na passagem de conformidade.

## Próximo passo
A revisão recusa enquanto `delivery/lending` tiver mudanças não commitadas ("git status --porcelain -- .../delivery/lending is not empty"). Primeiro, você faz o commit desta entrega: `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/` e `siegard-trace.json`. Depois, cole:

```
/review-change /tmp/it3/runs/compaction-resume-2/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```
