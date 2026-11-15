Implemente primeiro: `/implement-task task/fees/compute-late-fee`. A revisão agora está excluída — o próprio `/review-change` recusa a tarefa, porque nada dela foi entregue ainda.

- **Recomendo:** implementar primeiro.
- **Por quê:** é a única opção que o próprio comando aceita no estado atual do disco — fato verificado, não opinião.
- **O que mudaria isso:** existir o registro de implementação `delivery/lending/implementation/fees/compute-late-fee.md`; aí a revisão passa a ser possível.

Depois da implementação, a revisão é o passo seguinte.

Não rodei nada que altere o projeto, só verificações de leitura (estado: `lending · task 0/1 delivered · phase delivery`):

```
door.py --check implement-task --task task/fees/compute-late-fee
accepts

door.py --check review-change --task task/fees/compute-late-fee
refuses
refused: task/fees/compute-late-fee holds no implementation record: /tmp/rh/p/h02/delivery/lending/implementation/fees/compute-late-fee.md does not exist — a review of a task nothing delivered has no subject
```

Quando quiser seguir, é só dizer e eu rodo a implementação.
