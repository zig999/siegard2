# /deliver-scope lending — epic/fees, relatório completo

Pedido (lido de `ask.py --read`, sha256 38f9a15bc91f4f7b, após a compactação): «Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa que falta, revisa e comita cada passo, sem parar no meio pra me perguntar.»

## 1. Onde o HEAD estava

`HEAD` estava em `07e5d8c` (`seed`) no branch `main` quando a execução começou (passo 1 às 2026-11-07T12:00:00Z). Nenhum branch foi criado; se quiser isolar a execução num branch, cortar um a partir de `07e5d8c` é um ato seu.

## 2. Commits desta execução

- `ebd8ea3` deliver-scope lending: deliver task/fees/compute-late-fee
- `13a0dde` deliver-scope lending: review
- `6de0833` deliver-scope lending: measure

Intervalo: `git log 07e5d8c..6de0833`. Cada commit nomeou seus caminhos; nada foi enviado (push).

## 3. Entradas decididas em vez de informadas

Nenhuma. Alvo `app`, slug `lending` e alcance `epic/fees` foram nomeados no pedido. A execução é uma retomada sobre o plano vivo `lending`, a partir do conjunto entregável como estava. Ordem: a única tarefa entregável, `task/fees/compute-late-fee`.

## 4. Passos e resultados

- 1 Plano: pulado — o pedido nomeia `epic/fees`, que o plano vivo `lending` contém; nada commitado.
- 2 Commit do plano: não houve plano a commitar.
- 3 Entrega: `/implement-task task/fees/compute-late-fee` — implementação e prova escritas, suíte verde; commit `ebd8ea3`.
- 4 Revisão: `/review-change` sob o nome `lending` (livres: `review/lending.md`, `run/lending`, `siegard-reconcile/lending.md`, `siegard-reconcile/lending.returns/`), tarefas `task/fees/compute-late-fee`, arquivos `lending/fees.py` e `tests/test_fees.py`; registro em `delivery/lending/review/lending.md`; commit `13a0dde`.
- 5 Provar o que a revisão deixou testável: não se aplica — nenhuma certificação foi recusada (nenhuma foi encenada).
- 6 Medição: `telemetry.py --probe`, depois a leitura anunciada; commit `6de0833`.

Log: `delivery/lending/orchestration.md`.

Última execução de `deliver.py --outstanding delivery/lending work/lending app spec --scope epic/fees` (exit 0), verbatim:

```
scope: epic/fees — 1 task(s)
every task in the scope has a record, and every record its proof
standard.yaml (target app): pinned by 3 record(s); an invocation naming no standard now writes source these rules will still be read against
```

## 5. Registros que fixam nenhum standard ou outro que o declarado

Nenhum. A última execução imprimiu apenas a linha de que `standard.yaml (target app)` é fixado por 3 registros — nenhuma linha de registro sem standard ou com outro standard, nem com versão anterior dele.

## 6. Achados da revisão, na íntegra

A revisão abre com: cobertura — 1 critério `covered`, 1 `partial`, 0 `uncovered`; `unpaired: []`; 2 achados, ambos de conformidade, `unstated`; nenhuma certificação encenada.

Cobertura parcial:
- Critério «A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.» — `partial`, teste `tests/test_fees.py::test_each_further_calendar_day_after_the_due_date_adds_100_cents`. Por quê (da revisão): o passo de 100 centavos por dia adicional, do 2º ao 40º dia após o vencimento, é exercitado; o valor que uma devolução específica carrega não é, porque o teste aceita qualquer tarifa de (days_late - 1) * 100 a days_late * 100 centavos, de modo que uma contagem de dias errada por um em qualquer direção ainda passa, e nenhum teste fixa a tarifa de um empréstimo devolvido um dia corrido após o vencimento. O próprio critério não diz se a data de vencimento ou o dia da devolução entram na contagem.

Achado 1 — conformance, `unstated`, `lending/fees.py`, a contagem de dias em `late_fee_cents`, linha 7
- evidência: `overdue_days = (loan.returned_on - loan.due_on).days`
- custo: o "each calendar day between its due date and its return" do nó não diz se o vencimento ou o dia da devolução contam; o código decide que a contagem é a diferença das datas, então um empréstimo devolvido um dia atrasado carrega BRL 1,00, e essa decisão vive só nessa linha
- correção: `rules/lending/late-fee-per-overdue-day` declara como os dias corridos entre o vencimento e a devolução são contados (qual extremo, se algum, conta), e o código é lido contra isso

Achado 2 — conformance, `unstated`, `lending/fees.py`, a guarda em `late_fee_cents`, linhas 8-9
- evidência: `if overdue_days <= 0:` / `    return 0`
- custo: o nó declara a tarifa apenas de um empréstimo devolvido após o vencimento; que um empréstimo devolvido no vencimento ou antes não carrega tarifa vive só aqui e no critério da tarefa, então o próximo leitor procura isso na especificação e não encontra
- correção: um nó, mais plausivelmente `rules/lending/late-fee-per-overdue-day`, ganha a declaração de que um empréstimo devolvido no vencimento ou antes não carrega tarifa de atraso

Passes: coverage, conformance e standard rodaram (inline — nenhum subagente do plugin estava registrado, então cada spawn falhou e cada passe rodou sob a disciplina do arquivo do seu agente). O passe `failures` não teve o que ler: «run/lending passed; there was no failure to read». Notas da própria revisão: o passe standard leu PY-01 e nada se afastou dela; a conformidade deixou de lado que a tarifa é um int de centavos enquanto `domain/lending/loan` declara `late_fee` como valor decimal em BRL, representação que PY-01 governa; a revisão não julga desempenho, segurança além dos passos do registro, nem nada fora dos dois arquivos.

Qual rota cada achado merece, ou se merece alguma, é decisão sua; nenhum foi reparado aqui.

## 7. Testes, certificações e restos

Nenhum nó ficou decidido por teste nesta execução (`bindings a test decides: 0`). Nenhuma certificação foi encenada nem recusada: nenhum registro de prova carrega uma alegação `demonstrates`; a entrada `untested` da prova diz que a regra como um todo não é decidida por um teste finito porque o nó não declara se um dia extremo conta. Sem resto `testable` sobre nó de outra tarefa, nada de `trace.py --owed` a repassar.

## 8. Telemetria

Relatório: `telemetry/20261107T180853Z.json` (janela 2026-11-07T12:00:00Z..2026-11-07T18:08:53Z). Os transcripts do harness estavam indisponíveis (`/home/siegfriedneto/.claude/projects/-tmp-dsb-runs2-compaction-resume--shipped-2-p is not a directory`), então agentes, comandos e handoffs não foram contados; a contagem vem do disco: 3 runs capturados, 3 commits, 15 decisões adicionadas, 1 revisão.

## 9. O que encerrou a execução

Nada a encerrou antes do fim: o conjunto entregável de `epic/fees` esvaziou, a revisão foi escrita e a medição commitada. Nenhuma parada, nenhuma porta de parada a repassar.

## 10. O que esta execução nunca fez

Não invocou `/analyse`, não escreveu na raiz da especificação, não reparou nenhum achado, não criou branch, não fez push, não deu passo além da rota.

O intervalo `07e5d8c..6de0833` é a revisão, e é sua.
