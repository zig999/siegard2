# /deliver-scope lending — epic/fees — relatório

O run começou com `HEAD` em `a02c5fc` no `main` e fez seus commits ali mesmo. Se você preferia esses commits num branch próprio, criar o branch a partir de `a02c5fc` é com você.

**Resultado: o escopo `epic/fees` foi entregue de ponta a ponta. A única tarefa que faltava foi implementada, provada, revisada e medida, com um commit por passo. O run não parou por nenhum stop.** Ele foi retomado depois de uma compactação, e a autorização foi relida de `ask.py --read` (telemetry/ask-20261107T180826Z.md, sha256 38f9a15bc91f4f7b):

> Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa que falta, revisa e comita cada passo, sem parar no meio pra me perguntar.

- Projeto: `/tmp/dsb/runs2/compaction-resume--before-2/p`; target `app`; slug `lending` (plano vivo, retomado); reach `epic/fees`.
- Roots (`project.py`): specification_root `spec`, work_root `work`, delivery_root `delivery`, telemetry_root `telemetry`, standard `app/standard.yaml`.
- Gate: `spec.py spec` passou sobre uma root com commit, e a árvore estava limpa.

## Passos e commits

| Passo | O que rodou | Commit |
|---|---|---|
| plan | pulado: o ask nomeia `epic/fees`, que o plano vivo `lending` já contém | nenhum |
| deliver | `/implement-task` sobre `task/fees/compute-late-fee`: implementação e prova escritas, suíte verde | `2dbcfff deliver-scope lending: deliver task/fees/compute-late-fee` |
| review | `/review-change` com o nome `lending` (livre) sobre `lending/fees.py`, `tests/test_fees.py` | `79852dc deliver-scope lending: review` |
| prove | pulado: a review não recusou nenhuma certificação, então não sobrou `remainder: testable` | nenhum |
| measure | `telemetry.py --since 2026-11-07T12:00:00Z` gravou `telemetry/20261107T180852Z.json` | `1209cd6 deliver-scope lending: measure` |

O log fica em `delivery/lending/orchestration.md`. O commit de measure leva junto as linhas de review, prove e measure do log. A linha de measure identifica o próprio commit pelo assunto, porque um commit não consegue conter o próprio hash.

Última execução de `deliver.py --outstanding delivery/lending work/lending app spec --scope epic/fees`, verbatim:

```
scope: epic/fees — 1 task(s)
every task in the scope has a record, and every record its proof
standard.yaml (target app): pinned by 3 record(s); an invocation naming no standard now writes source these rules will still be read against
```

## Review `lending`: 2 achados (conformance `unstated` 2), nenhuma certificação preparada

Cobertura: 1 critério `covered`, 1 `partial`, 0 sem cobertura.

- **partial**: "A loan returned after its due date carries 100 cents for each calendar day between its due date and its return." O teste aceita qualquer taxa de `(days_late - 1) * 100` a `days_late * 100`. Por isso, uma contagem de dias errada por um, para mais ou para menos, ainda passa, e nenhum teste fixa a taxa de um empréstimo devolvido um dia depois do vencimento. O critério também não diz se o dia do vencimento ou o dia da devolução entra na contagem.

Achados, verbatim do registro `delivery/lending/review/lending.md`:

1. conformance / `unstated`, `lending/fees.py`, a contagem de dias em `late_fee_cents`, linha 7
   - evidência: `overdue_days = (loan.returned_on - loan.due_on).days`
   - custo: o "each calendar day between its due date and its return" do nó não diz se o dia do vencimento ou o da devolução conta. O código decide que a contagem é a diferença entre as datas, então um empréstimo devolvido com um dia de atraso paga BRL 1.00, e essa decisão só existe nessa linha.
   - correção: `rules/lending/late-fee-per-overdue-day` passa a dizer como os dias de calendário entre o vencimento e a devolução são contados (qual ponta conta, se alguma conta), e o código é lido contra isso.
2. conformance / `unstated`, `lending/fees.py`, o guard em `late_fee_cents`, linhas 8-9
   - evidência: `if overdue_days <= 0: return 0`
   - custo: o nó só define a taxa de um empréstimo devolvido depois do vencimento. Que um empréstimo devolvido no vencimento ou antes não paga taxa só aparece aqui e no critério da tarefa.
   - correção: um nó, provavelmente `rules/lending/late-fee-per-overdue-day`, passa a dizer que um empréstimo devolvido no vencimento ou antes não paga taxa de atraso.

Notas da review: nenhum subagent deste plugin estava registrado, então os passes rodaram inline. Os retornos da conformance estão em `siegard-reconcile/lending.returns/`. O PY-01 foi lido e nada se afastou dele. A conformance não tratou o fato de a taxa ser um int de centavos enquanto `domain/lending/loan` declara `late_fee` como valor decimal em BRL. Nenhuma certificação foi preparada porque nenhum registro de prova traz um claim `demonstrates`.

Nenhum achado foi tratado neste run. Corrigir qualquer um deles é um novo pedido.

## Medição

`telemetry/20261107T180852Z.json`: 3 runs capturados, 3 commits, 15 decisões adicionadas, 1 review (1 covered, 1 partial). Os transcripts não estavam disponíveis: `/home/siegfriedneto/.claude/projects/-tmp-dsb-runs2-compaction-resume--before-2-p` não é um diretório. Por isso o custo em tokens e os spawns ficaram sem medição, e isso não para o run.

## Próximo passo: é seu

Não há recomendação. O valor de um achado é uma decisão sua, e não existe goal com política de achados que a decida antes.

- **Especificar a contagem de dias e o caso sem atraso.** Faz sentido se o "between" do nó deve dizer qual ponta conta. Para isso, rode `/analyse` com o seu texto sobre a regra `rules/lending/late-fee-per-overdue-day`. Depois, uma nova entrega pode apertar o teste parcial. Este skill nunca invoca `/analyse`, então essa chamada é sua.
- **Aceitar como está.** Faz sentido se a diferença entre as datas (um dia de atraso = BRL 1.00) é a leitura pretendida e o caso de taxa zero pode ficar no critério da tarefa. Nesse caso não há nada a fazer.
