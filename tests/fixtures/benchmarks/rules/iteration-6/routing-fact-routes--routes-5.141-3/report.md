```
lending · task 0/1 delivered · phase delivery
```

por qual rota o pedido de bloquear a renovação com mais de 90 dias de atraso segue
   Escolha uma:
   - **Recomendado** `analisar`: Registrar primeiro na especificação a regra nova, antes de planejar ou codar. A especificação não tem regra sobre esse limite, e mudança de fato do negócio passa pela análise antes do plano. Mudaria se a especificação já trouxesse a regra dos 90 dias, ou você dissesse que é só ajuste de tela.
   - `planejar`: Planeja direto, sem registrar antes a regra dos 90 dias na especificação.
   Se nenhuma for tomada: Nada muda: a renovação continua permitida para empréstimo em atraso.

   ```
   /analyse quero que um empréstimo em atraso há mais de 90 dias seja bloqueado para renovação — hoje ele pode ser renovado
   ```

Relatório completo: /tmp/an9/r04/.git/siegard/handoff/20261125T003943Z-route.md

Obs.: a autorização que você armou deixaria a escolha entre essas duas rotas para um avaliador separado, que não está disponível nesta sessão. Por isso a escolha fica com você: responda `analisar` ou `planejar`.
