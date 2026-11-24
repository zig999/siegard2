Implementar primeiro, depois a revisão. Como você pediu para não rodar nada, não consultei o disco: a resposta vem da ordem das rotas, não de um estado verificado.

- Porta recomendada: `/implement-task` para `task/fees/compute-late-fee`, e só depois `/review-change`.
- Critério: a rota que a tabela do framework define para uma mudança com plano é `/plan-work` → `/implement-task` → `/review-change`. A revisão avalia o que a implementação entregou, então revisar antes quebra essa ordem. É uma recomendação derivada de regra, não um julgamento de custo.
- Fato que decide: o plano `lending` guarda a tarefa como ainda não entregue, ou seja, não há entrega para revisar.
- O que reverteria a recomendação: se no disco já existir uma entrega dessa tarefa, por exemplo escrita por outra sessão, o `/implement-task` seria recusado e a revisão passaria a ser a porta certa.

Esse estado "não entregue" é o que a sessão recebeu, não algo que eu conferi agora. Se você quiser, eu rodo `bin/door.py --check implement-task` e `--check review-change` sobre o projeto. Isso confirma qual das duas portas o framework aceita, e eu só rodo com a sua palavra.
