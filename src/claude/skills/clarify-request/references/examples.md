# Examples

Each instruction below, in the fence that follows an `instruction` comment, is held to the contract by `bin/clarify.py`; the comment is the test's marker and is not part of an instruction. The requests are
shown in the language they were made in; every instruction is in English.

## 1. A read-only request that leans on references

```text
Olha essa implementação e vê se ela está seguindo o standard que a gente definiu. Não altera nada ainda.
```

The reference "essa implementação" resolves from the conversation or the open file; "o standard"
resolves from the project. Neither is asked.

<!-- instruction -->
```
MODE: ANALYZE
TASK: Validate the implementation in src/billing/invoice.py against the project's standard.
SCOPE:
- src/billing/invoice.py and the tests that exercise it.
CONSTRAINTS:
- Do not modify code.
ASSUMPTIONS:
- "essa implementação" is src/billing/invoice.py: the file open in the session when requested.
- "o standard" is standards/backend.md: the only standard document under standards/.
DISCOVERY:
- Identify which rules of standards/backend.md apply to the target.
OUTPUT:
For each non-conformity: rule, file, line, current behavior, expected behavior, recommended correction.
If there is none, say so and name the evidence read.
```

## 2. A change request the project answers

```text
Precisamos guardar o histórico das mudanças de status do pedido.
```

"Guardar" does not name a storage mechanism, and the project has one: not asked, delegated. The
request asks for no verification, so the mode is the one that authorizes the change and no more.

<!-- instruction -->
```
MODE: IMPLEMENT
TASK: Implement persistence of the status-change history of an order.
CONSTRAINTS:
- Do not change existing persistence behavior outside the status history.
DISCOVERY:
- Find how the project persists history or audit data elsewhere, and follow that pattern.
```

## 3. A blocking, asked

```text
Remove os clientes inativos do sistema.
```

The project holds orders referencing customers: deleting changes history, a data-model and
irreversible effect the request does not settle. All three tests hold, so one question is asked.

```text
Question: How should an inactive customer be removed when orders reference it?
Why it matters: Orders reference customers; the choice decides whether purchase history survives.

1. Soft delete (Recommended) — mark inactive customers removed and keep every row.
   Recommended by the project: src/orders/models.py already soft-deletes products.
2. Block removal while orders exist — reject, and remove only customers with none.
3. Cascade delete — delete the customers and their orders. Irreversible.
```

The answer, "Soft delete", enters the instruction as a requirement:

<!-- instruction -->
```
MODE: IMPLEMENT
TASK: Remove inactive customers from the system.
SCOPE:
- Customer removal only.
REQUIREMENTS:
- Remove by soft delete: mark the customer removed and keep the row and its relationships.
- Apply the removal to the existing data, not only to the code.
CONSTRAINTS:
- Do not delete rows.
- Do not modify orders.
DISCOVERY:
- Find the existing soft-delete mechanism and follow it.
```

## 4. A request that is already one operation

Running an existing suite only observes, so it is within the mode that modifies nothing.

```text
Roda a suíte de testes de src/auth e me diz o que falhou.
```

Nothing to resolve and nothing to ask: the mode, the target and the output are stated. Running an
existing suite only observes, so it sits within the mode that modifies nothing.

<!-- instruction -->
```
MODE: ANALYZE
TASK: Run the test suite of src/auth and report the failures.
CONSTRAINTS:
- Do not modify code.
```

## 5. A plan, not a change

```text
Como a gente poderia expor o relatório mensal por API? Só quero o plano.
```

<!-- instruction -->
```
MODE: PLAN
TASK: Propose how to expose the monthly report through the project's API.
CONSTRAINTS:
- Do not modify the project.
DISCOVERY:
- Find how the report is produced today and how the project exposes comparable resources.
OUTPUT:
A plan stating the interface, the changes it needs, and the decisions that remain the operator's.
```

## 6. A call that changes state is not a look

```text
Usa essa chave pra chamar o POST /pay do gateway local com valor 1 e ver se responde 200.
```

The call creates a charge on the endpoint it reaches, so it is not observation, and the credential
is a secret that does not enter the instruction.

<!-- instruction -->
```
MODE: OPERATE
TASK: Send one POST request with amount 1 to the /pay endpoint of the local gateway and report whether the response status is 200.
CONSTRAINTS:
- Do not modify the project.
- Send the request to the local gateway only.
- Do not write the credential into any file, log or output.
ASSUMPTIONS:
- The credential is the one the operator gave in the request; it is not reproduced here and the operator supplies it when executing.
DISCOVERY:
- Find the address of the local gateway in the project.
OUTPUT:
The response status code, and whether it is 200.
```
