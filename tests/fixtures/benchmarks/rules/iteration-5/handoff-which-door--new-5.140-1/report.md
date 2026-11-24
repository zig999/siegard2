Implemente primeiro. A revisão só existe depois de uma entrega, e esta tarefa ainda não tem nenhuma.

O que li no disco (sem rodar nada, como você pediu):
- O plano `lending` tem a tarefa `task/fees/compute-late-fee`, que implementa a regra `late-fee-per-overdue-day`, e não há pasta `delivery/` nem registro de entrega.
- `app/lending/loans.py` só tem o `Loan`; nenhuma função de multa por atraso foi escrita ainda.
- A revisão (`/review-change`) examina o que uma entrega escreveu. Sem entrega, não há o que revisar.

Recomendação: `/implement-task` sobre `task/fees/compute-late-fee`, e `/review-change` depois dela.
- Tipo: derivada, porque o que decide é um fato no disco (nenhuma entrega existe).
- O que mudaria isso: se existir uma entrega dessa tarefa que eu não vi (por exemplo, em outra pasta ou branch).

Ressalva: não rodei `bin/door.py --check` para confirmar que cada entrada aceita ou recusa, porque você pediu que nada rodasse. Se quiser a confirmação mecânica antes de seguir, diga e eu rodo só essa checagem. Para implementar, basta você dizer para prosseguir.
