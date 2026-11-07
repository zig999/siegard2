# /implement-task — task/fees/compute-late-fee

Projeto: `/tmp/it3/runs/first-delivery/p` · target `app` · iniciativa `lending`

## Entradas decididas, não perguntadas

- Target `app`: `siegard.json` declara um único target em `targets`, então ele é o target (decidido e informado).
- Iniciativa `lending`: `work_root` tem exatamente uma iniciativa, sem `closure.md` (decidido e informado).
- A raiz de entrega `delivery/lending` não existia e foi criada vazia, como a skill prevê.

## Registros escritos

- `implementation/fees/compute-late-fee` — `delivery/lending/implementation/fees/compute-late-fee.md`, pin `sha256:bda5756edd429a0464359e80ad3eec79554b37e091bcd3e35993911991d028a4`
- `proof/fees/compute-late-fee` — `delivery/lending/proof/fees/compute-late-fee.md`, pin `sha256:109d14cf27bc14e3dcf79bdf23d559b925788c5afb20314e12b8492b698aa631`

Primeira entrega, não é uma re-entrega.

## Caminhos que a entrega criou ou alterou (relativos a `app/`)

- `lending/fees.py` — criado; `late_fee_cents(loan)` responde 0 para um empréstimo devolvido até o vencimento e 100 centavos por dia corrido entre o vencimento e a devolução caso contrário.
- `tests/test_fees.py` — criado; quatro testes.

`deliver.py --unrecorded` confirmou que esses dois caminhos são tudo o que a entrega mudou sob `app/`.

## Critérios registrados como não atendidos

Nenhum. Os dois critérios estão `met: true` no registro de implementação.

## Inferências e divergências registradas

Inferências (implementação):

1. A taxa é um `int` em centavos, então BRL 1,00 por dia é a constante 100 — de: o objetivo e os critérios da task falam em centavos, e a regra PY-01 do standard exige dinheiro em centavos inteiros.
2. A função recebe o registro `Loan` existente e lê `due_on` e `returned_on` dele, em vez de receber duas datas — de: o `must_not_duplicate` do inventário nomeia o registro Loan e suas datas em `lending/loans.py`, e o objetivo fala em "um empréstimo devolvido".
3. Um empréstimo sem `returned_on` está fora do domínio da função e não é respondido; nenhuma guarda ou erro foi adicionado — de: o objetivo da task fala apenas de empréstimo devolvido, e nenhum nó cataloga um erro para o não devolvido.

Divergências: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre

- `rules/lending/late-fee-per-overdue-day` — nenhum teste o nomeia em `demonstrates`. O `untested` da prova diz: o fato vale para um número ilimitado de dias de atraso, então nenhum teste finito o decide por inteiro; os testes dos critérios o seguram no primeiro dia de atraso e numa devolução de vários dias atravessando o fim do mês.

## O que a prova deixou sem prova, casos descartados e discordâncias

Sem prova (`untested`):

- o fato inteiro de `rules/lending/late-fee-per-overdue-day`, como acima;
- o que `late_fee_cents` responde para um empréstimo sem `returned_on` (inferência de comportamento da implementação; nenhum nó decide).

Casos de borda descartados (`not_applicable`):

- duas computações sobre o mesmo empréstimo ao mesmo tempo — a função lê um registro imutável e não guarda estado;
- uma dependência que falha ou demora — a função não chama dependência;
- coleção vazia ou duplicata — a função recebe um empréstimo e nada afirma unicidade;
- data de devolução anterior à data de empréstimo — nenhuma obrigação diz o que esse empréstimo responde.

Discordâncias (`contested`): nenhuma.

## Adiado e preservado

Adiado: `Loan` em `lending/loans.py` não tem o atributo `late_fee`, embora `domain/lending/loan` declare um, do tipo decimal — a task pede uma função que responda a taxa, não que ela seja guardada no empréstimo, e `domain/lending/loan` não é nó que esta task implementa.

Preservado: nada; a entrega não alterou código existente.

## Trace

- `rules/lending/late-fee-per-overdue-day` ligado a `lending/fees.py`, gravado em `siegard-trace.json` na raiz do projeto.
- Nenhuma ligação recusada. Nenhum recibo de ligações desatualizadas foi impresso, então não há invocação de `/reconcile` a entregar.

## Passos executados inline

Os passos 3 (implementação) e 5 (prova) rodaram inline nesta sessão, aplicando `agents/task-implementer.md` e `agents/test-author.md`, porque esta sessão não pode criar subagentes. Por isso os testes foram escritos no mesmo contexto que escreveu o código; os dois registros dizem isso em `## Notes`.

## Saída final do validador (verbatim)

```
derived /tmp/it3/runs/first-delivery/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

## Standard seguido

- Resolvido pelo arquivo do projeto: a linha `standard:` de `project.py` (`siegard.json`), sem nomeação na invocação.
- Caminho `app/standard.yaml` (`standard.yaml` relativo ao target), pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- Nenhuma divergência declarada contra ele.
- Não pressupõe nada; `app/` tem tudo de que precisa.
- `--outstanding` não imprimiu nenhuma linha sobre registros sem standard ou com outro standard.

## Execuções capturadas

- `delivery/lending/run/fees-compute-late-fee-build` — passed (build).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (build, test; 5 passed).
- Setup não rodou: o registro não declara nenhum passo com papel `install`.
- Nenhuma execução falhou.

## Dependências instaladas

Nenhuma. O registro autoriza 0 dependências diretas.

## O que `/review-change` ainda faz

Roda os mesmos passos sobre a mudança inteira, não sobre uma task, e julga se os testes provam os critérios, se o código diz só o que a especificação contém, se segue o standard (inclusive a regra PY-01, decidida por leitura) e por que algo falhou. Uma suíte verde aqui cobre uma task.

## Próximo passo

`/review-change` hoje recusa: `git status --porcelain -- /tmp/it3/runs/first-delivery/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make`. A entrega precisa ser commitada primeiro; commitar é decisão sua, e esta skill não commita.

Caminhos a commitar: `app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`.

Recomendado (derivado): commitar esses caminhos e então rodar `/review-change`. Por quê: a única porta de revisão recusa enquanto `delivery/lending` está pendente. Mudaria se: `delivery/lending` já estiver commitado, e então `/review-change` roda direto.

`/reconcile` não se aplica: o bind não imprimiu recibo de ligações desatualizadas.

```
/review-change project /tmp/it3/runs/first-delivery/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard standard.yaml
```
