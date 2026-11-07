# /implement-task — task/fees/compute-late-fee

Projeto: `/tmp/itbench2/runs/first-delivery-prior1/p` · alvo `app` · iniciativa `lending`.

Entradas decididas e divulgadas, nunca perguntadas:
- **alvo `app`**: `siegard.json` declara exatamente uma chave em `targets`.
- **iniciativa `lending`**: o `work_root` (`work/`) contém exatamente uma iniciativa, sem `closure.md`.
- **padrão**: `app/standard.yaml`, resolvido pelo campo `standard` de `siegard.json` (a invocação não nomeou nenhum).
- A raiz de entrega `delivery/lending` não existia e foi criada vazia, como a skill prevê.

## Nós escritos

- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md` (pin `sha256:96a44463d9fad457adecca1f00e17cbce34f7216c9f4c67595d16b7dceb89b2c`)
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md` (pin `sha256:bbfa8c788c87bea3879374fccdc923db7b8815c39bf6586add08aa37c829f679`)

Primeira entrega, não uma re-entrega.

## Caminhos criados, modificados ou removidos (relativos à raiz do alvo `app`)

- `lending/fees.py` — criado (registro de implementação, `files`)
- `tests/test_fees.py` — criado (registro de prova, `tests`)

`deliver.py --unrecorded` confirmou: `every path this tree changed under app is named by the 2 record(s) given`.

Fora do alvo, também pendentes no git: `delivery/lending/` (registros, runs, `delivery.json`) e `siegard-trace.json` (o vínculo do trace).

## Critérios registrados como não atendidos

Nenhum. Os dois critérios estão `met: true`.

## Inferências e divergências

Inferências do registro de implementação:
1. Um empréstimo sem `returned_on` é recusado com `ValueError` em vez de receber uma multa — inferido de: o objetivo da tarefa é enunciado sobre um empréstimo devolvido, e nenhum nó diz qual é a multa de um empréstimo não devolvido.
2. A multa é respondida por uma função de módulo sobre o registro `Loan` existente, não por um método dele — inferido da convenção do inventário (registro de domínio é dataclass congelada com campos tipados, vista em `lending/loans.py`) e da entrada `must_not_duplicate` sobre `Loan`.

Divergências: nenhuma, em nenhum dos dois registros.

## Nós que a tarefa implementa sem teste que os demonstre

Nenhum. `rules/lending/late-fee-per-overdue-day` é reivindicado em `demonstrates` pelo teste `test_a_late_loan_carries_100_cents_for_each_calendar_day_across_a_month_end` (a reivindicação é auditada pela revisão, não se auto-certifica).

## O que a prova deixou sem provar, casos de borda descartados e discordâncias

- `untested`: a recusa de um empréstimo sem `returned_on`, que a implementação registrou como inferência — nenhum nó diz qual é a multa de um empréstimo não devolvido, então o comportamento fica sem fixar.
- `not_applicable`:
  - duas computações da multa sobre o mesmo empréstimo ao mesmo tempo — a computação lê um registro imutável e não escreve nada; nenhum nó fala de concorrência;
  - dependência que falha ou responde devagar — a computação não chama dependência;
  - data de devolução muito distante ou atraso muito longo — nenhum nó estabelece teto ou limite, então não há fronteira além do primeiro dia de atraso.
- `contested`: nenhuma discordância.

## Adiado e preservado

- Adiado: `domain/lending/loan` declara o atributo `late_fee` que o registro `Loan` em `lending/loans.py` não carrega — o objetivo da tarefa é o cálculo da multa, e guardá-la no empréstimo vai além dele.
- Preservado: nada listado; a tarefa não alterou código existente (só criou `lending/fees.py`).

## Trace

- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` (1 vínculo, em `/tmp/itbench2/runs/first-delivery-prior1/p/siegard-trace.json`).
- Nenhum vínculo recusado.
- Nenhum recibo de vínculos obsoletos (stale-bindings) foi impresso; portanto não há invocação de `/reconcile` a entregar.

## Passos executados inline

Os passos 3 (implementar) e 5 (provar) rodaram inline nesta sessão, que não pode criar subagentes: `agents/task-implementer.md` e `agents/test-author.md` foram lidos e aplicados em sequência. Consequência: a fonte e os testes foram escritos no mesmo contexto — a separação entre os dois produtores, que é o ponto do arranjo, não existiu nesta entrega. Ambos os registros dizem isso em `## Notes`.

## Recomendação

O próximo passo derivado é: você faz o commit desta entrega e depois roda `/review-change`.
- Critério: derivado — uma porta que o próprio ponto de entrada recusa como a árvore está.
- Fato decisivo: `door.py --check` respondeu que `/review-change` recusa: `git status --porcelain -- /tmp/itbench2/runs/first-delivery-prior1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make`.
- Fato que reverteria: `delivery/lending` sem mudanças pendentes no git (isto é, já commitado).
- `/reconcile` fica excluído: nenhum vínculo ficou obsoleto, então não há conjunto de arquivos a reconciliar.

Esta skill não faz commit nem muda o estado do git; o commit é seu.

## Saída final do validador (verbatim)

```
derived delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Padrão seguido

- `app/standard.yaml` (relativo ao alvo: `standard.yaml`), resolvido de `siegard.json`, pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- 2 regras: `PY-01` (dinheiro em centavos inteiros, decidida por leitura) e `PY-02` (todo módulo compila, decidida pela ferramenta no passo `build`).
- Nenhuma divergência declarada contra o padrão por nenhum dos registros.
- Pressupõe nada: `it presupposes nothing, so app holds everything it needs to`.
- `--outstanding` não imprimiu linha alguma sobre registros que fixam outro padrão, nenhum padrão ou uma versão anterior.

## Runs capturados

- `delivery/lending/run/fees-compute-late-fee-build` — `passed` (passo `build`: `python3 -m compileall -q lending`).
- `delivery/lending/run/fees-compute-late-fee-suite` — `passed` (`build`, depois `test`: `python3 -m pytest -q tests` → `5 passed`).
- Nenhum run vermelho.
- Não rodou: a fase `setup` — o registro não declara passo com papel `install` (`setup: nothing runs — no step carries the role this phase needs`).

## Dependências instaladas

Nenhuma. O padrão autoriza 0 dependências diretas e a entrega não adicionou nenhuma.

## O que `/review-change` ainda faz

Roda de novo os mesmos passos sobre a mudança inteira, não sobre uma tarefa, e julga: se os testes provam os critérios, se a fonte afirma só o que a especificação contém, se segue o mesmo padrão (incluindo `PY-01`, decidida por leitura), e por que algo falhou. Uma suíte verde aqui é verde sobre uma tarefa. Também é ela que audita a reivindicação `demonstrates` do teste sobre `rules/lending/late-fee-per-overdue-day`.

## Handoff

Depois do commit de `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/` e `siegard-trace.json`:

```
/review-change /tmp/itbench2/runs/first-delivery-prior1/p --target app --slug lending --tasks task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard app/standard.yaml
```

---

# Handoff entregue à pessoa (saída de handoff.py --render, verbatim)

```
lending · task 1/1 delivered · phase review
```

1. A multa por atraso está escrita e testada; falta o seu commit para a revisão rodar.
   - **Recomendado** `a`: Commitar esta entrega e depois rodar a revisão. A revisão recusa enquanto a pasta de entrega tem mudanças pendentes, e esta skill não commita. Mudaria se a pasta de entrega já estiver commitada.
   - `b`: Revisar agora: excluída, recusa sem o commit.
   - `c`: Reconciliar: excluída, nenhum vínculo ficou desatualizado.
   - Se nenhuma for tomada: Tudo fica no disco sem commit e sem revisão.

   ```
   /review-change /tmp/itbench2/runs/first-delivery-prior1/p --target app --slug lending --tasks task/fees/compute-late-fee --files lending/fees.py tests/test_fees.py --standard app/standard.yaml
   ```

Relatório completo: /tmp/itbench2/runs/first-delivery-prior1/p/.git/siegard/handoff/20261107T144750Z-implement-task.md
