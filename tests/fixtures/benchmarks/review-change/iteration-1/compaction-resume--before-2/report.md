# /review-change — fees-review (initiative `lending`, target `app`)

## O que foi revisado

- Tarefa: `task/fees/compute-late-fee`
- Arquivos (relativos a `app`): `lending/fees.py`, `tests/test_fees.py`
- Raízes, de `siegard.json` (a invocação não nomeou nenhuma): specification_root `spec`, target `app`, work_root `work`, delivery_root `delivery`.
- Standard: `app/standard.yaml`, respondido pelo arquivo `siegard.json` (a invocação não nomeou nenhum); pin `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`.

## Checks executados (saída literal)

```
plan checked: work/lending/plan.json matches 3 node(s)
delivery checked: delivery/lending/delivery.json matches 2 node(s)
```

Ambos exit 0. `git status --porcelain -- delivery/lending` não imprimiu nada antes da escrita.

`deliver.py --standard app/standard.yaml --against app --specification spec`: limpo — PY-01 decidida por leitura, PY-02 pelo step `build`; steps `build` e `test` declarados; nada ausente.

## Trace

`trace.py --check app`:

```
no drift: 1 binding(s) match the specification and the code as both stand now
```

Nenhum recibo de supressão. Isto não é finding nem stop.

## Run capturado

`run/fees-review`, com os steps do registry `build` (`python3 -m compileall -q lending`) e `test` (`python3 -m pytest -q tests`), cwd `app`: outcome **passed**.

## Passes

Nenhum agente do plugin estava registrado na sessão: todo spawn falhou, e os passes **coverage, conformance e standard rodaram inline**. O passe **failures não rodou**: o run capturado passou, então não havia falha a diagnosticar (registrado como `missing`).

### coverage (inline)

| Critério (citado da tarefa) | Estado | Testes |
|---|---|---|
| A loan returned on or before its due date carries a late fee of 0 cents. | covered | `test_a_loan_returned_on_its_due_date_carries_no_late_fee`, `test_a_loan_returned_before_its_due_date_carries_no_late_fee` |
| A loan returned after its due date carries 100 cents for each calendar day between its due date and its return. | partial | `test_each_further_calendar_day_after_the_due_date_adds_100_cents` |

Por que `partial`: "The fee of a loan returned exactly one calendar day after its due date is held to a range of 0 to 100 cents, not to 100 cents, so the first day of lateness is unexercised."

`unpaired`: nenhum teste sem critério.

### conformance (inline, staged por `trace.py --stage --review`, 2 arquivos, 1 nó, 1 wave, sem certificação)

Registro: `siegard-reconcile/fees-review.md` (fold aceito por `trace.py --reconciliation`).

- `rules/lending/late-fee-per-overdue-day`: conforms — mantido em `late_fee_cents` (`return overdue_days * LATE_FEE_CENTS_PER_DAY`).
- `trace.py --bind-record` imprimiu: `bound rules/lending/late-fee-per-overdue-day to 1 file(s)`.
- `tests/test_fees.py`: sem nó vinculado (`unbound`); o nó do plano foi lido e não está lá (`nowhere`).

Finding (1, kind `unstated`):
- `lending/fees.py`, `late_fee_cents`, o branch sobre `overdue_days`
  - evidência: `if overdue_days <= 0:` / `return 0`
  - custo: "The fee of a loan returned on or before its due date is decided in code and in no node, so a change to it answers to no rule a reader can open."

### standard (inline, sobre `deliver.py --standard app/standard.yaml --reading --for lending/fees.py --for tests/test_fees.py`)

Em escopo: PY-01. Nenhum finding. Deixado de lado: "The tests' date arithmetic, which no rule in scope names."

### failures

Não rodou: o run `run/fees-review` passou.

## Registro e validação

Escrito: `delivery/lending/review/fees-review.md`.

```
review/fees-review: sound on its own. Cross-node checks and plan checks did not run; they run on the whole delivery.
```

```
derived delivery/lending/delivery.json: 3 node(s), 4 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof, 1 review; 1 of 1 task(s) hold a record; 0 criterion(s) recorded unmet; 1 recorded unproven; 1 finding(s)
```

```
delivery checked: delivery/lending/delivery.json matches 3 node(s)
```

`deliver.py --findings`:

```
fees-review.md: 1 finding(s) over 2 reviewed file(s)
  by pass: conformance 1
  conformance by kind: unstated 1
  standard by rule cited: none
  failures by cause: none
  by file: lending/fees.py 1
```

Todos exit 0.

## Handoff

Isto é evidência, não um veredito. O que ela significa para a mudança cabe a você decidir.

O que a revisão deixou no disco, sem commit (nenhum commit foi feito):
- `delivery/lending/review/fees-review.md` (novo)
- `delivery/lending/delivery.json` (derivado de novo)
- `delivery/lending/run/fees-review/` (run capturado)
- `siegard-reconcile/fees-review.md` e `siegard-reconcile/fees-review.returns/` (reconciliação)
- `siegard-trace.json` (restampado pelo `--bind-record`)

Caminhos:
1. **Commit do registro da revisão**, com pathspec restrito aos cinco caminhos acima. **Recomendado (derivado):** os checks passaram, o validador aceitou o registro, e a revisão em si está terminada. O que mudaria isso: você discordar do registro como está escrito. Nesse caso ele é reescrito antes do commit.
2. **O fato `unstated`** (taxa 0 para devolução na data de vencimento ou antes dela, decidida só em `lending/fees.py`). A rota é `/analyse`, que daria a esse fato um nó.
3. **O critério `partial`** (o primeiro dia de atraso não é fixado em 100 cents). O registro de prova já diz que nenhum nó decide se o dia final conta. Fixar isso num teste fixaria a inferência da implementação. O que decide é a especificação ganhar essa declaração: via `/analyse`, e depois uma nova prova.

Os caminhos 2 e 3 envolvem o valor de um finding. Isso é seu, e não recomendo um sobre o outro. O que decide cada um: se você quer que a regra de dias corridos e a fronteira de zero sejam fatos da especificação (então `/analyse`) ou se aceita que fiquem como inferência registrada no código e na prova (então nada a fazer).
