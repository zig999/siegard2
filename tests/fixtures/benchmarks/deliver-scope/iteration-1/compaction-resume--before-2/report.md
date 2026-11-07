O run começou em `main` com HEAD em 7e7915c; para rodar numa branch própria, crie-a a partir de 7e7915c (o ato é seu, esta skill nunca cria branch).

# deliver-scope lending — epic/fees entregue de ponta a ponta

**Pedido (verbatim):** "Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa que falta, revisa e comita cada passo, sem parar no meio pra me perguntar."

- Projeto: `/tmp/dsb/runs/compaction-resume--before-2/p`; target `app`; slug `lending` (plano vivo, retomado); alcance `epic/fees`.
- Gate: `spec.py spec` passou sobre raiz commitada; árvore limpa no início.
- Retomado após compactação a partir do resumo da sessão: o resumo não trazia a linha `read:` de um `ask.py --record`, então não houve `ask.py --read` a rodar; o pedido acima é o que o resumo cita (SPEC-010 R3 prefere o pedido gravado).

## Passos e commits

| Passo | Resultado | Commit |
|---|---|---|
| plan | pulado — o pedido nomeia `epic/fees`, que o plano vivo `lending` contém | — |
| deliver task/fees/compute-late-fee | implementação e prova escritas, suíte verde | 531da7c |
| review `lending` | registro escrito, 2 achados, nenhuma certificação preparada ou recusada | e869fa2 |
| prove | pulado — nenhuma certificação recusada, nenhum remainder `testable` | — |
| measure | `telemetry/20261107T175335Z.json` (só disco; transcripts indisponíveis) + linhas do log | d4c711b |

`deliver.py --outstanding ... --scope epic/fees` agora: "every task in the scope has a record, and every record its proof". Linha relatada verbatim:
`standard.yaml (target app): pinned by 3 record(s); an invocation naming no standard now writes source these rules will still be read against`

Log: `delivery/lending/orchestration.md`.

## Review `lending` — achados (relatados inteiros, não tratados aqui)

Cobertura: 1 critério coberto, 1 parcial, 0 descobertos. Conformance: 2 achados `unstated`.

**Cobertura parcial** — "A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.": o teste aceita qualquer taxa entre (days_late - 1) * 100 e days_late * 100 centavos, então uma contagem de dias errada por um passa; nenhum teste fixa a taxa de um empréstimo devolvido um dia depois do vencimento. O próprio critério não diz se o dia do vencimento ou o da devolução entram na contagem.

1. **conformance / unstated** — `lending/fees.py`, contagem de dias em `late_fee_cents`, linha 7: `overdue_days = (loan.returned_on - loan.due_on).days`. O nó não diz se o vencimento ou o dia da devolução contam; o código decide que é a diferença das datas (1 dia de atraso = BRL 1.00), e essa decisão vive só nessa linha. Correção apontada: `rules/lending/late-fee-per-overdue-day` declarar como os dias são contados.
2. **conformance / unstated** — `lending/fees.py`, guarda em `late_fee_cents`, linhas 8-9: `if overdue_days <= 0: return 0`. Que um empréstimo devolvido no ou antes do vencimento não paga taxa vive só aqui e no critério da tarefa. Correção apontada: um nó, plausivelmente `rules/lending/late-fee-per-overdue-day`, ganhar essa declaração.

Notas do registro: a review notou também que a taxa é `int` em centavos enquanto `domain/lending/loan` declara `late_fee` como valor decimal em BRL (representação governada por PY-01), sem levantar achado.

## Medição

`telemetry.py --probe` e depois `telemetry.py --since 2026-11-07T12:00:00Z`: 3 runs capturados, 3 commits na janela, 15 decisões adicionadas, 1 review (1 coberto, 1 parcial). Os transcripts do harness não existem para este diretório, então agentes, comandos e handoffs estão indisponíveis — uma linha, não uma parada.

## Próximo passo

Uma porta só, e ela é sua: os dois achados são lacunas da especificação (`unstated`), e decidir se e como cada um merece rota é uma pergunta sobre o valor de um achado — reservada a você, sem recomendação. O que decide: se a contagem de dias e a taxa zero devem ser declaradas no nó `rules/lending/late-fee-per-overdue-day`. Se sim, isso é um novo pedido, a partir de `/analyse` sobre esse nó, com o texto que você decidir — por exemplo:

```
/analyse /tmp/dsb/runs/compaction-resume--before-2/p "rules/lending/late-fee-per-overdue-day: <como os dias entre vencimento e devolução são contados, e que devolução no ou antes do vencimento não paga taxa>"
```

Se não, nada fica pendente: o épico está entregue, revisado e commitado.
