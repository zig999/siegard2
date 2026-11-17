> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [As demais skills e os scripts auxiliares](12-as-demais-skills-e-os-scripts.md) · Próximo: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md)

## 13. Os agentes

As skills delegam julgamento e produção a estes agentes, sempre pelo nome com escopo do plugin
(`siegard:<nome>`). **Nenhum agente tem shell** (não executa comandos). **Só os dois produtores
podem escrever arquivos**; todos os outros devolvem texto, e a skill grava.

| Agente | Usado por | Faz | Escreve arquivos? |
|---|---|---|---|
| `codebase-surveyor` | `/plan-work` | Levanta o código onde a mudança vai cair; devolve nós de inventário | Não |
| `backlog-decomposer` | `/plan-work` | Recorta o escopo em épicos e esqueletos de tarefa | Não |
| `execution-contract-binder` | `/plan-work` | Decide o `implements` de cada tarefa; devolve notas classificadas | Não |
| `unstated-fact-decider` | `/plan-work` | Decide um fato não declarado, às cegas quanto à tarefa; devolve edições de nó e entrada no log | Não |
| `task-implementer` | `/implement-task` | Escreve o código de uma tarefa e o conteúdo do registro de implementação | **Sim** |
| `test-author` | `/implement-task` | Escreve os testes e o conteúdo do registro de prova | **Sim** |
| `failure-diagnostician` | `/implement-task`, `/review-change` | Diz por que cada falha de uma execução capturada falhou | Não |
| `coverage-auditor` | `/review-change`, `/reconcile` | Pareia critérios com testes; certifica os testes de um nó | Não |
| `specification-conformance-reviewer` | `/review-change`, `/reconcile` | Lê um arquivo contra os seus nós; devolve findings e `read` | Não |
| `standard-conformance-reviewer` | `/review-change`, `/check-source` | Lê arquivos contra as regras de leitura do standard | Não |
| `domain-surveyor` | `/survey` | Lê uma área de código não entregue e devolve material de levantamento | Não |
| `test-intent-reader` | `/survey` (forma de testes) | Lê uma área de testes declarados e devolve material de intenção | Não |

**Respostas sem cerca.** Desde a 5.18.0, os oito agentes que devolvem um único mapeamento YAML
(`execution-contract-binder`, `unstated-fact-decider`, `task-implementer`, `test-author`,
`failure-diagnostician`, `coverage-auditor`, `specification-conformance-reviewer` e
`standard-conformance-reviewer`) mostram a forma da resposta como bloco recuado, nunca cercado, e
dizem onde ela começa e termina (§10, "O retorno").

**Delegação** = disparar um destes num contexto limpo. **Inline** = o recurso de emergência quando
a sessão não consegue disparar agentes: a própria sessão aplica o arquivo do agente, e o relatório
precisa dizer isso. O `/reconcile` e o `/review-change` recusam rodar o julgamento inline se a
mesma sessão escreveu algum dos nós julgados.

**Por que um revisor não pode escrever.** Se um revisor pudesse editar arquivos, poderia "corrigir"
o que apontou — e um achado com o qual ninguém pode discordar é uma decisão disfarçada. Por isso
`tests/test_agent_contract.py` garante que só os dois produtores tenham `Write` e `Edit`.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [As demais skills e os scripts auxiliares](12-as-demais-skills-e-os-scripts.md) · Próximo: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md)
