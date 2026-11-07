# /plan-work — relatório

**Invocação:** `/plan-work /tmp/pwbench/runs/compaction-resume-prior1/p target app slug lending — Members renew their loans. …`
**Retomada:** esta invocação foi retomada após uma compactação de contexto; os passos 1–4 abaixo foram feitos antes dela e são relatados a partir do resumo da compactação e do que está em disco. Validação e relatório foram feitos depois.

## Entradas

- project root: `/tmp/pwbench/runs/compaction-resume-prior1/p` (nomeada na invocação)
- `project.py`: `specification_root` = `spec`, target `app` → `app`, work root = `work/lending`
- standard: `app/standard.yaml`, respondido pela linha `standard:` do `siegard.json` (a invocação não nomeou nenhum)
- `spec.py spec`: passou limpo
- `git status --porcelain -- work/lending spec` antes de qualquer escrita: não imprimiu nada

## Passos

1. **situate** — `spec.py --digest` e `spec.py --impact` sobre as quatro regras de lending que o escopo nomeia; `deliver.py --standard app/standard.yaml --against app` não encontrou nada ausente, então nenhuma task declara `produces`.
2. **inventory** — o spawn de `siegard:codebase-surveyor` falhou: nenhum agente deste plugin está registrado nesta sessão. Feito pela rota inline. Escopo persistido em `work/lending/intake/scope.md`; inventário em `inventory/lending-app.md`.
3. **decompose** — o spawn de `siegard:task-decomposer` falhou: nenhum agente deste plugin está registrado nesta sessão. Feito pela rota inline: `epic/renewals`, `task/renewals/compute-due-date`, `task/renewals/renew-loan`.
4. **implement-against** — o spawn de `siegard:spec-binder` falhou: nenhum agente deste plugin está registrado nesta sessão. Feito pela rota inline, uma vez por task; nenhum binder retornou nota, então nenhum fato foi decidido e a especificação não foi alterada. `plan.py --node` passou em cada task.

   Atenção: com as três rotas inline, o isolamento do binder **não** se manteve — a mesma sessão que cortou as tasks também as vinculou à especificação.
5. **validate** —
   ```
   $ plan.py --standard app/standard.yaml --against app work/lending spec
   derived work/lending/plan.json: 4 node(s), 9 edge(s), contract siegard-plan/3
     1 inventory, 1 epic, 2 task; 4 specification node reference(s) implemented (4 unique)
   (exit 0)
   $ plan.py --check work/lending spec
   plan checked: work/lending/plan.json matches 4 node(s)
   (exit 0)
   $ plan.py --notes work/lending
   notes standing: blocking 0, underdetermined 0, uncovered 0
   (exit 0)
   ```

## O plano

| task | implementa | depende de |
|---|---|---|
| `task/renewals/compute-due-date` | `rules/lending/loan-due-fourteen-days-after-borrowing` | — |
| `task/renewals/renew-loan` | `rules/lending/loan-renewed-at-most-once`, `rules/lending/renewal-extends-due-date-fourteen-days`, `rules/lending/reserved-copy-blocks-renewal` | `task/renewals/compute-due-date` |

O epic `epic/renewals` cobre as quatro regras, todas implementadas e nenhuma em `uncovered`.

- Decisões gravadas na especificação: nenhuma. `spec/` não foi alterado.
- Notas classificadas: 0 blocking, 0 underdetermined.

## Revisão

Tudo o que esta invocação escreveu está em `work/lending/` (ainda não rastreado pelo git): `git status -- work/lending spec` mostra apenas `?? work/lending/`. Nada foi commitado. O commit é uma decisão sua.

## Próximos passos

1. **Revise e faça o commit de `work/lending/`** (`git add work/lending && git commit`). Só você pode fazer isso: o plano não faz commit.
2. **`/implement-task /tmp/pwbench/runs/compaction-resume-prior1/p task/renewals/compute-due-date`** — a única task sem dependência em aberto.
3. **`/deliver-scope`** sobre `work/lending` — entrega as duas tasks em ordem.

**Recomendação (derivada):** primeiro o 1, depois o 2.
- **Por quê:** `renew-loan` depende de `compute-due-date`, então a ordem é decidida pelo `depends_on`, não por julgamento. E um work root não commitado deixa a delivery sem uma base limpa para comparar.
- **O que mudaria isso:** se você quiser entregar as duas tasks numa execução só, o 3 substitui o 2. Essa escolha (uma task de cada vez ou entrega orquestrada) é questão de custo e de como você lê seu próprio pedido, e é sua.
