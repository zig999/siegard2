Feito: commit `6b5825b` com apenas `app/lending/fees.py` e `app/tests/test_fees.py`, enviado para `origin/main` (`c315af5..6b5825b`).

Ficou de fora, de propósito:
- `app/lending/loans.py` — tem uma alteração que eu não fiz; não entrou no commit e continua pendente na árvore.
- `telemetry/ask-20261115T151141Z.md` — o registro da sua mensagem (sha256 `3ebbabb1c60f4024`), citado no corpo do commit; está sem commit.

Para registro: esses dois arquivos foram escritos nesta sessão fora do fluxo do plano. O plano `lending` tem a tarefa `task/fees/compute-late-fee` para exatamente isso, e ela continua sem registro de implementação nem vínculo no trace.
