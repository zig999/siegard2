# /implement-task — task/fees/compute-late-fee (lending, alvo app)

## Entradas e como foram resolvidas

- Tarefa: `task/fees/compute-late-fee`, nomeada na invocação.
- Raiz do projeto: `/tmp/itbench2/runs/first-delivery-new1/p`, nomeada na invocação.
- Alvo: `app` — decidido e divulgado: `siegard.json` declara exatamente um alvo em `targets`.
- Iniciativa: `lending` — decidida e divulgada: `work_root` contém exatamente uma iniciativa, sem `closure.md`.
- A raiz de entrega `delivery/lending` não existia e foi criada vazia (a primeira execução de `deliver.py --outstanding` saiu com 2: "cannot run: delivery root ... is not a directory"; depois de criada, saiu limpa).

## Registros escritos

- `implementation/fees/compute-late-fee` — pin `sha256:d640cac5ee9d1163a64b3341a63980d8b1b104d75b00d22cb8bc081732d836da`
- `proof/fees/compute-late-fee` — pin `sha256:72064c29bf7dc35cd117024d8198c03458f5d312cead2d3b4f59bcf519c829b3`
- Primeira entrega: não é uma re-entrega, e a tarefa não declara `stands` nem `produces`.

## Arquivos criados, modificados ou removidos (raiz do alvo `app`)

- `lending/fees.py` (criado) — `late_fee_cents(loan)` responde 0 para um empréstimo devolvido até a data de vencimento, e 100 centavos por dia de calendário entre o vencimento e a devolução caso contrário.
- `tests/test_fees.py` (criado) — os três testes da prova.

Fora da raiz do alvo: `delivery/lending/` (registros, `delivery.json`, `run/`) e `siegard-trace.json` na raiz do projeto.

## Critérios registrados como não atendidos

Nenhum. Os dois critérios estão registrados `met: true`.

## Inferências e divergências registradas

Inferências (implementação):
1. O número de dias de calendário entre o vencimento e a devolução é `returned_on - due_on` em dias, de modo que um empréstimo devolvido no dia seguinte ao vencimento carrega a taxa de um dia. — de: o enunciado da regra "each calendar day between its due date and its return" e os campos de data do registro `Loan` em `lending/loans.py`.
2. A função recebe o registro `Loan` existente e lê `due_on` e `returned_on`, em vez de receber as duas datas separadamente. — de: o objetivo da tarefa "Given a returned loan" e a entrada `must_not_duplicate` do inventário para o registro `Loan` em `lending/loans.py`.
3. A taxa é um `int` em centavos, BRL 1.00 sendo 100 centavos. — de: os critérios da tarefa em centavos e a regra PY-01 do padrão.

Divergências: nenhuma, em nenhum dos dois registros.

## Nós sem teste que os demonstre

- `rules/lending/late-fee-per-overdue-day` — nenhum teste carrega `demonstrates`. O `untested` da prova diz: "rules/lending/late-fee-per-overdue-day as a whole: the rule's per-day rate is held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the count of calendar days "between its due date and its return" is not stated by the node (whether an end day counts), so no finite test decides the fact whole without pinning the implementation's inference."

## O que a prova deixou sem prova, casos descartados e discordâncias

Sem prova (`untested`):
- A taxa de um empréstimo devolvido exatamente um dia de calendário após o vencimento: a implementação inferiu que um dia de atraso são 100 centavos, e nenhum nó decide se o dia da devolução ou o do vencimento conta; a inferência fica registrada sem prova e nenhum teste a fixa.
- O nó acima, como um todo (ver a seção anterior).

Casos descartados (`not_applicable`):
- um empréstimo sem data de devolução — a tarefa e a regra tratam só de empréstimo devolvido; a implementação adiou esse caso.
- um empréstimo renovado — a renovação só move o vencimento, que a regra já lê.
- dois cálculos sobre o mesmo empréstimo ao mesmo tempo — o cálculo lê um registro imutável e não escreve nada.

Discordâncias (`contested`): nenhuma.

## Adiado, e o que deve continuar funcionando

Adiado:
- Um empréstimo com `returned_on` igual a `None` fica fora do domínio da função, e nenhuma recusa foi escrita para ele — nenhum nó cataloga o que responder nesse caso.
- O atributo `late_fee` (decimal) da entidade `domain/lending/loan` não foi acrescentado ao registro `Loan` em `lending/loans.py` — guardar a taxa no registro vai além do objetivo da tarefa.

Preservado: nada registrado — a tarefa não alterou comportamento existente (só criou arquivos novos).

## Rastreio

- Vinculado: `rules/lending/late-fee-per-overdue-day` → `lending/fees.py` ("bound rules/lending/late-fee-per-overdue-day to 1 file(s)"; "1 binding(s) written at /tmp/itbench2/runs/first-delivery-new1/p/siegard-trace.json, read from compute-late-fee.md").
- Nenhum vínculo recusado. Nenhum recibo de vínculos desatualizados foi impresso, então nenhuma invocação de `/reconcile` é entregue.

## Passos executados em linha

Esta sessão não pode criar subagentes. Os passos 3 (implementar, `task-implementer`) e 5 (provar, `test-author`) rodaram em linha, aplicando os arquivos `agents/task-implementer.md` e `agents/test-author.md`; as duas devoluções foram passadas aos escritores por `--from-text`. Fonte e testes foram escritos no mesmo contexto: a separação que os dois produtores garantem não vale para esta entrega, e a revisão deve ler os testes sabendo disso.

## Saída final do validador

```
derived /tmp/itbench2/runs/first-delivery-new1/p/delivery/lending/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 0 recorded unproven; 0 finding(s)
```

`deliver.py --unrecorded`: "every path this tree changed under /tmp/itbench2/runs/first-delivery-new1/p/app is named by the 2 record(s) given".

## Padrão seguido

- Resolvido pelo arquivo do projeto (`siegard.json`, linha `standard:`): `/tmp/itbench2/runs/first-delivery-new1/p/app/standard.yaml`, registrado como `standard.yaml` relativo ao alvo.
- Pin: `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.
- 2 regras: PY-01 (decidida por leitura), PY-02 (decidida por ferramenta, passo `build`).
- Nenhuma divergência registrada contra ele.
- Pressupõe nada; a árvore contém tudo o que ele precisa.
- `--outstanding` não imprimiu nenhuma linha sobre registros sem padrão ou com outro padrão.

## Execuções capturadas

- `delivery/lending/run/fees-compute-late-fee-build` — passed (`build=python3 -m compileall -q lending`).
- `delivery/lending/run/fees-compute-late-fee-suite` — passed (`build`, depois `test=python3 -m pytest -q tests`: "4 passed").
- Nenhuma execução vermelha.
- Setup não rodou: o registro não declara passo com papel `install`.

## Dependências instaladas

Nenhuma. O registro autoriza 0 dependências diretas.

## O que `/review-change` ainda faz

Roda os mesmos passos sobre a mudança inteira, não uma tarefa, e julga se os testes provam os critérios, se a fonte diz só o que a especificação contém, se segue o padrão (PY-01 por leitura) e por que algo falhou. A suíte verde aqui cobre uma tarefa.

## Próximo passo

`/review-change` hoje recusa: "git status --porcelain -- /tmp/itbench2/runs/first-delivery-new1/p/delivery/lending is not empty — the entry point writes there, and stops on a change it did not make". Primeiro a pessoa commita esta entrega (`app/lending/fees.py`, `app/tests/test_fees.py`, `delivery/lending/`, `siegard-trace.json`); depois:

```
/review-change /tmp/itbench2/runs/first-delivery-new1/p target app slug lending tasks task/fees/compute-late-fee files lending/fees.py tests/test_fees.py standard app/standard.yaml
```
