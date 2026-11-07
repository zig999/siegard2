Rodada `deliver-scope lending` concluída sobre `main`, onde `HEAD` estava em 8e28631 quando a rodada começou (2026-11-07T12:00:00Z). Para isolar este trabalho num branch próprio, cortá-lo é um ato seu: `git branch deliver-scope/lending 46fef06`.

## O que foi feito

Pedido (verbatim): "Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa que falta, revisa e comita cada passo, sem parar no meio pra me perguntar."

- Projeto: `/tmp/dsb/runs/compaction-resume--before-1/p`; target `app`; slug `lending` (plano vivo, retomada); alcance `epic/fees`.
- Gate: `spec.py spec` passou sobre raiz commitada; árvore limpa.
- Passo 1 (plano): pulado — o pedido nomeia `epic/fees`, que o plano vivo `lending` contém. Nada commitado.
- Passo 3 (entrega): `deliver.py --outstanding ... --scope epic/fees` listou `task/fees/compute-late-fee`; `/implement-task` entregou (implementação e prova escritas, suíte verde, sem parada).
- Passo 4 (revisão): `/review-change` sobre `task/fees/compute-late-fee`, arquivos `lending/fees.py` e `tests/test_fees.py`, nome da revisão `lending` (o slug, livre nas quatro posições). Registro em `delivery/lending/review/lending.md`; run `run/lending` verde.
- Passo 5 (fechar o testável): nada a fazer — a revisão não encenou nem recusou nenhuma certificação (nenhum registro de prova carrega `demonstrates`), logo não há `remainder: testable` a provar.
- Passo 6 (medida): `telemetry.py --probe` e depois `telemetry.py --since 2026-11-07T12:00:00Z` sobre a raiz do projeto. Relatório em `telemetry/20261107T175338Z.json`, lido só do disco: o diretório de transcrições do harness não existe (`/home/siegfriedneto/.claude/projects/-tmp-dsb-runs-compaction-resume--before-1-p is not a directory`), então agentes, sessões, comandos e handoffs constam como `unavailable`. Do disco: 3 runs capturados, 3 commits, 15 decisões adicionadas, 1 revisão (critérios: 1 covered, 1 partial).

Commits desta rodada, do mais novo:

```
46fef06 deliver-scope lending: measure
c2f5bdc deliver-scope lending: review
ff4d77c deliver-scope lending: deliver task/fees/compute-late-fee
```

O commit de medida leva também a linha do log da revisão (que ainda estava pendente após a compactação) e a linha da própria medida; `delivery/lending/orchestration.md` agora tem uma linha por passo. Árvore limpa ao final.

## A revisão — achados, repassados inteiros

2 findings (conformance `unstated` 2); nenhuma certificação encenada ou recusada. Cobertura: 1 critério covered, 1 partial.

1. **conformance / unstated** — `lending/fees.py`, a contagem de dias em `late_fee_cents`, linha 7.
   Evidência: `overdue_days = (loan.returned_on - loan.due_on).days`
   Custo: o "each calendar day between its due date and its return" do nó não diz se a data de vencimento ou o dia da devolução contam; o código decide que a contagem é a diferença das datas, então um empréstimo devolvido um dia atrasado carrega BRL 1.00, e essa decisão vive só nessa linha.
   Correção indicada: `rules/lending/late-fee-per-overdue-day` declara como os dias corridos entre vencimento e devolução são contados (qual ponta, se alguma, conta), e o código é lido contra isso.
2. **conformance / unstated** — `lending/fees.py`, o guarda em `late_fee_cents`, linhas 8-9.
   Evidência: `if overdue_days <= 0: return 0`
   Custo: o nó declara a multa só de empréstimo devolvido após o vencimento; que um empréstimo devolvido no vencimento ou antes não carrega multa vive só aqui e no critério da tarefa.
   Correção indicada: um nó, mais plausivelmente `rules/lending/late-fee-per-overdue-day`, ganha a declaração de que empréstimo devolvido no vencimento ou antes não carrega multa por atraso.

Cobertura parcial: o critério "A loan returned after its due date carries 100 cents for each calendar day between its due date and its return." está `partial` — o teste aceita qualquer multa de `(days_late - 1) * 100` a `days_late * 100`, então uma contagem errada em um dia passa, e nenhum teste fixa a multa de um empréstimo devolvido um dia após o vencimento. O próprio critério não diz qual ponta conta — a mesma lacuna do achado 1.

Notas da revisão: nenhum subagente do plugin estava registrado, então as passadas de cobertura, conformidade e padrão rodaram inline sob a disciplina de cada arquivo de agente; os retornos de conformidade estão verbatim em `siegard-reconcile/lending.returns/`. A passada de conformidade não tratou a multa ser um `int` de centavos enquanto `domain/lending/loan` declara `late_fee` como valor decimal em BRL — representação que PY-01 governa.

Linhas de `--outstanding` sobre registros sem padrão fixado ou com padrão diferente: nenhuma registrada na rodada.

## Próximo passo — a decisão é sua

Os dois achados e a cobertura parcial apontam para a mesma lacuna da especificação: como se contam os dias de atraso. Quanto vale um achado é uma das três perguntas que só você decide, e esta rodada não recomenda por cima dela. Corrigir qualquer coisa que um achado nomeia é um novo pedido.

- **Especificar a contagem de dias** — o achado é real e o nó deve declará-la. Decide por esta porta: você saber qual ponta conta (ou querer que ela seja decidida e registrada). Invocação, com o material sendo os dois achados:
  `/analyse /tmp/dsb/runs/compaction-resume--before-1/p target app — rules/lending/late-fee-per-overdue-day: state how the calendar days between a loan's due date and its return are counted (which end, if any, counts), and that a loan returned on or before its due date carries no late fee; see delivery/lending/review/lending.md findings 1 and 2`
  Depois, uma nova entrega sobre o slug reconcilia código e teste com o que o nó passar a dizer.
- **Deixar como está** — a diferença das datas é a leitura pretendida e a lacuna não custa nada agora. Decide por esta porta: o comportamento atual (1 dia de atraso = BRL 1.00) ser o que você quer. Nada a invocar; os achados ficam no registro da revisão.
