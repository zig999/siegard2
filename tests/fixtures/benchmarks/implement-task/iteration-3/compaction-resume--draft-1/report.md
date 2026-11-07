# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos
- implementation/fees/compute-late-fee (`delivery/lending/implementation/fees/compute-late-fee.md`)
- proof/fees/compute-late-fee (`delivery/lending/proof/fees/compute-late-fee.md`, pin sha256:55f6dbc83d242dc82d204ce5be2a59e74b433827944b38eec1421790711594a6)
- Primeira entrega, não uma re-entrega.

## Caminhos criados pela entrega (relativos à raiz do alvo `app`)
- `lending/fees.py` — criado (implementation `files`)
- `tests/test_fees.py` — criado (proof `tests`)
`deliver.py --unrecorded` confirmou: "every path this tree changed under app is named by the 2 record(s) given".

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true` no registro de implementação.

## Inferências e divergências
- Inferência (implementação): um empréstimo ainda não devolvido é recusado com `ValueError` em vez de responder uma multa — a regra fala só de empréstimo devolvido após o vencimento e nada de um ainda em aberto.
- Divergências: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `test_a_loan_returned_late_carries_100_cents_for_each_calendar_day_past_its_due_date`.

## O que a prova deixou sem prova, casos descartados e discordâncias
- Sem prova: a recusa com `ValueError` de um empréstimo não devolvido — inferência de comportamento que nenhum nó decide, portanto não fixada por teste.
- Casos descartados (`not_applicable`): entrada ausente ou vazia; coleção vazia ou duplicata; dependência que falha ou demora; duas operações simultâneas sobre o mesmo empréstimo — nenhuma obrigação os alcança.
- Discordâncias (`contested`): nenhuma.

## O que a implementação adiou e o que precisa continuar funcionando
Nada adiado; o registro não nomeia nada que precise continuar funcionando além do próprio arquivo.

## Rastreio
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `app/lending/fees.py` (em `siegard-trace.json`).
- Nenhum vínculo recusado. O vínculo não imprimiu aviso de vínculos desatualizados, então nenhuma invocação de `/reconcile` é entregue.

## Passos executados inline
- Implementar (passo 3) e Provar (passo 5) rodaram inline, nesta mesma sessão, e não em subagentes: esta sessão não pode criar subagentes. A disciplina de `agents/task-implementer.md` e `agents/test-author.md` foi aplicada no lugar. Por isso os testes foram escritos no mesmo contexto que escreveu a fonte — a separação entre os dois produtores não vale para esta entrega, e a revisão deve pesar isso.

## Saída final do validador (verbatim)
```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido pelo arquivo do projeto (`siegard.json`, campo `standard`): `app/standard.yaml`, registrado como `standard.yaml` relativo à raiz do alvo, pin sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6.
- Divergências declaradas contra ele: nenhuma.
- Pressupõe: nada declarado em `presupposes`; a árvore já atende.
- `--outstanding` imprime: "standard.yaml (target app): pinned by 2 record(s); an invocation naming no standard now writes source these rules will still be read against". Nenhum registro sem pin ou com outro padrão.

## Execuções capturadas
- `delivery/lending/run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (build + test: `python3 -m pytest -q tests`).
- Setup não rodou: o registro não declara comando com papel `install`.
- Nenhuma execução vermelha.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se a fonte afirma só o que a especificação contém, se segue o padrão e por que algo falhou. A suíte verde aqui cobre uma tarefa.

## Próximo passo
`/review-change` hoje recusa: "git status --porcelain -- /tmp/it3/runs/compaction-resume/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". A revisão roda depois que a pessoa fizer commit desta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`). Nada aqui faz commit.

Invocação pronta para colar, depois do commit:
```
/review-change project /tmp/it3/runs/compaction-resume/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```

---

# Handoff (verbatim, as rendered)

```
lending · task 1/1 delivered · phase review
```

1. A multa por atraso está escrita e testada; a revisão só roda depois do seu commit.
   - **Recomendado** `commit`: Fazer commit da entrega (fonte, testes, registros, rastreio) e então revisar com a linha abaixo. A revisão recusa hoje: a pasta da entrega tem mudanças sem commit. Mudaria se você preferir descartar ou refazer a entrega.
   - `revisar`: Revisar já: excluída, recusa enquanto houver mudanças sem commit.
   - `reconciliar`: Reconciliar: nada a fazer, nenhum vínculo ficou desatualizado.
   - Se nenhuma for tomada: A entrega fica sem commit e sem revisão.

   ```
   /review-change project /tmp/it3/runs/compaction-resume/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
   ```

Relatório completo: /tmp/it3/runs/compaction-resume/p/.git/siegard/handoff/20261107T184014Z-implement-task.md
