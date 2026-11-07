# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Nós escritos
- `implementation/fees/compute-late-fee` e `proof/fees/compute-late-fee`, em `delivery/lending/`. Primeira entrega, não é re-entrega.

## Arquivos criados ou alterados (relativos à raiz do alvo `app/`)
- `lending/fees.py` — criado (registro de implementação, `files`)
- `tests/test_fees.py` — criado (prova, `tests`)
`deliver.py --unrecorded` confirmou que todo caminho alterado sob `app/` é nomeado pelos 2 registros.

## Critérios registrados como não atendidos
- Nenhum. Os dois critérios estão `met: true`.

## Inferências e desvios
- Inferência: um empréstimo ainda não devolvido é recusado com `ValueError` em vez de receber uma multa — de: a regra fala da multa de um empréstimo devolvido após o vencimento e nada diz de um empréstimo ainda em aberto.
- Desvios: nenhum, em nenhum dos dois registros.

## Nós sem teste que os demonstre
- `rules/lending/late-fee-per-overdue-day` — nenhum teste carrega `demonstrates`. O `untested` da prova diz: o nó afirma a multa para todo empréstimo devolvido após o vencimento, uma totalidade sobre toda contagem de dias de atraso que nenhum conjunto finito de entradas enumera; os testes de critério a amostram na fronteira e em uma classe, e nenhum teste reivindica o nó inteiro.

## O que a prova deixou sem provar, descartou ou contestou
- Sem provar: o nó acima; e a inferência do `ValueError` para empréstimo não devolvido, comportamento que nenhum nó decide, deixado sem fixar para que a especificação lhe dê um lugar.
- Casos de borda descartados: empréstimo devolvido antes de ser tomado (nenhum critério ou nó o decide); duas computações simultâneas sobre o mesmo empréstimo (lê um empréstimo imutável e não escreve nada); dependência que falha ou demora (a computação não chama nada fora do empréstimo).
- Contestações: nenhuma.

## O que a implementação adiou e o que deve continuar funcionando
- Nada registrado.

## Rastreio
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 vínculo, em `siegard-trace.json`). Nenhum vínculo recusado.
- Nenhum recibo de vínculos obsoletos foi impresso; portanto não há invocação de `/reconcile` a entregar.

## Passos executados inline
- Implementar (passo 3) e provar (passo 5) rodaram inline, aplicando `agents/task-implementer.md` e `agents/test-author.md` no lugar: esta sessão não pode criar subagentes. A separação entre quem escreveu o código e quem escreveu os testes, portanto, não existiu nesta entrega.

## Recomendação
- Esta invocação não parou; entrega a revisão. `/review-change` recusa como a árvore está: `git status --porcelain -- .../delivery/lending` não está vazio. O fato que decide: a raiz de entrega tem alterações não commitadas. Recomendado (derivado, `precondition unmet`): você commitar esta entrega, depois rodar a revisão. Mudaria se: a raiz de entrega já estivesse commitada — então a revisão aceita direto.

## Saída final do validador
```
derived /tmp/itbench2/runs/compaction-resume-prior1/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- `app/standard.yaml` (de `siegard.json`), registrado como `standard.yaml` relativo à raiz do alvo, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, nos dois registros. Nenhum desvio declarado. A tarefa não declara `produces`; a árvore foi mantida ao que o registro pressupõe (`deliver.py --standard ... --against` limpo). Nenhum registro deste root fixa outro padrão ou nenhum.

## Execuções capturadas
- `delivery/lending/run/fees-compute-late-fee-build` — passed (build).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (build, test).
- Nenhuma execução vermelha.
- Setup não rodou: o registro não declara passo de `install`.

## Dependências instaladas
- Nenhuma.

## O que `/review-change` ainda faz
- Roda os mesmos passos de novo sobre a mudança inteira, e julga: se os testes provam os critérios, se o código diz só o que a especificação contém, se segue o mesmo padrão, e por que algo falhou. Uma suíte verde aqui é verde sobre uma tarefa só.

## Handoff — `/review-change` invocation ready to paste (depois do commit)
```
/review-change task/fees/compute-late-fee project=/tmp/itbench2/runs/compaction-resume-prior1/p target=app slug=lending files=lending/fees.py,tests/test_fees.py standard=app/standard.yaml review-name=<nome>
```

---

# Handoff entregue à pessoa (saída de handoff.py --render, verbatim)

```
lending · task 1/1 delivered · phase review
```

1. Multa por atraso escrita e testada, build e testes verdes; falta você commitar para revisar.
   - **Recomendado** `commit`: Commitar a entrega e depois rodar a revisão abaixo. A revisão recusa enquanto a pasta da entrega tiver mudanças sem commit. Mudaria se a pasta da entrega já estiver commitada.
   - `revisar`: Revisar agora: excluída, recusa pelas mudanças sem commit.
   - `reconciliar`: Reconciliar: nada a fazer, nenhum vínculo ficou desatualizado.
   - Se nenhuma for tomada: A entrega fica pendente, sem commit e sem revisão.

   ```
   /review-change task/fees/compute-late-fee project=/tmp/itbench2/runs/compaction-resume-prior1/p target=app slug=lending files=lending/fees.py,tests/test_fees.py standard=app/standard.yaml review-name=<nome>
   ```

Relatório completo: /tmp/itbench2/runs/compaction-resume-prior1/p/.git/siegard/handoff/20261107T144711Z-implement-task.md
