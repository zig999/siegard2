Implemente primeiro: `/implement-task` na tarefa task/fees/compute-late-fee, e só depois a revisão com `/review-change`.

- Critério: a revisão olha o que uma entrega escreveu, e esta tarefa ainda não foi entregue. Antes da implementação não há nada para revisar.
- Fato que decide: o plano `lending` guarda a tarefa como não entregue e nada está pendente na árvore. Esse é o estado que o início desta sessão descreve. Como você pediu para não rodar nada, não o reli do disco.
- O que inverteria a resposta: se a tarefa já tiver sido entregue e faltar só a revisão, a revisão vem primeiro. Dá para conferir com `/siegard-status` ou com `bin/door.py --check` sobre as duas portas, mas só rodo isso se você mandar.

Nada foi executado nesta resposta.
