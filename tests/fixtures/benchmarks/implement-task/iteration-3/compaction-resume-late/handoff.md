# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Registros escritos

- Implementação: `delivery/lending/implementation/fees/compute-late-fee.md` (task/fees/compute-late-fee)
- Prova: `delivery/lending/proof/fees/compute-late-fee.md` (task/fees/compute-late-fee)
- Não é uma re-entrega: nenhum registro existia no caminho da tarefa quando `--outstanding` rodou.

## Caminhos criados, modificados ou removidos (o conjunto de arquivos da revisão)

Sob a raiz de origem do alvo `app` (`--unrecorded` os conferiu contra a árvore, saída 0):

- `app/lending/fees.py` — criado (implementação, `files`)
- `app/tests/test_fees.py` — criado (prova, `tests`)

Fora do alvo, escritos por esta entrega: a raiz de entrega `delivery/lending/` (os dois registros, `delivery.json` derivado, `run/fees-compute-late-fee-build/`, `run/fees-compute-late-fee-suite/`) e `siegard-trace.json` na raiz do projeto.

## Critérios registrados como não atendidos

Nenhum. Os dois critérios da tarefa estão registrados `met: true`:

- «A loan returned on or before its due date carries a late fee of 0 cents.» — `late_fee_cents()` limita a 0 uma contagem de dias não positiva antes de multiplicar.
- «A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.» — `late_fee_cents()` multiplica os dias corridos entre `due_on` e `returned_on` por `CENTS_PER_OVERDUE_DAY`, que é 100.

## Inferências e desvios registrados

- Inferência (implementação): «a loan not yet returned is refused with a ValueError rather than answered a fee.» — de: «the rule states the fee of a loan returned after its due date and states nothing of a loan still out». Um revisor lê isto primeiro: é uma decisão que ninguém pediu.
- Desvios contra o padrão: nenhum registro declarou algum.

## Nós sem teste que os demonstre

Nenhum. A tarefa implementa um nó, `rules/lending/late-fee-per-overdue-day`, e o teste `test_each_further_calendar_day_after_the_due_date_adds_100_cents` em `tests/test_fees.py` o nomeia em `demonstrates`. A prova não declara `untested`.

## O que a prova deixou sem provar, casos de borda descartados, discordâncias

Nada registrado: a prova não declara `unproven`, casos de borda descartados nem discordâncias, e suas notas dizem «None.». Observação: a inferência acima (empréstimo ainda não devolvido recusado com `ValueError`) não tem teste que a sustente na prova; ela não é critério da tarefa nem fato de nó.

## O que a implementação adiou e o que deve continuar funcionando

Nada registrado: a implementação não declara adiamentos nem o que deve continuar funcionando, e suas notas dizem «None.».

## Rastro

- Vinculado: `rules/lending/late-fee-per-overdue-day` a 1 arquivo (`lending/fees.py`), escrito em `siegard-trace.json`.
- Nenhuma vinculação recusada.
- O vínculo não imprimiu recibo de vinculações obsoletas; não há invocação de `/reconcile` devida por esta entrega.

## Passos executados em linha

Esta sessão não pode gerar subagentes. Implementar (passo 3) e Provar (passo 5) rodaram em linha, na mesma sessão, aplicando a disciplina de `agents/task-implementer.md` e de `agents/test-author.md` respectivamente. Por isso os testes foram escritos no mesmo contexto que escreveu o código — a separação que os dois produtores garantem não vale aqui, e a revisão é quem a recupera.

## Saída final do validador, verbatim

```
every path this tree changed under app is named by the 2 record(s) given
```

```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido

- Resolvido do arquivo de projeto: `siegard.json` declara `standard: app/standard.yaml`.
- Caminho relativo ao alvo: `standard.yaml`; pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6` (o mesmo nos dois registros).
- Desvios declarados contra ele: nenhum.
- Pressupõe: nada que esta tarefa produza — a tarefa não declara `produces`, e a verificação do padrão contra a árvore passou limpa.
- `--outstanding` não listou registros sem padrão, com outro padrão ou com versão anterior dele.

## Execuções capturadas

- `delivery/lending/run/fees-compute-late-fee-build` — passou (passo `build`: `python3 -m compileall -q lending`, saída 0; timeout 60 s).
- `delivery/lending/run/fees-compute-late-fee-suite` — passou na primeira tentativa (`build` e depois `test`: `python3 -m pytest -q tests`, ambos saída 0; timeout 120 s).
- Nenhuma execução falhou; nenhuma suíte vermelha foi diagnosticada.
- Passo do registro que não rodou: set up — o registro não declara nenhum comando de papel `install`.

## Dependências instaladas

Nenhuma: não há passo de instalação e nenhum manifesto foi alterado.

## O que `/review-change` ainda faz

Roda os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga se os testes provam os critérios, se o código afirma só o que a especificação contém, se segue o padrão (incluindo PY-01, dinheiro em centavos inteiros, decidido por leitura) e por que algo falhou. Uma suíte verde aqui cobre uma tarefa. Neste caso ela também lê de novo o que foi escrito em linha, num contexto que não o escreveu.

## Próximo passo

`/review-change` hoje recusa: «git status --porcelain -- /tmp/it3/runs2/compaction-resume-late/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make». A revisão só roda depois que a pessoa fizer o commit desta entrega — os caminhos `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/` e `siegard-trace.json`. Fazer o commit é da pessoa; esta invocação não muda o estado do git.

Recomendado (derivado): fazer o commit da entrega e então rodar a revisão. Por quê: a própria revisão recusa enquanto a raiz de entrega tem mudanças pendentes. Mudaria se: a raiz de entrega já estiver limpa no git quando a pessoa for revisar. `/reconcile` fica excluído: o vínculo não imprimiu recibo de vinculações obsoletas, então não há nada para ele restaurar.

Invocação pronta para colar, depois do commit:

```
/review-change /tmp/it3/runs2/compaction-resume-late/p target app slug lending task task/fees/compute-late-fee files app/lending/fees.py app/tests/test_fees.py standard app/standard.yaml
```
