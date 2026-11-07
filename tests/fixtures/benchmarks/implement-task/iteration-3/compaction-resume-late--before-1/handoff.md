# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos
- Implementação: `delivery/lending/implementation/fees/compute-late-fee.md`
- Prova: `delivery/lending/proof/fees/compute-late-fee.md`
- Primeira entrega (não é re-entrega): `--outstanding` não encontrou registro no caminho da task.

## Caminhos que a entrega criou, modificou ou removeu (relativos à raiz do alvo `app`)
- `lending/fees.py` (criado) — `files` da implementação
- `tests/test_fees.py` (criado) — `tests` da prova

`deliver.py --unrecorded app <implementação> <prova>` saiu 0: "Every path this tree changed under app is named by the 2 record(s) given". Fora do alvo, a entrega escreveu `delivery/lending/` e o vínculo de rastreio `siegard-trace.json` na raiz do projeto.

## Critérios registrados como não atendidos
Nenhum. Os dois critérios estão `met: true`.

## Inferências e desvios registrados
- Inferência: "a loan not yet returned is refused with a ValueError rather than answered a fee." — de: "the rule states the fee of a loan returned after its due date and states nothing of a loan still out".
- Desvios contra o padrão: nenhum declarado em nenhum dos registros.

## Nós sem teste que os demonstre
Nenhum. `rules/lending/late-fee-per-overdue-day` é demonstrado por `tests/test_fees.py::test_each_further_calendar_day_after_the_due_date_adds_100_cents`.

## Não provado, casos descartados, discordâncias
A prova não registra nada não provado, nenhum caso de borda descartado e nenhuma discordância. A inferência acima (empréstimo ainda não devolvido recusado com ValueError) não tem teste na prova.

## Adiado / o que deve continuar funcionando
A implementação não registra nada adiado nem nada que deva continuar funcionando (Notes: "None.").

## Rastreio
`trace.py --bind-record app spec delivery/lending/implementation/fees/compute-late-fee.md` saiu 0:
```
bound rules/lending/late-fee-per-overdue-day to 1 file(s)
1 binding(s) written at /tmp/it3/runs/compaction-resume-late--before-1/p/siegard-trace.json, read from compute-late-fee.md
```
Nenhum vínculo recusado. Nenhum recibo de vínculos desatualizados foi impresso, então não há `/reconcile` a entregar por esta entrega.

## Passos executados inline
Esta sessão não pode criar subagentes. Os passos 3 (implementar, disciplina de `agents/task-implementer.md`) e 5 (provar, disciplina de `agents/test-author.md`) rodaram inline, nesta mesma sessão — portanto o código e os testes foram escritos no mesmo contexto; a revisão deve lê-los sabendo disso. A sessão foi compactada após o passo 6 e retomada no passo 7.

## Validação final (verbatim)
`deliver.py delivery/lending work/lending app spec` saiu 0:
```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido
- Resolvido do arquivo de projeto: `siegard.json` → `standard: app/standard.yaml` (`lending-app`), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`, gravado como `standard.yaml` em ambos os registros.
- Desvios divulgados: nenhum.
- Pressupostos: o registro não declara nenhum; a task não declara `produces`, e `deliver.py --standard` (com `--against app`) passou limpo.
- `--outstanding` não imprimiu registros sem padrão, com outro padrão ou com versão anterior.

## Execuções capturadas
- `delivery/lending/run/fees-compute-late-fee-build` — passed (build: `python3 -m compileall -q lending`, timeout 60 s), primeira tentativa.
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (build, depois test: `python3 -m pytest -q tests`, timeout 120 s), primeira tentativa.
- Setup não rodou: o registro não declara passo com papel `install`.
- Nenhuma suíte vermelha, nenhum diagnóstico.

## Dependências instaladas
Nenhuma.

## O que `/review-change` ainda faz
Roda os mesmos passos sobre a mudança inteira, não sobre uma task, e julga se os testes provam os critérios, se o código afirma só o que a especificação contém, se segue o padrão (PY-01, PY-02) e por que algo falhou. Uma suíte verde aqui cobre uma task.

## Encaminhamento
A revisão hoje recusa: `git status --porcelain -- /tmp/it3/runs/compaction-resume-late--before-1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make`. Ela roda depois que você fizer o commit desta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`). O commit é seu; esta skill não faz commit.

`/review-change` invocation ready to paste:
```
/review-change project root /tmp/it3/runs/compaction-resume-late--before-1/p, target app, slug lending, tasks task/fees/compute-late-fee, files app/lending/fees.py app/tests/test_fees.py, standard app/standard.yaml
```
