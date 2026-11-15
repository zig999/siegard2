Implemente primeiro. A revisão agora não tem o que revisar: a tarefa `task/fees/compute-late-fee` ainda não foi entregue, e o próprio `/review-change` recusa rodar sobre ela.

**Recomendo `/implement-task task/fees/compute-late-fee`, e só depois `/review-change`.**

- **Por quê:** o `/review-change` está excluído. A verificação dele respondeu:
  ```
  refuses
  refused: task/fees/compute-late-fee holds no implementation record: /tmp/rd/p/d07/delivery/lending/implementation/fees/compute-late-fee.md does not exist — a review of a task nothing delivered has no subject
  ```
  Já a do `/implement-task` respondeu `accepts` (plan, pendências, padrão do projeto e árvore limpa conferidos).
- **O que mudaria isso:** se o registro de implementação dessa tarefa já existisse (ou seja, se ela já tivesse sido entregue), a revisão passaria a ser o próximo passo.

Não rodei implementação nem revisão; só `door.py --check implement-task` e `door.py --check review-change`, que apenas leem o disco. Nada foi escrito nem commitado.

Quando quiser seguir, é só colar:

```
/implement-task task/fees/compute-late-fee
```
