# /implement-task — task/fees/compute-late-fee (lending, alvo `app`)

## Nós escritos
- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md`
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md`
- Primeira entrega (não é re-entrega): não havia registro no caminho da tarefa.

## Caminhos criados, modificados ou removidos (o conjunto de arquivos para `/review-change`)
Relativos à raiz de fonte do alvo `app` (`app/`):
- `lending/fees.py` — criado (registro de implementação, `files`)
- `tests/test_fees.py` — criado (registro de prova, `tests`)

`deliver.py --unrecorded` confirmou: "every path this tree changed under /tmp/itbench/runs/compaction-resume-cand2/p/app is named by the 2 record(s) given".

Fora do alvo, também pendentes no repositório: `delivery/lending/` (registros, `delivery.json`, execuções capturadas) e `siegard-trace.json`.

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true`.

## Inferências e desvios
- Inferência (implementação): "a loan not yet returned is refused with a ValueError rather than answered a fee." — de: "the rule states the fee of a loan returned after its due date and states nothing of a loan still out".
- Desvios: nenhum, em nenhum dos dois registros.

## Nós implementados sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é reivindicado por `demonstrates` em `tests/test_fees.py::test_a_loan_returned_days_after_its_due_date_carries_100_cents_per_calendar_day`. A reivindicação é só uma oferta: quem a certifica é a revisão.

## O que a prova deixou sem provar, os casos de borda descartados e as discordâncias
- untested: "The implementation refuses a loan with no return date by raising ValueError; that is an inference the implementation recorded, no node decides the fee of a loan still out, and it is not pinned by a test."
- not_applicable:
  - empréstimo sem data de devolução — nenhum critério nem nó afirma a multa de um empréstimo ainda em aberto; a recusa é inferência, listada em untested;
  - duas computações simultâneas sobre um empréstimo — função pura sobre um empréstimo imutável; nenhuma obrigação afirma comportamento concorrente;
  - dependência que falha ou responde devagar — a computação não lê dependência alguma;
  - duplicata onde se afirma unicidade, ou coleção vazia — as obrigações recebem um empréstimo e respondem um valor.
- contested: nenhum.

## O que a implementação adiou e o que precisa continuar funcionando
Nada adiado. O módulo existente `lending/loans.py` não foi alterado; `tests/test_loans.py` continua passando na suíte.

## Rastreio
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 vínculo escrito em `siegard-trace.json`).
- Nenhum vínculo recusado. Nenhum recibo de vínculos desatualizados foi impresso, portanto não há invocação de `/reconcile` a entregar.

## Passos executados inline
Esta sessão não pode criar subagentes. Os dois passos delegados rodaram inline, aplicando o arquivo de cada agente:
- passo 3 (implementar), com `agents/task-implementer.md` — antes da compactação;
- passo 5 (provar), com `agents/test-author.md` — depois da compactação. O retorno da prova está em `/tmp/itbench/runs/compaction-resume-cand2/out/proof-return.yaml` e foi gravado por `--from-text`.
Os testes, portanto, foram escritos no mesmo contexto de sessão que escreveu o código (em momentos separados por uma compactação). A separação entre os dois produtores, que o arranjo existe para garantir, não ocorreu; a revisão é quem a substitui.

## Recomendação
Esta invocação terminou; não parou numa barreira. Recomendado (derivado): commitar a entrega e então rodar `/review-change`. Critério: uma porta que o próprio ponto de entrada recusa não é recomendada. Fato decisivo: `/review-change` recusa agora — "git status --porcelain -- /tmp/itbench/runs/compaction-resume-cand2/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". `/reconcile` está excluída: o vínculo não imprimiu recibo de vínculos desatualizados, então não há conjunto de arquivos a reconciliar. Mudaria se: a raiz de entrega `delivery/lending` estivesse limpa no git (a revisão passa a aceitar e é a porta) ou o vínculo tivesse impresso um recibo e nenhuma revisão fosse seguir.

## Saída final do validador (verbatim)
```
derived /tmp/itbench/runs/compaction-resume-cand2/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- `standard.yaml` (relativo à raiz do alvo), resolvido do arquivo do projeto `siegard.json`; pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, o mesmo nos dois registros.
- Desvios declarados contra ele: nenhum.
- A tarefa não declara `produces`; `deliver.py --standard ... --against` passou limpo, então a árvore já mantém o que o registro pressupõe.
- Nenhum registro desta raiz fixa outro padrão, nenhum padrão, ou versão anterior.

## Execuções capturadas
- `run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`).
- `run/fees-compute-late-fee-suite` — passed (build: `python3 -m compileall -q lending`; test: `python3 -m pytest -q tests`).
- Nenhuma execução vermelha.
- Passo que não rodou: setup — o registro não declara comando com papel `install`.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos de novo sobre a mudança inteira, não sobre uma tarefa, e julga: se os testes provam os critérios, se o código afirma só o que a especificação contém, se segue o mesmo padrão (incluindo PY-01, decidido por leitura) e por que algo falhou. Uma suíte verde aqui é verde sobre uma tarefa.

## Handoff
Antes: commitar o que esta entrega deixou pendente (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`) — a revisão recusa enquanto `delivery/lending` não estiver limpo.

```
/review-change /tmp/itbench/runs/compaction-resume-cand2/p app lending task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard standard.yaml
```
Projeto: `/tmp/itbench/runs/compaction-resume-cand2/p`; alvo: `app`; iniciativa: `lending`; tarefa: `task/fees/compute-late-fee`; arquivos: `lending/fees.py`, `tests/test_fees.py`; padrão: `standard.yaml` (do `siegard.json`). Nome da revisão: nenhum dado, então será `lending`.
