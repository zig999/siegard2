# /implement-task — task/fees/compute-late-fee (lending, alvo `app`)

## Registros escritos
- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md` (run `run/fees-compute-late-fee-build`).
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md`, pin `sha256:6b7d1e8f19719750c74277b7198229962e4d8065608e07ab0008d4b09bd2bfe4` (run `run/fees-compute-late-fee-suite`).
- Primeira entrega, não uma re-entrega: não havia registro no caminho da tarefa.

## Arquivos que a entrega criou (relativos a `app/`; `deliver.py --unrecorded` exit 0)
- `lending/fees.py` — calcula a multa por atraso de um empréstimo devolvido: 100 centavos por dia corrido após o vencimento, 0 quando devolvido no prazo.
- `tests/test_fees.py` — os quatro testes da prova.

Fora do alvo: `delivery/lending/` (registros, runs, `delivery.json`) e `siegard-trace.json` na raiz do projeto.

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão com `met: true`.

## Inferências e divergências registradas
- Inferência (implementação): um empréstimo ainda não devolvido é recusado com `ValueError` em vez de receber uma multa — a regra fala apenas do empréstimo devolvido após o vencimento.
- Divergências: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `test_a_loan_returned_days_after_its_due_date_carries_100_cents_per_calendar_day`.

## O que a prova deixou sem prova, casos descartados, discordâncias
- `untested`: a recusa de um empréstimo não devolvido com `ValueError` — inferência sobre comportamento, que nenhum nó decide e nenhum teste fixa.
- `not_applicable`: entrada ausente ou vazia (o `Loan` exige as datas); coleção vazia ou duplicata (a função opera sobre um empréstimo); dependência que falha ou demora (nenhuma é lida); duas operações simultâneas (função pura sobre empréstimo imutável).
- `contested`: nenhuma.

## Adiado e o que deve continuar funcionando
A implementação não registrou nada adiado. `tests/test_loans.py`, existente, segue passando na suite.

## Rastreamento
- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (`siegard-trace.json`).
- Nenhuma vinculação recusada; nenhum recibo de vinculações desatualizadas foi impresso, então nenhuma invocação de `/reconcile` é devida por esta entrega.

## Passos executados em linha
Esta sessão não pode criar subagentes. Os passos 3 (implementar, disciplina de `agents/task-implementer.md`) e 5 (provar, disciplina de `agents/test-author.md`) rodaram em linha, na mesma sessão. Por isso o código e os testes foram escritos no mesmo contexto — exatamente o que os dois produtores separados existem para evitar; a revisão deve ler os testes com isso em mente. A prova foi gravada com `--from-text` a partir do mapeamento composto em linha.

## Saída final do validador
```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido do arquivo do projeto (`siegard.json` → `app/standard.yaml`); `standard.at: standard.yaml`, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6` nos dois registros.
- Regras: PY-01 (dinheiro em centavos inteiros — `CENTS_PER_OVERDUE_DAY = 100`, sem ponto flutuante), PY-02 (compila — decidida pelo passo `build`).
- Divergências declaradas: nenhuma.
- Pressupostos: a tarefa não declara `produces`; `deliver.py --standard` passou limpo antes de qualquer escrita.
- `--outstanding` não imprimiu registros sem padrão, com outro padrão ou com versão anterior dele.

## Runs capturados
- `delivery/lending/run/fees-compute-late-fee-build` — passed (`build`).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (`build`, `test`: `python3 -m pytest -q tests`).
- Setup não rodou: o registro não declara nenhum passo com papel `install`.
- Nenhum run vermelho.

## Dependências instaladas
Nenhuma.

## O que a `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, e julga se os testes provam os critérios, se o código declara apenas o que a especificação contém, se segue o padrão e por que algo falhou. A suite verde aqui cobre uma tarefa.

## Próximo passo
A `/review-change` recusa enquanto `delivery/lending` tiver alterações não commitadas (`git status --porcelain -- delivery/lending` não está vazio). Faça o commit desta entrega primeiro — `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json` — e então a invocação `/review-change` pronta para colar:

```
/review-change /tmp/it3/runs/compaction-resume--before-2/p --target app --slug lending --tasks task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard standard.yaml --name <nome-da-revisão>
```
