# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos
- `delivery/lending/implementation/fees/compute-late-fee.md` (implementação)
- `delivery/lending/proof/fees/compute-late-fee.md` (prova)
- Primeira entrega, não é re-entrega: não havia registro no caminho da tarefa.

Entradas decididas e divulgadas: nenhuma — projeto, alvo `app`, slug `lending` e tarefa foram nomeados na invocação.

## Caminhos que a entrega criou (relativos à raiz de fonte do alvo `app`)
- `lending/fees.py` — implementação `files`: responde a multa por atraso de um empréstimo devolvido como 100 centavos por dia corrido após o vencimento, e 0 quando devolvido no prazo
- `tests/test_fees.py` — prova `tests`

`deliver.py --unrecorded` manteve a árvore a esse conjunto: "Every path this tree changed under app is named by the 2 record(s) given".

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true`.

## Inferências e desvios registrados
- Inferência: um empréstimo ainda não devolvido é recusado com `ValueError` em vez de receber uma multa. Origem: a regra declara a multa de um empréstimo devolvido após o vencimento e nada diz de um empréstimo ainda em aberto.
- Desvios contra o padrão: nenhum registrado.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `test_each_further_calendar_day_after_the_due_date_adds_100_cents`.

## O que a prova deixou sem provar, casos dispensados, discordâncias
Nada registrado como não provado; nenhum caso de borda dispensado; nenhuma discordância.

## O que a implementação adiou / o que deve continuar funcionando
Nada registrado.

## Vínculo do rastro
- `trace.py --bind-record`: "bound rules/lending/late-fee-per-overdue-day to 1 file(s)"; "1 binding(s) written at /tmp/it3/runs/compaction-resume-late--before-2/p/siegard-trace.json, read from compute-late-fee.md".
- Nenhum vínculo recusado. Nenhum recibo de vínculos obsoletos foi impresso, portanto não há porta `/reconcile` a entregar por esta entrega.
- `siegard-trace.json` na raiz do projeto é a única escrita fora das três raízes desta entrega.

## Passos executados em linha
Esta sessão não pode criar subagentes. Implementar (passo 3, disciplina de `agents/task-implementer.md`) e Provar (passo 5, disciplina de `agents/test-author.md`) rodaram em linha, cada um aplicando o arquivo do seu agente. Código e testes foram escritos no mesmo contexto da sessão — a separação que os subagentes dariam não existiu aqui, e a revisão é o que a recupera.

## Saída final do validador (verbatim)
```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido do arquivo de projeto (`siegard.json` → `standard: app/standard.yaml`), registrado como `standard.yaml` relativo à raiz de fonte do alvo.
- Pin: `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6` (nos dois registros).
- Desvios divulgados: nenhum.
- Pressupostos: a tarefa não declara `produces`; `deliver.py --standard` passou limpo contra a árvore.
- `--outstanding` não imprimiu linhas de registros sem padrão, com outro padrão ou com versão anterior.

## Execuções capturadas
- `delivery/lending/run/fees-compute-late-fee-build` — passou (build: `python3 -m compileall -q lending`, 60 s)
- `delivery/lending/run/fees-compute-late-fee-suite` — passou na primeira tentativa (build, depois test: `python3 -m pytest -q tests`, 120 s)
- Nenhuma suíte vermelha, portanto nenhum diagnóstico.
- Passo do registro que não rodou: setup — o registro não declara comando de papel `install`.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se a fonte declara só o que a especificação contém, se segue o padrão (PY-01 por leitura, PY-02 por ferramenta) e por que algo falhou. A suíte verde aqui cobre uma tarefa.

## Próximo passo
`/review-change` hoje recusa: "git status --porcelain -- /tmp/it3/runs/compaction-resume-late--before-2/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". A entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`) precisa ser commitada pela pessoa antes. Commitar é decisão sua; esta invocação não muda o estado do git.

Invocação pronta para colar, depois do commit:
```
/review-change /tmp/it3/runs/compaction-resume-late--before-2/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```
