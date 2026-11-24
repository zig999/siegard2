Implementar primeiro. A revisão vem depois da implementação, e hoje não há nada para revisar: a tarefa task/fees/compute-late-fee está no plano `lending` e ainda não foi entregue. O caminho do framework é plano, implementação, revisão, nessa ordem. A revisão lê o que a implementação escreveu.

Isto vem da ordem das rotas e do que você me disse sobre o estado. Como você pediu para não rodar nada, não rodei a checagem que confirma se o `/implement-task` aceita essa tarefa como a árvore está agora (`bin/door.py --check`), nem olhei o estado em disco. Por isso não estou dando uma recomendação formal, só a ordem do caminho.

O que mudaria isso: se você me autorizar a rodar essa checagem e ela recusar o `/implement-task` (por exemplo, por algo pendente no plano), eu te digo qual é o motivo e o que vem antes.
