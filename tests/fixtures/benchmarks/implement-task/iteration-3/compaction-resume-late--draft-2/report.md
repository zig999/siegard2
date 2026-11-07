# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos
- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md`
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md`
- Não foi re-entrega: nenhum registro existia no caminho da tarefa (`--outstanding` a listou como entregável, sem nota BLOCKING).
- Entradas decididas e declaradas: alvo `app` e slug `lending`, nomeados na invocação; raiz do projeto `/tmp/it3/runs/compaction-resume-late-2/p`.

## Caminhos que a entrega criou, modificou ou apagou (relativos à raiz-fonte do alvo `app`)
- `lending/fees.py` — criado (`files` da implementação)
- `tests/test_fees.py` — criado (`tests` da prova)

`deliver.py --unrecorded` sobre os dois registros: «Every path this tree changed under /tmp/it3/runs/compaction-resume-late-2/p/app is named by the 2 record(s) given» (exit 0).

## Critérios registrados como não atendidos
Nenhum. Os dois critérios da tarefa estão `met: true`.

## Inferências e desvios registrados
- Inferência (implementação): «a loan not yet returned is refused with a ValueError rather than answered a fee.» — de: «the rule states the fee of a loan returned after its due date and states nothing of a loan still out».
- Desvios declarados contra o padrão: nenhum, em nenhum dos dois registros.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `test_each_further_calendar_day_after_the_due_date_adds_100_cents`. A prova não tem `untested`.

## Não provado, casos de borda descartados, discordâncias
Nenhum registrado pela prova.

## O que a implementação adiou, e o que deve continuar funcionando
Nada registrado (Notas: «None.»).

## Rastro (trace)
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `app/lending/fees.py` (1 vínculo escrito em `siegard-trace.json`).
- Nenhum vínculo recusado. Nenhum recibo de vínculos desatualizados foi impresso; por isso nenhuma invocação de `/reconcile` é devida por esta entrega.

## Passos executados inline
As etapas 3 (Implement) e 5 (Prove) rodaram inline, aplicando a disciplina de `agents/task-implementer.md` e `agents/test-author.md` na própria sessão, porque esta sessão não pode criar subagentes. Por isso os testes foram escritos no mesmo contexto que escreveu o código — o fallback inline que a skill admite, declarado aqui.

## Portas
- `/review-change` — a verificação do ponto de entrada recusa como a árvore está: «git status --porcelain -- /tmp/it3/runs/compaction-resume-late-2/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make».
- Recomendado (derivado): fazer o commit desta entrega e então rodar `/review-change`. Critério: uma porta que o próprio ponto de entrada recusa fica excluída, e a recusa cai só com a raiz de entrega commitada. Fato decisivo: a recusa acima. Fato reversor: `git status --porcelain` sobre `delivery/lending` não imprimir nada.
- `/reconcile` — não verificado por script; não há recibo de vínculos desatualizados, então nada aguarda reconciliação.

## Saída final do validador (verbatim)
```
derived /tmp/it3/runs/compaction-resume-late-2/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido do arquivo do projeto (`siegard.json`, campo `standard`): `app/standard.yaml`, registrado como `standard.yaml` relativo à raiz-fonte do alvo, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Desvios declarados: nenhum.
- Pressupõe: a árvore já o contém (a tarefa não declara `produces`); `deliver.py --standard` passou limpo.
- `--outstanding` não listou registros sem padrão, com outro padrão, ou com versão anterior dele.

## Execuções capturadas
- `run/fees-compute-late-fee-build` — passou (build: `python3 -m compileall -q lending`, timeout 60 s).
- `run/fees-compute-late-fee-suite` — passou na primeira tentativa (build, depois test: `python3 -m pytest -q tests`, timeout 120 s).
- Nenhuma execução falhou; nenhuma suíte vermelha foi diagnosticada.
- Setup não rodou: o registro não declara comando com papel `install`.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se o código afirma só o que a especificação contém, se segue o padrão e por que algo falhou. A suíte verde aqui cobre uma tarefa.

## Handoff
Depois de commitar a entrega (código em `app/lending/fees.py`, `app/tests/test_fees.py`, a raiz `delivery/lending` e `siegard-trace.json`):

```
/review-change /tmp/it3/runs/compaction-resume-late-2/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```

---

# Handoff (verbatim, as rendered by handoff.py --render)

```
lending · task 1/1 delivered · phase review
```

1. A multa por atraso está entregue e validada; a revisão só roda após o commit desta entrega.
   - **Recomendado** `commit`: Fazer o commit desta entrega e então pedir a revisão. A revisão recusa rodar com a pasta de entrega sem commit, como está hoje. Mudaria se a pasta de entrega já estiver commitada.
   - `revisar`: Revisar agora: excluída, recusa com a pasta de entrega sem commit.
   - `reconciliar`: Reconciliar vínculos: nada aguarda, nenhum ficou desatualizado.
   - Se nenhuma for tomada: A entrega fica sem commit e sem revisão.

   ```
   /review-change /tmp/it3/runs/compaction-resume-late-2/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
   ```

Relatório completo: /tmp/it3/runs/compaction-resume-late-2/p/.git/siegard/handoff/20261107T183939Z-implement-task.md
