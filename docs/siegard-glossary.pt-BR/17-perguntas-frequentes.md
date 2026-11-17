> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md) · Próximo: [Índice alfabético](18-indice-alfabetico.md)

## 17. Perguntas frequentes

**Por que não posso simplesmente editar o `siegard-trace.json` para tirar o drift?**
Porque o trace é a única ligação de longa duração entre código e especificação. Apagar ou ajustar
uma entrada à mão faria o trace afirmar algo que nenhum julgamento verificou. Cada classe de drift
tem o seu remédio (§9): `code` e `moved` são respondidos por um `/reconcile` sobre os arquivos,
`proof` por uma certificação, um arquivo apagado da árvore pelo `trace.py --release`, e só a classe
`orphaned` é removida, pelo `--prune`, depois de um `/analyse` que retirou nós. Num projeto
Siegard, um hook recusa até a tentativa: a escrita à mão do `siegard-trace.json` (assim como a de
um `plan.json`, de um `delivery.json` ou de uma execução capturada) é bloqueada.

**Qual a diferença entre `/review-change` e `/reconcile`?**
A revisão examina uma **entrega** (tarefas de um plano) por quatro ângulos (mais a certificação,
quando algum teste alega provar um nó), inclusive cobertura de testes e standard. A reconciliação examina **arquivos quaisquer** que mudaram fora de uma entrega,
e só pelo ângulo da conformidade com os nós que o trace já liga a eles. A revisão usa internamente o
mesmo mecanismo de stage, fold e bind da reconciliação. Para ler arquivos mudados sem tarefa contra
o **standard** (e não contra a especificação), a skill é outra: `/check-source`.

**Qual a diferença entre bind, rebind e re-bind?**
*Bind* é escrever um vínculo no trace. *Rebind* é escrevê-lo de novo para que os digests batam com
o disco. *Re-bind* (com hífen) é outra coisa: é o binder do planejamento reler um nó que mudou
depois que a tarefa foi planejada (§6).

**Por que o Siegard não aprova nem reprova nada?**
Porque um revisor automático que aprova vira um portão, e um achado com o qual ninguém pode
discordar deixa de ser evidência para virar decisão. O Siegard produz a evidência; a pessoa decide.

**Por que um juiz por arquivo, se sai mais caro?**
Porque um único contexto lendo tudo "satura" e declara limpos pares que nunca examinou. A economia
vem de outro lugar: da omissão de pares já julgados (`pairs_omitted`), da camada mecânica, da
certificação por testes e, na adoção, do ledger.

**O juiz disse `nowhere` para um nó. O código está errado?**
Não necessariamente. `nowhere` diz só que o fato daquele nó não está naquele arquivo. Se o nó
estava vinculado ao arquivo, o vínculo deixa de valer ali; o que fazer (corrigir a especificação,
corrigir o código, ou tirar só aquele par do vínculo com `trace.py --release … --node`, §9) é
decisão da pessoa.

**O que significa `collateral` e o que eu faço com ele?**
Que o nó não foi liberado **só** porque divide o arquivo com um finding que não disse a qual nó
pertence. Nada foi encontrado contra o próprio nó. Resolva o finding sem nó; na próxima
reconciliação daquele arquivo, o nó é liberado junto.

**`findings: []` e a ausência de `findings` são a mesma coisa?**
Sim. As duas formas significam "nada encontrado" — e isso é uma afirmação real de que o código
afirma só o que a especificação contém.

**Posso rodar `/reconcile` sobre um arquivo não commitado?**
Não. O bind grava digests, e o digest de uma edição não commitada aponta para um conteúdo que pode
desaparecer. Commite (ou descarte) primeiro; a decisão é sua.

**Como sei que uma onda de juízes terminou?**
Pela linha que o `--save-return` imprime depois de cada retorno salvo: `wave N: … 0 pending`.
Nunca contando notificações de cabeça. Várias chegam num mesmo turno, algumas dentro do turno que
disparou a onda, e a contagem guardada na conversa fica sempre abaixo do real. Uma sessão que
contou "faltam 3" quando os vinte já tinham voltado espera por nada.

**Tenho um pedido vago. Mando direto ou passo pelo `/clarify-request`?**
Se o projeto já responde tudo o que o pedido deixa em aberto, as duas formas dão o mesmo
resultado. O `/clarify-request` vale quando o pedido se apoia em referências ("isso", "o
standard", "o plano acima") ou deixa um ato irreversível implícito: ele devolve uma instrução com
as suposições à vista. Se a instrução só lê ou planeja, ele já a executa no mesmo turno, só lendo,
e o resultado vem logo abaixo; se ela age (roda um comando, chama algo, muda o projeto), você
decide se executa.

**Um slug já usado foi recusado. Posso reaproveitar?**
Não. Escolha outro. O registro existente pode ser a justificativa de vínculos ainda em vigor, e
sobrescrevê-lo apagaria essa justificativa. Para execuções repetidas de um mesmo passo, o
`run.py --next` escolhe sozinho o próximo número livre (`<nome>-2`, `<nome>-3`…).

**Quem faz os commits?**
Cada skill de rota (`/analyse`, `/plan-work`, `/implement-task`, `/review-change`, `/reconcile`)
commita, ao final, o que ela mesma escreveu: um commit, restrito por pathspec às pastas que ela
encontrou limpas, com a mensagem `<skill> <slug>: <step>`. `/deliver-scope` e `/adopt-scope`
commitam também o próprio log e a medição. Fora disso, uma sessão só commita com as palavras da
pessoa naquela sessão. `push`, branch, `stash` e reescrita de histórico nunca são de uma skill; com
um goal ou um grant armado, um hook os recusa. O `/siegard-archive` não commita nada: entrega os
comandos git prontos, e quem os roda é a pessoa.

**Posso deixar o Siegard trabalhando sozinho?**
Sim, com `/siegard-goal --arm` sobre um escopo (um objetivo em prosa, um épico ou tarefas de um
plano vivo). Antes de armar, o `goal.py` confere tudo o que o `/deliver-scope` recusaria. O goal
sempre termina: um script lê do disco `state A` (entregue, provado, revisado e medido) ou
`state B` (parado onde só você resolve). Para acompanhar, `/siegard-progress`; para interromper,
`goal.py --disarm`, rodado por você.

**Qual a diferença entre goal e grant?**
O goal diz **o que** levar até o fim e quando acabou. O grant diz **quais decisões** o framework
pode tomar sem perguntar numa parada: portas, commits do que a rota escreveu, o fechamento da
iniciativa. Uma porta que um fato em disco decide (*derived*) uma rota de ponta a ponta já toma
sozinha; uma porta que depende de julgamento (*judged*) só é tomada sob um grant com orçamento
(`--budget`). Os dois são independentes e fechados ao modelo: só você os arma.

**O Siegard decidiu um fato que eu nunca disse. Posso discordar?**
Pode, e é esperado que você leia. Um fato que a especificação não dizia é decidido por um contexto
que não viu o recorte de tarefas, gravado no nó e registrado no decision log dele
(`<slug>.log.md`). Essa divulgação não é um portão: discordar é uma mudança comum, pelo
`/analyse`. Um fato que a especificação **contradiz**, ao contrário, nunca é decidido: a rota
para e espera você.

**Por que às vezes o relatório recomenda uma porta e às vezes diz que a escolha é minha?**
Porque três perguntas são sempre suas: uma contradição entre o escopo e a especificação, duas
leituras de uma mesma evidência, e quanto vale um achado. Nelas, o relatório diz o que cada opção
supõe e o que decidiria, sem recomendar. Fora delas, ele recomenda, e diz se a recomendação é
*derived* (um fato em disco decide) ou *judged* (um julgamento de custo ou de leitura do pedido).

**A sessão foi compactada no meio de uma rota. O que muda?**
As regras de sessão voltam ao contexto pelos hooks, mas o resumo da conversa não autoriza commit
nenhum. Antes do próximo commit, a autorização é relida das suas palavras gravadas pelo `ask.py`
(`ask.py --read`), vem de um goal armado que nomeia a rota, ou é pedida de novo a você.

**Como sei em que pé está o projeto?**
Pergunte ao disco, nunca à conversa: `/siegard-status` sobre o projeto inteiro (iniciativas vivas,
o que está entregue, bloqueado, em drift ou não commitado, e a versão do framework), ou
`/siegard-progress` sobre uma iniciativa (uma linha por tarefa).

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md) · Próximo: [Índice alfabético](18-indice-alfabetico.md)
