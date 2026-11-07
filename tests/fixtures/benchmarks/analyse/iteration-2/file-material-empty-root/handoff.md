# /analyse — relatório

Projeto: `/tmp/analyse-bench/iteration-2/projects/file-material-empty-root`
Raiz da especificação: `spec/` (vazia antes desta invocação; primeira execução)
Material: `docs/material.md` (arquivo; sha256 `bec66729869237ae202e49b51f7c126ed8649a8fb6f4e5de2a8d69fadef13193`)

## Nós escritos (todos criados; nada alterado nem removido)

Campos decididos / declarados, como `spec.py --shape --of` imprimiu:

- `domain/lending/_context` — 1 / 1
- `domain/lending/member` — 1 / 10
- `domain/lending/loan` — 3 / 16
- `domain/lending/title` — 0 / 4
- `domain/lending/copy` — 1 / 7
- `domain/lending/reservation` — 1 / 12
- `rules/lending/member-holds-at-most-three-loans` — 0 / 4
- `rules/lending/overdue-loan-blocks-borrowing` — 0 / 4
- `rules/lending/loan-falls-due-fourteen-days-after-borrowing` — 0 / 3
- `rules/lending/renewal-extends-due-date-by-fourteen-days` — 0 / 3
- `rules/lending/loan-renews-at-most-once` — 0 / 3
- `rules/lending/reserved-copy-blocks-renewal` — 1 / 5
- `rules/lending/returned-reserved-copy-held-for-collection` — 2 / 5
- `rules/lending/overdue-loan-accrues-daily-fine` — 1 / 3
- `scenarios/lending/overdue-member-cannot-borrow` — 0 / 9
- `contracts/lending/reserved-copy-returned` — 1 / 3

## Conjunto de impacto lido

Nenhum: a raiz estava vazia, então o passo 1 (situar) não se aplica.

## Decisões registradas (primeira linha do escritor, por nó e campo)

1. `decided: domain/lending/_context.log.md entries[0] — strategic` — `core`; controlar empréstimos é tudo o que o material pede ao sistema.
2. `decided: domain/lending/member.log.md entries[0] — attributes.name` — `name: string, required`; o único exemplo identifica o sócio pelo nome.
3. `decided: domain/lending/loan.log.md entries[0] — aggregate` — `member`; o limite de três e o bloqueio por atraso valem sobre todos os empréstimos de um sócio, e só valem de imediato se esses empréstimos mudam dentro do agregado do sócio.
4. `decided: domain/lending/loan.log.md entries[1] — attributes.renewed` — `renewed: boolean, required`; com uma única renovação permitida, o único fato a guardar é se ela aconteceu.
5. `decided: domain/lending/loan.log.md entries[2] — attributes.returned_on` — `returned_on: date`, ausente até a devolução; o atraso é julgado por dia.
6. `decided: domain/lending/copy.log.md entries[0] — attributes.code` — `code: string, required`; exemplares de um título são emprestados separadamente e precisam de identificação própria.
7. `decided: domain/lending/reservation.log.md entries[0] — attributes.reserved_on` — `reserved_on: date, required`; a reserva é uma reivindicação datada.
8. `decided: rules/lending/reserved-copy-blocks-renewal.log.md entries[0] — consistency` — `eventual`; empréstimo e reserva estão em agregados distintos, então uma reserva registrada no mesmo instante de uma renovação pode não recusá-la.
9. `decided: rules/lending/returned-reserved-copy-held-for-collection.log.md entries[0] — statement` — "3 dias" lidos como três dias corridos; o material conta o prazo do empréstimo em dias corridos e não dá outra contagem.
10. `decided: rules/lending/returned-reserved-copy-held-for-collection.log.md entries[1] — consistency` — `eventual`; o aviso não precisa ocorrer na mesma transação da devolução.
11. `decided: rules/lending/overdue-loan-accrues-daily-fine.log.md entries[0] — statement` — o material pergunta (pergunta em aberto) se a multa é por dia ou fixa, e a diretoria sugere R$ 1,00 por dia; decidido BRL 1.00 por dia corrido de atraso, seguindo a recomendação da diretoria, único valor oferecido.
12. `decided: contracts/lending/reserved-copy-returned.log.md entries[0] — type` — o material diz que o sócio "é avisado" mas não nomeia evento; decidido `domain-event`, `published`, payload `domain/lending/reservation`.

## Leitura do `--shape` e o que ficou de pé

- Frase compartilhada "unreturned loan whose due date has passed must" (8 palavras × 2 nós: `overdue-loan-blocks-borrowing`, `overdue-loan-accrues-daily-fine`). Mantida: a frase é a própria condição de atraso, derivada de dois atributos declarados (`due_on`, `returned_on`); dar-lhe um nome como estado armazenado (ex.: um `status` no empréstimo) poria um fato derivado num segundo lar. O par foi ao cruzamento: as duas regras dão consequências distintas (bloqueio vs. multa) à mesma condição, sem caso decidido de forma diferente e sem sobreposição.
- Três logs com `why` no p90 (`loan`, `reserved-copy-blocks-renewal`, `returned-reserved-copy-held-for-collection`): relidos; cada um carrega uma única alegação sobre o valor decidido. Com 12 entradas o p90 é praticamente o máximo.
- Nenhum `statement` com mais de uma frase, nenhum `expression`, nenhum nome sem nó, fechamento de leitura 0 em todos.

## Cruzamento (passo 5): itens de observação, sem caso a decidir

- O fim de uma reserva (retirada pelo sócio ou prazo de três dias vencido) não é declarado: `reserved-copy-blocks-renewal` vale "enquanto uma reserva é mantida", e o material não diz quando ela deixa de ser. Próximo incremento deve declarar o ciclo de vida da reserva.
- `returned-reserved-copy-held-for-collection` × `overdue-loan-blocks-borrowing` / `member-holds-at-most-three-loans`: um sócio com atraso ou com três empréstimos não pode retirar o exemplar reservado para ele; nenhuma das regras diz o contrário, então não há contradição, mas o material não trata o caso.
- `loan-falls-due-fourteen-days-after-borrowing` × `renewal-extends-due-date-by-fourteen-days`: disjuntas (a primeira só vale para empréstimo não renovado). O cenário de Ana (retira no dia 1, vence no dia 15, bloqueada no dia 16) é coerente com ambas.

## Livro-razão (`trace.py --ledger`), verbatim

```
ledger sound: 10 fact line(s) over 1 material file(s) — 8 landed in 13 node(s), 2 left out with a reason, 0 open
  left out, by reason (2 distinct, largest first):
    1 × A button's color and label and a list's sort order are interface choices the implementation makes, never a fact of the domain (SPEC-005 R2).
    1 × States the purpose of the system as a whole, which the lending context exists to serve, and no fact of its own.
  candidates, all: contracts/lending/reserved-copy-returned domain/lending/copy domain/lending/loan domain/lending/reservation rules/lending/loan-falls-due-fourteen-days-after-borrowing rules/lending/loan-renews-at-most-once rules/lending/member-holds-at-most-three-loans rules/lending/overdue-loan-accrues-daily-fine rules/lending/overdue-loan-blocks-borrowing rules/lending/renewal-extends-due-date-by-fourteen-days rules/lending/reserved-copy-blocks-renewal rules/lending/returned-reserved-copy-held-for-collection scenarios/lending/overdue-member-cannot-borrow
```

Livro-razão em `docs/ledger.md`. Nenhuma linha em aberto: a pergunta da multa (linha 13) foi decidida (decisão 11). Fora: linha 12 (botão verde e ordenação da lista — interface) e linha 3 (propósito geral, nenhum fato próprio).

## O que este incremento pode ter posto em violação

Este passo nunca lê o código-alvo. Os nós escritos aqui podem declarar obrigações que código já entregue viola, e nada nesta invocação poderia perceber. Só uma reconciliação descobre isso, se alguém a executar; nada a agenda.

## Candidatos para uma reconciliação (nós deste incremento)

domain/lending/_context, domain/lending/member, domain/lending/loan, domain/lending/title, domain/lending/copy, domain/lending/reservation, rules/lending/member-holds-at-most-three-loans, rules/lending/overdue-loan-blocks-borrowing, rules/lending/loan-falls-due-fourteen-days-after-borrowing, rules/lending/renewal-extends-due-date-by-fourteen-days, rules/lending/loan-renews-at-most-once, rules/lending/reserved-copy-blocks-renewal, rules/lending/returned-reserved-copy-held-for-collection, rules/lending/overdue-loan-accrues-daily-fine, scenarios/lending/overdue-member-cannot-borrow, contracts/lending/reserved-copy-returned

## Validação final, verbatim

```
specification sound: 5 element(s), 8 rule(s), 1 scenario(s), 1 contract(s) across 1 context(s); 12 decision(s) disclosed
```

`--project` escreveu: `projected 5 file(s) into .../spec/projections: capability-map.mmd, class-diagram-lending.mmd, context-map.mmd, full-text.md, overview.md`

## Próximo passo

`/plan-work` invocation ready to paste:

```
/plan-work /tmp/analyse-bench/iteration-2/projects/file-material-empty-root target <target> slug <slug> — <o escopo, em prosa>
```

(O único alvo declarado em `siegard.json` é `app`.) O material não é levantamento nem material de intenção, então nenhuma invocação de `/reconcile` como adoção é entregue.

A revisão é `git diff` sobre `spec/` e `docs/ledger.md`; quem fizer o commit da especificação leva o livro-razão no mesmo commit, por caminho.
