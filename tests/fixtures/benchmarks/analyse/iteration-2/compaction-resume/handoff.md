# /analyse — relatório

Projeto: `/tmp/analyse-bench/iteration-2/projects/compaction-resume` · raiz da especificação: `spec` (vazia antes desta invocação) · material: `docs/material.md` (arquivo).

## Nós escritos (todos criados; nenhum alterado ou removido) — campos decididos, como `spec.py --shape --of` imprimiu

```
>   4 decided /  18 declared  domain/lending/loan
>   3 decided /  10 declared  domain/lending/reservation
>   2 decided /  11 declared  domain/lending/copy
>   2 decided /  10 declared  domain/lending/member
>   1 decided /   1 declared  domain/lending/_context
>   1 decided /   3 declared  rules/lending/late-fee-per-overdue-day
>   1 decided /   3 declared  rules/lending/renewal-extends-due-date-fourteen-days
>   1 decided /   5 declared  rules/lending/reserved-copy-blocks-renewal
>   1 decided /   3 declared  rules/lending/reserved-copy-held-three-days
>   1 decided /   5 declared  rules/lending/returned-reserved-copy-notifies-reserver
>   0 decided /   4 declared  domain/lending/book
>   0 decided /   3 declared  rules/lending/loan-due-fourteen-days-after-borrowing
>   0 decided /   3 declared  rules/lending/loan-renewed-at-most-once
>   0 decided /   4 declared  rules/lending/member-holds-at-most-three-loans
>   0 decided /   4 declared  rules/lending/overdue-member-cannot-borrow
>   0 decided /   8 declared  scenarios/lending/overdue-member-refused-new-loan
```

Nenhum nó foi introduzido sem que o material o nomeasse: sócio, livro, exemplar, empréstimo e reserva estão todos no material; a regra da multa responde à pergunta da linha 13.

## Conjunto de impacto lido

Nenhum: a raiz estava vazia, então a etapa de situar foi pulada. Não há `constraints/` nem nó anterior a ler.

## Decisões registradas nesta invocação (17, primeira linha do escritor de cada uma)

- `domain/lending/_context` · `strategic` = `core` — o controle de empréstimos é tudo o que o material pede ao sistema. (`decided: domain/lending/_context.log.md entries[0] — strategic`)
- `domain/lending/copy` · `attributes.code` = `code: string, required` — exemplares do mesmo título são idênticos e empréstimo e reserva precisam nomear exatamente um. (`entries[0]`)
- `domain/lending/copy` · `relationships.reservation.cardinality` = `0..1` — o material sempre nomeia um único sócio reservante e não fala de fila. (`entries[1]`)
- `domain/lending/loan` · `aggregate` = `member` — os dois limites de retirada contam os empréstimos de um sócio. (`entries[0]`)
- `domain/lending/loan` · `attributes.renewed` = `boolean, required` — com no máximo uma renovação, só importa se ela ocorreu. (`entries[1]`)
- `domain/lending/loan` · `attributes.returned_on` = `date, optional` — bloqueio, multa e os 3 dias da reserva contam a partir da devolução. (`entries[2]`)
- `domain/lending/loan` · `attributes.late_fee` = `decimal, optional, valor em BRL` — a multa é devida por um empréstimo atrasado. (`entries[3]`)
- `domain/lending/member` · `attributes.name` = `string, required` — o material identifica o sócio pelo nome (Ana). (`entries[0]`)
- `domain/lending/member` · `relationships.loan.type` = composição — limite de três e bloqueio por atraso decidem a retirada sobre os outros empréstimos do sócio no mesmo instante. (`entries[1]`)
- `domain/lending/reservation` · `aggregate` = `copy` — a reserva bloqueia a renovação e é disparada pela devolução de um exemplar. (`entries[0]`)
- `domain/lending/reservation` · `attributes.pickup_deadline` = `date, optional, definido na devolução` — os 3 dias só começam na devolução. (`entries[1]`)
- `domain/lending/reservation` · `attributes.reserved_on` = `date, required` — a regra de renovação lê se existe reserva naquele momento. (`entries[2]`)
- `rules/lending/late-fee-per-overdue-day` · `statement` = R$ 1,00 por dia corrido entre o vencimento e a devolução, seguindo a sugestão da diretoria — a pergunta da linha 13 perguntava por dia ou fixo; a diretoria recomendou R$ 1,00/dia e a decisão segue a recomendação. (`decided: rules/lending/late-fee-per-overdue-day.log.md entries[0] — statement`)
- `rules/lending/reserved-copy-blocks-renewal` · `consistency` = `eventual` — empréstimo e reserva estão em agregados distintos. (`entries[0]`)
- `rules/lending/returned-reserved-copy-notifies-reserver` · `consistency` = `eventual` — devolução e reserva estão em agregados distintos; um aviso logo após a devolução atende o material. (`entries[0]`)
- `rules/lending/reserved-copy-held-three-days` · `statement` = três dias **corridos** após a devolução — o material diz só "3 dias"; conta como no único outro prazo que qualifica ("dias corridos"). `decided: rules/lending/reserved-copy-held-three-days.log.md entries[0] — statement` (registrada após a compactação: o enunciado já dizia "calendar days" sem entrada no log)
- `rules/lending/renewal-extends-due-date-fourteen-days` · `statement` = o vencimento passa a ser 14 dias corridos depois do que era — o material diz "por mais 14 dias" sem dizer a partir de quando nem que tipo de dia. `decided: rules/lending/renewal-extends-due-date-fourteen-days.log.md entries[0] — statement` (registrada após a compactação, pelo mesmo motivo)

## Leitura de `--shape` — o que fica em pé e por quê

- Classe `element` p90 = máx. 103 palavras (5 nós, abaixo do que uma distribuição precisa): é o `loan`, cujo comprimento está nos campos declarados; a prosa tem duas frases. Fica.
- Frase compartilhada "calendar days after the day its copy was" (8w × 2) entre `loan-due-fourteen-days-after-borrowing` e `reserved-copy-held-three-days`: conta prazos diferentes a partir de eventos diferentes (retirada vs. devolução); a unidade comum agora é decisão registrada, não definição duplicada. Fica; levada à verificação cruzada (sem caso em comum).
- `why` no p90 em `domain/lending/member.log` e `rules/lending/returned-reserved-copy-notifies-reserver.log`: cada um carrega uma alegação rejeitável sobre o domínio (onde fica a fronteira de consistência), não um argumento de composição da especificação. Entradas nunca são editadas (SPEC-001 R9). Ficam.
- Nenhum `statement` com mais de uma frase, nenhum nome sem nó, nenhuma prosa nomeando irmãos, fechamento de leitura 0 em todos.

## Verificação cruzada

Pares abertos: o par da frase compartilhada; os pares que o material juntou na linha 8 (`loan-renewed-at-most-once`, `renewal-extends-due-date-fourteen-days`, `reserved-copy-blocks-renewal`) e na linha 10 (`returned-reserved-copy-notifies-reserver`, `reserved-copy-held-three-days`); e `loan-due-fourteen-days-after-borrowing` × `renewal-extends-due-date-fourteen-days`, `member-holds-at-most-three-loans` × `overdue-member-cannot-borrow`. Nenhum decide um caso de forma diferente; nenhum decide o mesmo caso da mesma forma (o vencimento inicial vale "until the loan is renewed", e a renovação o move). Nada registrado.

Itens de observação (tensões sem caso a decidir):
- `reserved-copy-blocks-renewal` é `eventual`: uma reserva feita instantes antes de uma renovação pode não ser vista e a renovação passar. Decisão registrada; se o negócio exigir bloqueio imediato, a fronteira de agregados muda.
- Nada diz o que acontece quando os 3 dias de retirada passam sem o reservante retirar (reserva expira? passa para outro?). Nenhuma regra contraditória; é um fato que o material não trouxe.
- Nada diz se um exemplar que está na prateleira (não emprestado) pode ser reservado.

## Ledger (`docs/ledger.md`) — saída de `trace.py --ledger`, literal

```
ledger sound: 10 fact line(s) over 1 material file(s) — 8 landed in 13 node(s), 2 left out with a reason, 0 open
  left out, by reason (2 distinct, largest first):
    1 × A screen's button colour, label and list ordering are presentation of the solution, not a fact of the lending domain.
    1 × States the library's purpose in controlling loans, which the lending context's prose explains; it carries no condition, term or case a field holds.
  candidates, all: domain/lending/book domain/lending/copy domain/lending/loan rules/lending/late-fee-per-overdue-day rules/lending/loan-due-fourteen-days-after-borrowing rules/lending/loan-renewed-at-most-once rules/lending/member-holds-at-most-three-loans rules/lending/overdue-member-cannot-borrow rules/lending/renewal-extends-due-date-fourteen-days rules/lending/reserved-copy-blocks-renewal rules/lending/reserved-copy-held-three-days rules/lending/returned-reserved-copy-notifies-reserver scenarios/lending/overdue-member-refused-new-loan
```

Nenhuma linha em aberto. A linha 3 ficou de fora porque o esquema do ledger não admite `_context` como nó; o contexto `domain/lending/_context` explica o propósito.

## O que este incremento pode ter posto o código entregue em violação

Esta etapa nunca lê o alvo, de propósito. As decisões deste incremento podem contradizer código já entregue (no alvo `app`, raiz `.`), e só uma reconciliação descobre isso, se alguém a rodar. Nada a agenda.

## Candidatos para uma reconciliação (nós escritos neste incremento, ainda não vinculados a nada)

domain/lending/_context, domain/lending/book, domain/lending/copy, domain/lending/loan, domain/lending/member, domain/lending/reservation, rules/lending/late-fee-per-overdue-day, rules/lending/loan-due-fourteen-days-after-borrowing, rules/lending/loan-renewed-at-most-once, rules/lending/member-holds-at-most-three-loans, rules/lending/overdue-member-cannot-borrow, rules/lending/renewal-extends-due-date-fourteen-days, rules/lending/reserved-copy-blocks-renewal, rules/lending/reserved-copy-held-three-days, rules/lending/returned-reserved-copy-notifies-reserver, scenarios/lending/overdue-member-refused-new-loan

## Saída final do validador, literal, e o que `--project` escreveu

```
specification sound: 5 element(s), 9 rule(s), 1 scenario(s) across 1 context(s); 17 decision(s) disclosed
projected 5 file(s) into spec/projections: capability-map.mmd, class-diagram-lending.mmd, context-map.mmd, full-text.md, overview.md
```

## Próximo passo

`/plan-work` invocation ready to paste:

```
/plan-work /tmp/analyse-bench/iteration-2/projects/compaction-resume target <alvo> slug <slug-da-iniciativa> — <o escopo, em prosa>
```

`/reconcile`: o material não é survey nem intent, então não há adoção sobre este ledger; uma reconciliação só serve para checar código já entregue contra os nós acima, com os candidatos listados.

A revisão é o `git diff` sobre `spec/` e `docs/ledger.md`; quem commitar a especificação commita o ledger no mesmo commit, pelo caminho. Nada foi commitado.
