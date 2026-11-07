# /deliver-scope lending — epic/fees, alvo `app`

A execução começou com `HEAD` em `be24402` no `main` e comitou ali mesmo, sem criar branch; se preferir isolar o trabalho, cortar uma branch a partir de `be24402` é decisão sua.

Pedido (lido de `ask.py --read`, sha256 38f9a15bc91f4f7b): «Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa que falta, revisa e comita cada passo, sem parar no meio pra me perguntar.»

## O que foi feito

- **Plano**: pulado — o pedido nomeia `epic/fees`, que o plano vivo `lending` já contém; nada comitado.
- **Entrega**: `task/fees/compute-late-fee` — implementação e prova escritas, suíte verde. Commit `da76c47` `deliver-scope lending: deliver task/fees/compute-late-fee`.
- **Revisão**: `/review-change` com o nome `lending` (o slug, livre), sobre `lending/fees.py` e `tests/test_fees.py`. Commit `8670959` `deliver-scope lending: review`.
- **Fechar o que restou testável**: nada a fazer — a revisão não recusou nenhuma certificação (nenhum registro de prova traz `demonstrates`, então nenhuma foi encenada).
- **Medição**: `telemetry.py --since 2026-11-07T12:00:00Z` escreveu `telemetry/20261107T180850Z.json`. Os transcripts do harness estavam indisponíveis (`/home/siegfriedneto/.claude/projects/-tmp-dsb-runs2-compaction-resume--before-1-p is not a directory`), então agentes, comandos e handoffs ficam ausentes com esse motivo. Commit `e83aba9` `deliver-scope lending: measure` (inclui as últimas linhas de `delivery/lending/orchestration.md`).

Commits desta execução, do mais novo ao mais antigo: `e83aba9`, `8670959`, `da76c47`. Nada enviado (push), nenhuma branch criada. Nenhum `deliver.py --outstanding` imprimiu linhas sobre registros com padrão ausente ou divergente.

## Achados da revisão `lending` (relatados inteiros, não tratados aqui)

Cobertura: 1 critério coberto, 1 parcial, 0 descobertos. Conformidade: 2 achados, ambos `unstated`. Padrão: nada se desviou de PY-01. Falhas: `run/lending` passou.

**Cobertura parcial** — «A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.»: o passo de 100 centavos por dia é exercitado, mas o valor de uma devolução específica não — o teste aceita qualquer taxa entre (days_late - 1) * 100 e days_late * 100, então um erro de um dia em qualquer direção passa, e nenhum teste fixa a taxa de um empréstimo devolvido um dia após o vencimento. O próprio critério não diz se o dia do vencimento ou o da devolução entra na contagem.

1. **conformance / unstated** — `lending/fees.py`, contagem de dias em `late_fee_cents`, linha 7: `overdue_days = (loan.returned_on - loan.due_on).days`. Custo: o nó não diz se o dia do vencimento ou o da devolução conta; o código decide que a contagem é a diferença das datas (um dia de atraso = BRL 1,00), e essa decisão vive só nessa linha. Correção: `rules/lending/late-fee-per-overdue-day` declara como os dias são contados (qual extremo, se algum, conta), e o código é relido contra isso.
2. **conformance / unstated** — `lending/fees.py`, guarda em `late_fee_cents`, linhas 8-9: `if overdue_days <= 0: return 0`. Custo: o nó só declara a taxa de devolução após o vencimento; que devolução no dia ou antes não paga taxa vive só aqui e no critério da tarefa. Correção: um nó, provavelmente `rules/lending/late-fee-per-overdue-day`, ganha a afirmação de que devolução no vencimento ou antes não gera taxa.

Notas da revisão: nenhum subagente do plugin estava registrado, então os passes rodaram inline sob a disciplina de cada arquivo de agente; os retornos inline de conformidade estão em `siegard-reconcile/lending.returns/`. O passe de conformidade não tratou a taxa ser `int` de centavos enquanto `domain/lending/loan` declara `late_fee` como valor decimal em BRL, representação que PY-01 governa.

## Próximo passo

O escopo `epic/fees` está entregue, revisado e medido; esta execução termina aqui. O que fazer com os achados é seu: **o valor de um achado é uma das três questões que nunca recebem recomendação** — se merecem uma rota, e qual, só você decide. O que decide cada lado:

- **Especificar a contagem de dias e a regra do "sem taxa"** (achados 1 e 2, e a cobertura parcial que depende deles): `/analyse` com o seu texto declarando como os dias entre vencimento e devolução são contados e que devolução no vencimento ou antes não gera taxa, sobre `rules/lending/late-fee-per-overdue-day`. Vale se a regra do código (diferença das datas; um dia de atraso = BRL 1,00) não for a que o negócio quer, ou se você quer a regra escrita onde o próximo leitor a procura.
- **Deixar como está**: vale se a decisão do código é aceitável sem estar na especificação; os achados continuam registrados em `delivery/lending/review/lending.md`.
- A representação da taxa (`int` de centavos vs. decimal em BRL de `domain/lending/loan`) não foi um achado; se importar, é um pedido novo.

Corrigir qualquer coisa que um achado nomeia é um pedido novo.
