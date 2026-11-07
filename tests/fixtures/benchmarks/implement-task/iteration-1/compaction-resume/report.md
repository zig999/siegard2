# /implement-task — task/fees/compute-late-fee (lending, target app)

## Nós escritos
- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md` (pin sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b)
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md` (pin sha256:daa61db7ddcd1c531e6f1a147cdd74952bc6082616a29a4ed992d3f0433486de)
- Primeira entrega, não é re-delivery (`--outstanding` não encontrou record no caminho da task).

## Caminhos que a entrega criou (relativos ao target `app`; `deliver.py --unrecorded` exit 0)
- `lending/fees.py` (implementation `files`)
- `tests/test_fees.py` (proof `tests`)

## Criteria recorded unmet
- Nenhum. Os dois criteria estão `met: true` no implementation record.

## Inferences e departures
- Inference: "a loan not yet returned is refused with a ValueError rather than answered a fee." — from: "the rule states the fee of a loan returned after its due date and states nothing of a loan still out".
- Departures (`divergences`): nenhuma, em nenhum dos dois records.

## Nós implementados sem teste que os demonstre
- `rules/lending/late-fee-per-overdue-day` — nenhum teste carrega `demonstrates`. O `untested` da proof diz: "rules/lending/late-fee-per-overdue-day — its fact quantifies over every loan returned after its due date, an unbounded set of date pairs no finite test enumerates; the tests above exercise one representative per class and the boundary, which is part of the fact and is never offered as the whole of it."

## O que a proof deixou sem prova, edge cases descartados, disagreements
- untested: o nó acima; e "the inference that a loan not yet returned is refused with a ValueError rather than answered a fee — a behavior the implementation chose that no node decides, recorded as unproven and never pinned by a test."
- not_applicable: loan ausente (nenhum criterion nem nó decide); devolução datada antes do empréstimo (nenhuma obrigação alcança); dois cálculos simultâneos sobre um loan (leitura de valor imutável, nenhum nó fala de concorrência); exibição em BRL em vez de centavos (criteria falam em centavos, nenhum nó fala de exibição).
- contested: nenhum.
- Testes escritos (4, em `tests/test_fees.py`): devolução antes do vencimento → 0; no dia do vencimento → 0 (fronteira); um dia depois → 100 (fronteira); dez dias corridos atravessando o fim do mês → 1000.

## O que a implementação adiou / o que deve continuar funcionando
- Nada adiado; o record não carrega campo de adiamento. `tests/test_loans.py` (pré-existente) continua passando na suíte.

## Trace
- Bound: `rules/lending/late-fee-per-overdue-day` → 1 arquivo (`lending/fees.py`), em `siegard-trace.json`.
- Nenhuma binding recusada. Nenhum stale-bindings receipt foi impresso — portanto nenhuma invocação de `/reconcile` é entregue por este relatório.

## Passos executados inline
- Passo 3 (Implement) e passo 5 (Prove) rodaram inline: esta sessão não pode gerar subagents. Cada um aplicou o arquivo do agente (`agents/task-implementer.md`, `agents/test-author.md`) no lugar. Com isso, código e testes foram escritos no mesmo contexto — a separação que os dois agentes existem para dar não houve, e a review deve ler os testes sabendo disso.

## Recomendação
- Derivada: commitar esta entrega antes da review. Critério: uma porta cujo entry point recusa as entradas como a árvore está é `precondition unmet`. Fato decisivo: o check de `/review-change` respondeu `refuses` — "git status --porcelain -- /tmp/itbench/runs/compaction-resume-cand1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". Fato que reverteria: `git status --porcelain -- delivery/lending` vazio (entrega já commitada), quando a própria `/review-change` é a recomendada.

## Saída final do validador (verbatim)
```
derived /tmp/itbench/runs/compaction-resume-cand1/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard
- `app/standard.yaml`, resolvido do `siegard.json` (`standard`), registrado como `at: standard.yaml`, pin sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6, nos dois records.
- Departures declaradas contra ele: nenhuma. A task não declara `produces`; `deliver.py --standard --against` passou limpo, então o que o registry pressupõe a árvore já mantinha.
- Nenhum record deste root fixa outro standard, nenhum standard ou versão anterior.

## Runs capturados
- `run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`).
- `run/fees-compute-late-fee-suite` — passed (build + test: `python3 -m pytest -q tests`).
- Nenhum run vermelho. Setup não rodou: o registry não declara passo com role `install`.

## Dependências instaladas
- Nenhuma.

## O que `/review-change` ainda faz
- Roda os mesmos passos de novo sobre a mudança inteira, e julga: se os testes provam os criteria, se o código afirma só o que a specification sustenta, se segue o mesmo standard, e por que algo falhou. Uma suíte verde aqui é verde sobre uma task só.

## Handoff
A review só roda depois que você commitar esta entrega (a `/review-change` recusa enquanto `delivery/lending` estiver pendente). Depois do commit:

```
/review-change /tmp/itbench/runs/compaction-resume-cand1/p app lending task/fees/compute-late-fee files: lending/fees.py tests/test_fees.py standard: app/standard.yaml review-name: <nome-da-review>
```

---

# Handoff (verbatim, `handoff.py --render`)

```
lending · task 1/1 delivered · phase review
```

1. Multa por atraso entregue, suíte verde; falta o commit para a revisão rodar.
   - **Recomendado** `commit`: Commit desta entrega, depois a revisão. A revisão recusa enquanto a pasta de entrega tem mudanças sem commit. Mudaria se a pasta de entrega já estiver commitada.
   - `revisar`: Revisar agora: excluída, a pasta de entrega tem mudanças sem commit.
   - `reconciliar`: Reconciliar: nada a fazer, nenhum vínculo ficou desatualizado.
   - Se nenhuma for tomada: A entrega fica no disco sem commit e sem revisão.

   ```
   /review-change /tmp/itbench/runs/compaction-resume-cand1/p app lending task/fees/compute-late-fee files: lending/fees.py tests/test_fees.py standard: app/standard.yaml review-name: <nome-da-review>
   ```

Relatório completo: /tmp/itbench/runs/compaction-resume-cand1/p/.git/siegard/handoff/20261107T143145Z-implement-task.md
