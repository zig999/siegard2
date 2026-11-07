# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos
- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md`
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md` (pin sha256:9b116e21311f6e8883cc746494783d86ff48277c7b7d1dfda018379dc67a895a)
- Primeira entrega: não é uma re-entrega (nenhum registro existia no caminho da tarefa).

## Caminhos criados ou modificados (relativos à raiz de fonte do alvo `app`)
- `lending/fees.py` — criado; responde a multa por atraso de um empréstimo devolvido, 100 centavos por dia corrido após o vencimento, 0 quando devolvido no prazo.
- `tests/test_fees.py` — criado; quatro testes da multa.
`deliver.py --unrecorded` confirmou: todo caminho alterado sob `app` está nomeado pelos 2 registros.

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true` no registro de implementação.

## Inferências e divergências
- Inferência (implementação): um empréstimo ainda não devolvido é recusado com `ValueError` em vez de receber uma multa — a regra fala só de empréstimos devolvidos após o vencimento e nada diz de um empréstimo ainda em aberto.
- Divergências do padrão: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre
- `rules/lending/late-fee-per-overdue-day` — nenhum teste carrega `demonstrates`. O `untested` da prova diz: o fato quantifica sobre toda contagem de dias corridos de atraso, um conjunto que nenhum teste finito enumera; os testes seguram a fronteira de um dia e um representativo de vários dias como critérios da tarefa, nunca como o fato inteiro do nó.

## O que a prova deixou sem prova, casos de borda descartados e contestações
- Sem prova: o nó acima; a inferência do `ValueError` para empréstimo não devolvido (nenhum nó decide o que um empréstimo em aberto responde, então a escolha fica registrada como não provada e não é fixada por teste).
- Descartados (`not_applicable`): entrada ausente ou vazia (a operação recebe um empréstimo e nenhum critério/nó diz o que um ausente responde); coleção vazia ou duplicata (lê um empréstimo, não alega unicidade); dependência que falha ou demora (não lê dependência); duas operações simultâneas sobre o mesmo empréstimo (lê um empréstimo imutável e não escreve nada; nenhum nó declara comportamento concorrente).
- Contestações: nenhuma.

## O que a implementação adiou e o que deve continuar funcionando
Nada adiado. O que já existia (`lending/loans.py`, `tests/test_loans.py`) não foi alterado; a suíte rodou os 5 testes, inclusive o existente, e passou.

## Rastreabilidade
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 vínculo escrito em `siegard-trace.json`).
- Nenhum vínculo recusado. Nenhum recibo de vínculos obsoletos foi impresso, então nenhuma invocação de `/reconcile` é devida.

## Passos executados em linha
Os passos 3 (implementar) e 5 (provar) rodaram em linha, nesta sessão, porque ela não pode criar subagentes: a disciplina de `agents/task-implementer.md` e `agents/test-author.md` foi aplicada no próprio contexto. Consequência: fonte e testes foram escritos no mesmo contexto — exatamente a separação que os dois produtores existem para garantir não ocorreu, e a revisão deve ler os testes sabendo disso. A prova carrega essa nota em `## Notes`.

## Saída final do validador (verbatim)
```
derived /tmp/it3/runs2/compaction-resume-2/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido do arquivo do projeto (`siegard.json` → `app/standard.yaml`); nos registros: `at: standard.yaml`, `pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Divergências divulgadas contra ele: nenhuma.
- Pressupõe: nada além do que a árvore já contém (a tarefa não declara `produces`).
- `--outstanding` não imprimiu linhas sobre registros sem padrão ou com outro padrão.

## Execuções capturadas
- `run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`).
- `run/fees-compute-late-fee-suite` — passed (build + `python3 -m pytest -q tests`: 5 passed).
- Nenhuma execução falhou.
- Não rodou: setup — o registro não declara comando de papel `install`.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se a fonte afirma só o que a especificação contém, se segue o padrão e por que algo falhou. Uma suíte verde aqui cobre uma tarefa.

## Encaminhamento
`/review-change` hoje recusa: «git status --porcelain -- /tmp/it3/runs2/compaction-resume-2/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make». A entrega precisa ser commitada por você antes. Recomendado (derivado): commitar `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/` e `siegard-trace.json`, e então rodar:

```
/review-change /tmp/it3/runs2/compaction-resume-2/p target app slug lending task task/fees/compute-late-fee files lending/fees.py tests/test_fees.py
```

O padrão vem do arquivo do projeto (`app/standard.yaml`), sem lacuna a preencher. `/reconcile` não é devido: nenhum recibo de vínculos obsoletos foi impresso.
Mudaria se: a raiz de entrega `delivery/lending` ficasse limpa sem commit (por exemplo, se a entrega fosse descartada) — aí a revisão aceitaria ou não teria o que revisar.
