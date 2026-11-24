Implementar primeiro. A revisão vem depois da implementação, porque a tarefa task/fees/compute-late-fee ainda não foi entregue e não há nada para revisar.

Isso é uma recomendação por julgamento, não verificada no disco. Como você pediu para não rodar nada, não consultei o estado do projeto nem rodei `bin/door.py --check`. Os dados vêm do que me foi dito ao começar: a tarefa está no plano `lending`, ainda não entregue, e não há nada pendente na árvore.

- Porta recomendada: `/implement-task` sobre task/fees/compute-late-fee.
- Critério: julgamento, o critério que mantém a rota do framework. A rota é `/plan-work` → `/implement-task` → `/review-change`, e a revisão vem por último.
- Fato que decidiria: nenhum fato em disco decide isto ainda. Falta confirmar que o `/implement-task` aceita a tarefa e que o `/review-change` a recusa por falta de entrega.
- O que inverteria: se o `bin/door.py --check` aceitasse o `/review-change` sobre essa tarefa, ou se o `/implement-task` a recusasse, a recomendação mudaria.

Se quiser que eu confirme, digo que rodo `bin/door.py --check implement-task` e `bin/door.py --check review-change` sobre o projeto e a tarefa e lhe trago o resultado. Só rodo depois do seu aval.
