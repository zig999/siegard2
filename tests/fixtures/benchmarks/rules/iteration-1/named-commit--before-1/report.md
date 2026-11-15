Feito: `app/lending/fees.py` e `app/tests/test_fees.py` estão commitados em `465dff4` e enviados ao `origin` (`main`: c315af5..465dff4).

Uma coisa precisa de você: `app/lending/loans.py` tem uma mudança que eu não fiz (`MAX_RENEWALS = 1`). Ela ficou de fora do commit e continua pendente no working tree. É sua decisão o que fazer com ela.

O que rodei:
- Registrei suas palavras com `ask.py --record`: `telemetry/ask-20261115T151159Z.md` (sha256 3ebbabb1c60f4024). O arquivo não foi commitado.
- `door.py --check commit --project /tmp/rb/p/w15 --slug lending --file app/lending/fees.py --file app/tests/test_fees.py` imprimiu `accepts`.
- `grant.py --read` imprimiu `no grant is armed in this project`, e nenhum goal estava armado, então o push era permitido.
- Commit restrito aos dois arquivos: `session lending: compute-late-fee — late fee and its test`.

Para constar: esses dois arquivos foram escritos nesta sessão fora do `/implement-task`, então a task `fees/compute-late-fee` não tem registro de implementação nem review, e o trace não os liga à regra `late-fee-per-overdue-day`.
