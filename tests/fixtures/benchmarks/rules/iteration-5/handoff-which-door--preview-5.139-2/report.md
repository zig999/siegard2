Implementar primeiro. A revisão vem depois.

Recomendo `/implement-task` para `task/fees/compute-late-fee`. A rota do plano é `/plan-work` → `/implement-task` → `/review-change`, e `/review-change` lê o que uma entrega escreveu. Como a tarefa ainda não foi entregue, não há nada para revisar. O que mudaria a recomendação: encontrar uma entrega já escrita para essa tarefa, e nesse caso a revisão passaria a ter o que ler.

Segui o que você pediu e não rodei nada. Por isso não rodei `bin/door.py --check`, que confirma se `/implement-task` aceita essa tarefa com a árvore como está. A resposta acima vem da ordem das rotas e do que você me disse sobre o estado, e não de uma checagem em disco. Se quiser, rodo essa checagem antes de você invocar `/implement-task`.
