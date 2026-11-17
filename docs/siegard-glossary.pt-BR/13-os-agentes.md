> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [As demais skills e os scripts auxiliares](12-as-demais-skills-e-os-scripts.md) · Próximo: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md)

## 13. Os agentes

As skills delegam julgamento e produção a estes treze agentes (`src/claude/agents/`), sempre pelo
nome com escopo do plugin (`siegard:<nome>`), nunca pelo nome solto, que um `.claude/agents/` do
próprio projeto poderia sobrepor. **Nenhum agente tem shell** (não executa comandos). **Só os dois
produtores podem escrever arquivos**; todos os outros devolvem texto, e quem os disparou grava.

| Agente | Usado por | Faz | Modelo · esforço | Escreve arquivos? |
|---|---|---|---|---|
| `codebase-surveyor` | `/plan-work` | Levanta o código onde a mudança vai cair; devolve nós de inventário | `sonnet` · `medium` | Não |
| `backlog-decomposer` | `/plan-work` | Recorta o escopo em épicos e esqueletos de tarefa | `opus` · `high` | Não |
| `execution-contract-binder` | `/plan-work` | Decide o `implements` de cada tarefa; devolve notas classificadas | `opus` · `high` | Não |
| `unstated-fact-decider` | `/plan-work` | Decide um fato não declarado, às cegas quanto à tarefa; devolve edições de nó e entrada no log | `opus` · `high` | Não |
| `task-implementer` | `/implement-task` | Escreve o código de uma tarefa e o conteúdo do registro de implementação | `sonnet` · `high` | **Sim** |
| `test-author` | `/implement-task` | Escreve os testes e o conteúdo do registro de prova | `sonnet` · `high` | **Sim** |
| `failure-diagnostician` | `/implement-task`, `/review-change` | Diz por que cada falha de uma execução capturada falhou | `sonnet` · `medium` | Não |
| `coverage-auditor` | `/review-change`, `/reconcile` | Pareia critérios com testes; certifica os testes de um nó | `opus` · `high` | Não |
| `specification-conformance-reviewer` | `/review-change`, `/reconcile` | Lê um arquivo contra os seus nós; devolve findings e onde cada fato está | `sonnet` · `high` | Não |
| `standard-conformance-reviewer` | `/review-change`, `/check-source` | Lê arquivos contra as regras do standard que uma leitura decide | `sonnet` · `high` | Não |
| `domain-surveyor` | `/survey` | Lê uma área de código não entregue e devolve material de levantamento | `opus` · `high` | Não |
| `test-intent-reader` | `/survey` (forma de testes) | Lê uma área de testes declarados e devolve material de intenção | `opus` · `high` | Não |
| `door-decider` | `/deliver-scope`, e a sessão sob um grant | Escolhe uma porta entre as que uma parada entregou, onde nenhum fato no disco decide | `opus` · `high` | Não |

Todos os agentes leem com `Read`, `Grep` e `Glob`. Os dois produtores têm, além disso, `Write` e
`Edit`. Modelo e esforço vêm do frontmatter de cada arquivo de agente.

### `door-decider` — o decisor de porta
**O que é.** O agente que escolhe **uma porta** entre as que uma etapa parada entregou, quando
nenhum fato no disco decide entre elas: a escolha que sobra é de custo ou de leitura do pedido.
Devolve a porta, o degrau da escada que a separou, o fato que decide e o fato que inverteria a
escolha, ou diz que nada as separa.
**Por que existe.** Uma recomendação *judged* (julgada, ver §12, "O handoff") só é tomada sem a
pessoa sob um grant que ela armou. Quem toma essa escolha precisa estar às cegas quanto ao fim do
goal e quanto à história da execução: uma escolha feita onde o fim do goal é visível é feita pela
linha de chegada, e não pelo trabalho.
**Quando aparece.** Quando o `grant.py --decide` responde `judge:` sobre o relatório de uma
parada. O `/deliver-scope` o dispara (`references/doors.md`), e as regras de sessão mandam
dispará-lo sobre as portas que essa linha listou, e nada mais.
**Como funciona.** Recebe quatro coisas: as portas (cada uma com o que faz, o que deixa como está e
a invocação), os fatos em que cada uma se apoia (caminhos e linhas citadas, que ele mesmo lê), o
escopo do pedido citado literalmente e o orçamento que resta. Nunca recebe a conversa, a condição
do goal nem o grant. Uma porta que a própria entrada recusaria, ou que quebra uma regra, é
excluída, não escolhida. As três escolhas que são da pessoa (contradição entre escopo e
especificação, duas leituras da mesma evidência, o valor de um finding) ele devolve como
`reserved`. No resto, sobe a escada de SPEC-006 e para no primeiro degrau que separa as portas:
`keeps the route`, `serves the stated goal`, `can be undone`, `costs less`. O orçamento é um fato,
não um degrau.
**O retorno.** Um mapeamento YAML sem cerca, começando em `outcome:`, que é um de `chosen`,
`excluded` (sobrou uma porta depois das exclusões), `reserved` ou `none` (nenhum degrau separa as
portas). Com `chosen` ou `excluded`, a porta é tomada e vira uma linha `decided:` no log de
orquestração, terminando em `(grant sha256 <mark>)`. Qualquer outra resposta mantém a parada.
**Não confundir com.** O `unstated-fact-decider`, que decide um **fato** da especificação, às
cegas quanto à tarefa. O `door-decider` decide qual **porta** tomar e não escreve nada na
especificação.

**Respostas sem cerca.** Os nove agentes que devolvem um único mapeamento YAML
(`execution-contract-binder`, `unstated-fact-decider`, `task-implementer`, `test-author`,
`failure-diagnostician`, `coverage-auditor`, `specification-conformance-reviewer`,
`standard-conformance-reviewer` e `door-decider`) mostram a forma da resposta como bloco recuado,
nunca cercado, e dizem onde ela começa e termina (§10, "O retorno"). `tests/test_agent_contract.py`
recusa o arquivo de agente que mostre essa forma dentro de uma cerca, porque o modelo copia o
exemplo. Os dois leitores do `/survey` devolvem markdown (frontmatter mais os seis cabeçalhos), e
o `codebase-surveyor` e o `backlog-decomposer` devolvem blocos em texto puro.

**Delegação** = disparar um destes num contexto limpo. Um agente disparado roda em segundo plano, e
a skill espera a notificação do harness, nunca um `sleep` nem uma mensagem ao agente. **Inline** = o
recurso de emergência quando a sessão não consegue disparar agentes: a própria sessão aplica o
arquivo do agente, e o relatório precisa dizer isso. O `/reconcile` e o `/review-change` recusam
rodar o julgamento inline se a mesma sessão escreveu algum dos nós julgados.

**Por que nenhum agente tem shell.** As skills executam, sempre pelo `bin/run.py`, que captura cada
execução. Um agente com shell rodaria fora dessa captura, e o que ele viu existiria só num contexto
que ninguém mais consegue abrir. `tests/test_agent_contract.py` garante que nenhum agente tenha
`Bash`.

**Por que um revisor não pode escrever.** Se um revisor pudesse editar arquivos, poderia "corrigir"
o que apontou, e um achado com o qual ninguém pode discordar é uma decisão disfarçada. A permissão
de escrita de um agente não pode ser limitada a um caminho, só concedida ou negada por inteiro, por
isso `tests/test_agent_contract.py` garante que só os dois produtores tenham `Write` e `Edit`.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [As demais skills e os scripts auxiliares](12-as-demais-skills-e-os-scripts.md) · Próximo: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md)
