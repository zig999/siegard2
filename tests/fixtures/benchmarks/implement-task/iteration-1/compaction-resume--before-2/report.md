# /implement-task — task/fees/compute-late-fee (retomado após compactação)

## Relatório

Entregue: `task/fees/compute-late-fee` no alvo `app`, iniciativa `lending`.

- **Raízes** (de `project.py`): specification_root `spec`, work_root `work`, delivery_root `delivery`, alvo `app` → `app`.
- **Standard**: `app/standard.yaml`, resolvido pelo campo `standard` de `siegard.json` (nenhum nomeado na invocação). `deliver.py --standard` limpo.
- **Plano**: `plan.py --check` limpo; árvore limpa antes de qualquer escrita; `--outstanding` listou a tarefa como entregável, sem nota BLOCKING e sem registro prévio (não é re-entrega).
- **Set up**: não rodou — o registro não declara passo `install`/`prepare`.
- **Implement** (inline — a sessão não pode criar subagentes; disciplina de `agents/task-implementer.md` aplicada no lugar): `app/lending/fees.py` — `late_fee_cents(loan)` responde 100 centavos por dia corrido após `due_on`, 0 quando devolvido no prazo; recusa com `ValueError` um empréstimo não devolvido.
- **Build**: `run/fees-compute-late-fee-build` — passou.
- **Registro de implementação**: `delivery/lending/implementation/fees/compute-late-fee.md` (via `deliver.py --write-implementation`).
- **Prove** (inline — disciplina de `agents/test-author.md` aplicada no lugar): `app/tests/test_fees.py`, 4 testes:
  - devolvido antes do vencimento → 0 (classe);
  - devolvido no dia do vencimento → 0 (fronteira);
  - devolvido um dia após → 100 (fronteira);
  - devolvido 10 dias corridos após, atravessando a virada de mês → 1000 (classe).
- **Suite**: `run/fees-compute-late-fee-suite` (build + `python3 -m pytest -q tests`) — passou na primeira tentativa; nenhuma tentativa vermelha.
- **Registro de prova**: `delivery/lending/proof/fees/compute-late-fee.md` (via `deliver.py --write-proof`, pin da implementação `sha256:22c4804e…` estampado pelo writer). Os testes de critério não reivindicam `demonstrates`.
- **Validate**: `deliver.py --unrecorded` — todo caminho alterado sob `app` é nomeado pelos 2 registros; `deliver.py` derivou `delivery/lending/delivery.json` (2 nós, 3 arestas, 1 de 1 tarefa com registro, 0 critérios não atendidos, 0 achados); `--check` confere.
- **Bind**: `trace.py --bind-record` ligou `rules/lending/late-fee-per-overdue-day` a `lending/fees.py` em `siegard-trace.json`.

**Passos executados inline** (sem subagentes): implement e prove. Os dois produtores foram escritos no mesmo contexto, portanto a separação entre implementação e prova que o arranjo pressupõe não existiu nesta entrega — a revisão é o que a compensa.

**Deixado sem prova, por registro** (`untested`):
- `rules/lending/late-fee-per-overdue-day` — o fato vale para todo empréstimo devolvido com atraso, um conjunto que nenhum nó enumera; nenhum teste finito o decide por inteiro. A ligação no trace permanece decidida por leitura até uma certificação.
- A inferência de que um empréstimo ainda não devolvido é recusado com `ValueError` — nenhum nó decide isso; não foi fixada por teste. Se o negócio deve dizer o que vale aí, a rota é `/analyse`.

**Estado git**: nada foi commitado. Pendentes: `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/` (registros, runs, `delivery.json`), `siegard-trace.json`.

## Handoff

Portas:

1. **`/review-change` sobre esta entrega** — recomendada (julgada: nenhum fato em disco decide entre as portas; implement e prove rodaram no mesmo contexto, então a revisão independente é a primeira leitura separada que esta entrega recebe). O que reverteria isso: você preferir commitar antes e revisar depois sobre o commit.
   ```
   /review-change /tmp/itbench/runs/compaction-resume-base2/p lending task/fees/compute-late-fee
   ```
2. **Commitar a entrega** — decisão sua; esta skill não commita. Escopo por pathspec:
   ```
   git -C /tmp/itbench/runs/compaction-resume-base2/p add app/lending/fees.py app/tests/test_fees.py delivery/lending siegard-trace.json
   ```
