# /implement-task — task/fees/compute-late-fee

Entrega concluída: fonte, testes, build e suite verdes, registros validados, nó vinculado ao trace.

## Entradas
- project root: `/tmp/itbench/runs/compaction-resume-base1/p`
- target: `app` (único em `targets`); slug: `lending`; task: `task/fees/compute-late-fee`
- standard: `app/standard.yaml`, respondido pelo campo `standard` de `siegard.json` (via `project.py`)
- `plan.py --check`: limpo; árvore: limpa no início; `--outstanding`: task entregável, sem nota `BLOCKING, from the specification —`, sem registro anterior (não é re-delivery)

## O que foi feito
1. **set up** — não rodou: o registry não declara passo de install.
2. **implement** — inline (a sessão não pode criar subagents; disciplina de `agents/task-implementer.md` aplicada no lugar). Fonte: `app/lending/fees.py` — `late_fee_cents(loan)` responde 100 centavos por dia de calendário após `due_on`, 0 até o vencimento inclusive.
3. **build** — `run/fees-compute-late-fee-build`: passed.
4. **implementation record** — `delivery/lending/implementation/fees/compute-late-fee.md` (via `deliver.py --write-implementation`).
5. **prove** — inline (disciplina de `agents/test-author.md` aplicada no lugar). `app/tests/test_fees.py`, 4 testes:
   - devolvido antes do vencimento → 0
   - devolvido no dia do vencimento → 0 (limite)
   - devolvido 1 dia depois → 100 (limite)
   - devolvido 7 dias depois → 700 (multiplicação por dia)
6. **suite** — `run/fees-compute-late-fee-suite` (build + `python3 -m pytest -q tests`): passed, `5 passed`. Nenhuma tentativa vermelha.
7. **proof record** — `delivery/lending/proof/fees/compute-late-fee.md` (via `deliver.py --write-proof`, run e standard carimbados; pin da implementação `sha256:afe5f2ec…`).
8. **validate** — `deliver.py --unrecorded`: todo caminho alterado sob `app` está nomeado pelos 2 registros. `deliver.py`: `delivery/lending/delivery.json` derivado — 2 nós, 3 arestas, 1 de 1 task com registro, 0 critérios não atendidos, 0 findings. `deliver.py --check`: atual.
9. **bind** — `trace.py --bind-record`: `rules/lending/late-fee-per-overdue-day` vinculado a `lending/fees.py` em `siegard-trace.json`. `trace.py --check app`: sem drift, 1 binding.

## Divulgações
- **Passos inline:** implement e prove rodaram inline, na mesma sessão — a separação entre implementador e autor dos testes, que é o propósito do arranjo, **não** valeu nesta entrega. A revisão deve ler os testes sabendo disso.
- **Inferência (não testada):** um empréstimo ainda não devolvido é recusado com `ValueError`; nenhum nó nem critério decide isso. Está em `untested`, sem teste que o fixe.
- **Nó sem prova por teste:** `rules/lending/late-fee-per-overdue-day` vale para qualquer quantidade de dias de atraso — uma totalidade que nenhum teste finito decide por inteiro. Fica em `untested`; nenhum teste reivindica `demonstrates`. O binding no trace é, portanto, por leitura, não decidido por teste.
- **Compactação:** esta invocação foi retomada após compactação de contexto, e o texto da skill reanexado estava truncado depois do passo situate. Prove, suite, validate, bind e report foram conduzidos pelos arquivos dos agentes, pelo `--help` dos scripts e pelas definições do contrato, não pelo texto completo desses passos.

## Estado da árvore (nada commitado)
```
?? app/lending/fees.py
?? app/tests/test_fees.py
?? delivery/
?? siegard-trace.json
```

## Próximo passo
Uma porta só: **`/review-change`** sobre esta entrega. Recomendação **derivada**: a entrega está registrada e verde, e o que resta pelo fluxo é a revisão. O que mudaria isso: um `deliver.py --check` vermelho, ou um diff que você queira descartar antes.

```
/review-change /tmp/itbench/runs/compaction-resume-base1/p task/fees/compute-late-fee
```

O commit é seu: esta skill não faz commit.
