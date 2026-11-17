> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [O panorama: que problema o Siegard resolve](02-o-panorama-que-problema-o-siegard.md) · Próximo: [Configurando um projeto](04-configurando-um-projeto.md)

## 3. A jornada completa de uma mudança, contada do começo ao fim

Esta seção narra, em alto nível, o percurso típico de um projeto. Cada termo em negrito tem um
verbete próprio na Parte II.

**Etapa 1 — Configuração.** A pessoa roda `/siegard-config`, que escreve o **`siegard.json`**: o
arquivo que declara onde ficam a especificação, os planos, os registros de entrega e a telemetria,
quais são as bases de código (os **targets**), onde ficam os testes de cada uma e quais targets ela
edita livremente. Opcionalmente, roda `/siegard-standard`, que transcreve para o **standard** (um
registro do próprio projeto) as regras que as ferramentas do projeto já aplicam ou que a pessoa
declara, e os passos — instalar, compilar, testar — com que o projeto é construído. Os dois são
fechados ao modelo: só a pessoa os invoca.

**Etapa 2 — Especificação.** A pessoa entrega à skill `/analyse` um **material** (um documento, uma
transcrição de reunião, um ticket). A skill transforma esse material em **nós** da especificação —
elementos do domínio, regras, cenários, contratos, restrições de arquitetura — e valida tudo com o
`spec.py`. O que o material não dizia e precisava ser decidido é decidido e registrado no
**decision log** do nó. A skill commita a especificação; a pessoa revisa lendo esse commit.

**Etapa 3 — Planejamento.** A pessoa descreve o que quer construir (o **escopo**) e roda
`/plan-work`. A skill levanta o código existente (**inventário**), recorta o escopo em **épicos**
e **tarefas**, e um agente separado (o **binder**) decide, para cada tarefa, quais nós da
especificação ela implementa. Divergências entre a tarefa e a especificação voltam como **notas**
classificadas. Um fato de que a tarefa precisa e que nenhum nó diz não para o plano: ele é decidido
por um agente que não vê o recorte de tarefas (o `unstated-fact-decider`), entra na especificação e
no decision log, e a pessoa revisa depois. Uma **contradição** entre o escopo e a especificação, ao
contrário, para: só a pessoa a resolve. O resultado é validado pelo `plan.py`, que gera o
`plan.json`, e a skill commita o plano.

**Etapa 4 — Entrega.** Para cada tarefa, a pessoa roda `/implement-task`. Um agente escreve o
código (`task-implementer`), outro escreve os testes (`test-author`), os passos que o standard
declara (instalar, compilar, testar) rodam por meio do `run.py`, que guarda tudo o que foi
impresso, e dois **registros de entrega** são gravados: o de **implementação** e o de **prova**.
Por fim, a skill **vincula** (bind) no **trace** cada nó ao arquivo que agora contém o seu fato e
commita o que escreveu.

**Etapa 5 — Revisão.** A pessoa roda `/review-change`. Quatro julgamentos independentes (os
**passes**) examinam a mudança: se os testes provam os critérios, se o código afirma só o que a
especificação contém, se o código segue o standard, e por que alguma execução falhou; quando um
teste alega provar um nó, uma **certificação** julga se ele de fato o prova. O resultado é um
**registro de revisão** com **findings**, que a skill commita. Nenhum finding para a rota: o valor
de cada um é decisão da pessoa.

*(As etapas 3 a 5 podem ser executadas de ponta a ponta por `/deliver-scope`, quando a mensagem da
pessoa pede isso com todas as letras. Ele invoca cada skill inteira, prova o que a revisão deixou
testável, mede a execução no fim, registra cada passo num log de orquestração
(`orchestration.md`) e toma sozinho as portas que um fato em disco decide, anotando cada uma numa
linha `decided:`. Onde só a pessoa decide, ele para.)*

**Caminho autônomo — goal e grant.** Quem quer apontar um escopo e voltar só no fim roda
`/siegard-goal --arm`. O goal leva o escopo pela rota do `/deliver-scope` sem perguntar nada e
sempre termina, porque quem diz se acabou é um script (`goal.py --state`), não o modelo: em
**state A** (entregue, provado, revisado e medido) ou em **state B** (parado onde só a
pessoa resolve). Por padrão, um objetivo escrito em prosa passa antes por um `/analyse`. Já o
`/siegard-grant` autoriza o framework a tomar as decisões que uma parada devolveria — uma porta
(as julgadas, só dentro de um orçamento), o commit do que a rota escreveu, o fechamento da
iniciativa — até a pessoa limpá-lo. Os dois são fechados ao modelo, e com qualquer um armado um
hook recusa `push`, branch e reescrita de histórico. Para acompanhar: `/siegard-progress` sobre a iniciativa, ou
`/siegard-status` sobre o projeto. Ver §12.

**Etapa 6 — Semanas depois: uma edição fora do fluxo.** Durante um incidente, alguém corrige um
arquivo diretamente e commita. O trace continua afirmando o digest antigo daquele arquivo. Na
próxima sessão, o hook de início já mostra o drift que o projeto carrega, e o `trace.py --check`
aponta **drift** (divergência) da classe `code` naquele arquivo.

**Etapa 7 — Reconciliação.** A pessoa roda `/reconcile` sobre o arquivo alterado. A skill prepara
o material dos juízes (**stage**), dispara um juiz por arquivo, salva os retornos literalmente,
**dobra** (fold) os retornos num **registro de reconciliação**, **revincula** no trace apenas os
nós que os juízes liberaram e commita o trace e o registro. Para os demais, entrega as duas portas
— corrigir a especificação (`/analyse`) ou corrigir o código (incremento corretivo do
`/plan-work`) — sem recomendar nenhuma: duas leituras de uma mesma evidência são da pessoa.

**Outras rotas.** Nem toda mudança percorre as etapas 2 a 5. As regras de sessão listam seis rotas,
e qual delas uma mudança toma é a pessoa que diz: um fato do negócio começa no `/analyse`; uma
superfície que a especificação já contém começa no `/plan-work`; um comportamento errado em código
já entregue vai pelo incremento corretivo do `/plan-work`; um comentário que não deveria estar no
código é removido à mão e seguido de `/reconcile`; um ajuste puramente visual vai direto ao código,
num target que o `siegard.json` declara `edits_freely`; e código anterior ao Siegard vai pela
adoção, abaixo. Ver §4.

**Caminho alternativo — adoção.** Se o projeto já tinha código antes do Siegard, o percurso começa
por `/survey` (levantamento do código existente), segue para `/analyse` (que escreve a
especificação a partir do levantamento e um **ledger**) e termina num `/reconcile` em modo
**adoção**, que cria o primeiro trace. O `/adopt-scope` executa esses três passos de ponta a
ponta, um contexto por vez, commitando entre eles. Ver §11 e §16.

**Fechamento.** Quem diz que uma iniciativa acabou é a pessoa — com as próprias palavras, ou por um
grant que ela armou com `--close`. Um `/plan-work` de fechamento grava então o `closure.md`, com o
que a iniciativa deixa em aberto lido do disco, e ela passa a ser história. Mais tarde, o
`/siegard-archive` pode retirá-la da árvore de trabalho; ela continua no histórico do git.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [O panorama: que problema o Siegard resolve](02-o-panorama-que-problema-o-siegard.md) · Próximo: [Configurando um projeto](04-configurando-um-projeto.md)
