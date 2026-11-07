# /analyse — relatório

Projeto: `/tmp/analyse-bench/iteration-3/projects/file-material-empty-root`
Raiz da especificação: `spec/` (vazia antes desta execução; árvore limpa no `git status`).
Material: `docs/material.md` (arquivo; ledger em `docs/ledger.md`).

## Nós escritos (todos criados; nada alterado ou removido), com campos decididos conforme `spec.py --shape --of`

- `domain/lending/_context` — 1 decidido / 1 declarado
- `domain/lending/member` — 3 / 10
- `domain/lending/loan` — 2 / 16
- `domain/lending/copy` — 2 / 7
- `domain/lending/title` — 1 / 4
- `domain/lending/reservation` — 1 / 9
- `rules/lending/member-holds-at-most-three-loans` — 0 / 4
- `rules/lending/loan-due-date` — 1 / 3
- `rules/lending/loan-renewed-at-most-once` — 0 / 3
- `rules/lending/renewal-refused-while-copy-reserved` — 1 / 5
- `rules/lending/overdue-loan-blocks-checkout` — 0 / 4
- `rules/lending/reserving-member-notified-on-return` — 1 / 5
- `rules/lending/reserved-copy-held-three-days` — 1 / 3
- `rules/lending/overdue-fine-per-day` — 1 / 3
- `scenarios/lending/overdue-member-cannot-check-out` — 0 / 7

## Conjunto de impacto lido

Nenhum: a raiz estava vazia, então não havia nó a situar (passo 1 pulado, como o skill determina).

## Decisões registradas nesta execução (primeira linha do escritor)

- `decided: domain/lending/_context.log.md entries[0] — strategic` — `core`: empréstimo é todo o problema que o material pede para controlar.
- `decided: domain/lending/member.log.md entries[0] — type` — `aggregate-root`: o limite de 3 e o bloqueio por atraso são decididos por sócio.
- `decided: domain/lending/member.log.md entries[1] — attributes.name` — `name`, string, obrigatório: o exemplo identifica a sócia pelo nome (Ana).
- `decided: domain/lending/member.log.md entries[2] — relationships.loan` — composição `0..*`: as duas regras contam os empréstimos de um sócio juntos, na mesma transação.
- `decided: domain/lending/loan.log.md entries[0] — type` — `entity` dentro do agregado `member`.
- `decided: domain/lending/loan.log.md entries[1] — attributes.renewed` — booleano obrigatório: uma única renovação só precisa saber se já ocorreu.
- `decided: domain/lending/copy.log.md entries[0] — type` — `aggregate-root`: empréstimo e reserva apontam para o exemplar por identidade.
- `decided: domain/lending/copy.log.md entries[1] — attributes.inventory_number` — string obrigatória: o material não nomeia atributo que distinga exemplares do mesmo título.
- `decided: domain/lending/title.log.md entries[0] — type` — `aggregate-root`.
- `decided: domain/lending/reservation.log.md entries[0] — type` — `aggregate-root`: a reserva tem ciclo próprio, independente do empréstimo.
- `decided: rules/lending/loan-due-date.log.md entries[0] — statement` — a renovação soma 14 dias corridos à data de devolução (não 14 a partir do dia da renovação).
- `decided: rules/lending/renewal-refused-while-copy-reserved.log.md entries[0] — consistency` — `eventual`: a regra cruza o agregado do sócio e o da reserva.
- `decided: rules/lending/reserving-member-notified-on-return.log.md entries[0] — consistency` — `eventual`: o material não fixa prazo para o aviso.
- `decided: rules/lending/reserved-copy-held-three-days.log.md entries[0] — statement` — 3 dias corridos a partir do aviso.
- `decided: rules/lending/overdue-fine-per-day.log.md entries[0] — statement` — R$ 1,00 (1.00 BRL) por dia corrido de atraso, seguindo a sugestão da diretoria; o `unstated` registra a pergunta do material ("por dia ou valor fixo?") e a sugestão.

Leitura do `--shape` deixada de pé, com o motivo:
- `domain/lending/member.log` (131 palavras) e `domain/lending/loan.log` (76) no p90 dos logs: são os logs com mais entradas (3 e 2), cada entrada com uma afirmação só; nada a cortar.
- O `why` de `rules/lending/overdue-fine-per-day` está no p90 (23 palavras) e junta dois apoios (a diretoria é a única que respondeu; por dia acompanha a contagem em dias corridos). Fica: ambos sustentam a mesma escolha, e uma entrada nunca é editada.
- `member` (3/10) é o nó mais decidido: o material descreve o sócio só pelos limites que sofre.

## Verificação cruzada — pontos de atenção (sem caso concreto decidido de forma diferente)

`--shape` não apontou frases compartilhadas nem prosa citando irmãos. Pares que o material juntou (linha 8: `loan-due-date`, `loan-renewed-at-most-once`, `renewal-refused-while-copy-reserved`) não divergem em nenhum caso.
- Observar: um empréstimo já atrasado pode ser renovado? Nenhuma regra decide; nenhuma das existentes decide o caso de forma conflitante.
- Observar: `reserved-copy-held-three-days` guarda o exemplar para quem reservou, enquanto `overdue-loan-blocks-checkout` e `member-holds-at-most-three-loans` podem impedir essa pessoa de retirá-lo; "ficar disponível" não é "retirada permitida", então não há contradição.
- Observar: o que acontece com a reserva depois dos 3 dias não é dito pelo material.

## Ledger (`trace.py --ledger`, saída literal)

```
ledger sound: 10 fact line(s) over 1 material file(s) — 8 landed in 12 node(s), 2 left out with a reason, 0 open
  left out, by reason (2 distinct, largest first):
    1 × A button's colour and label and a list's on-screen ordering are what the interface chose, never a fact of the lending domain.
    1 × The opening paragraph names the library's goal of controlling loans and states no fact of its own.
  candidates, all: domain/lending/copy domain/lending/loan domain/lending/title rules/lending/loan-due-date rules/lending/loan-renewed-at-most-once rules/lending/member-holds-at-most-three-loans rules/lending/overdue-fine-per-day rules/lending/overdue-loan-blocks-checkout rules/lending/renewal-refused-while-copy-reserved rules/lending/reserved-copy-held-three-days rules/lending/reserving-member-notified-on-return scenarios/lending/overdue-member-cannot-check-out
```

Nenhuma linha em aberto. A pergunta da multa (linha 13) foi decidida neste incremento, seguindo a sugestão da diretoria, e está divulgada no log de `rules/lending/overdue-fine-per-day`.

## O que este incremento pode ter colocado o código entregue em violação

Este passo nunca lê o alvo, de propósito: um nó escrito aqui pode afirmar uma obrigação que o código já entregue viola, e nada nesta execução teria notado. Só uma reconciliação descobre isso, se alguém a rodar; nada a agenda. (O alvo `app` é a própria raiz do projeto, que hoje só contém `docs/` e `spec/`.)

## Candidatos para uma reconciliação (nós deste incremento)

domain/lending/_context, domain/lending/member, domain/lending/loan, domain/lending/copy, domain/lending/title, domain/lending/reservation, rules/lending/member-holds-at-most-three-loans, rules/lending/loan-due-date, rules/lending/loan-renewed-at-most-once, rules/lending/renewal-refused-while-copy-reserved, rules/lending/overdue-loan-blocks-checkout, rules/lending/reserving-member-notified-on-return, rules/lending/reserved-copy-held-three-days, rules/lending/overdue-fine-per-day, scenarios/lending/overdue-member-cannot-check-out

## Validação final (literal) e projeções

```
specification sound: 5 element(s), 8 rule(s), 1 scenario(s) across 1 context(s); 15 decision(s) disclosed
```

`spec.py --project`: `projected 5 file(s) into /tmp/analyse-bench/iteration-3/projects/file-material-empty-root/spec/projections: capability-map.mmd, class-diagram-lending.mmd, context-map.mmd, full-text.md, overview.md`

## Próximo passo

`/plan-work` invocation ready to paste (o alvo `app` está preenchido porque `siegard.json` declara só esse alvo):

```
/plan-work /tmp/analyse-bench/iteration-3/projects/file-material-empty-root target app slug <slug> — <o escopo, ou o incremento, em prosa>
```

Não há `/reconcile` a oferecer como adoção: o material não é levantamento (`siegard-survey/1`) nem material de intenção (`siegard-intent/1`).

A revisão é o `git diff` sobre `spec/` e `docs/ledger.md`; quem fizer o commit da especificação leva o ledger no mesmo commit, pelo caminho. Nada foi commitado.
