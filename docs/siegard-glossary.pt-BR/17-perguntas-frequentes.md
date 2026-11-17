> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md) · Próximo: [Índice alfabético](18-indice-alfabetico.md)

## 17. Perguntas frequentes

**Por que não posso simplesmente editar o `siegard-trace.json` para tirar o drift?**
Porque o trace é a única ligação de longa duração entre código e especificação. Apagar ou ajustar
uma entrada à mão faria o trace afirmar algo que nenhum julgamento verificou. Cada classe de drift
tem o seu remédio (§9); só a classe `orphaned` é removida, e pelo `--prune`.

**Qual a diferença entre `/review-change` e `/reconcile`?**
A revisão examina uma **entrega** (tarefas de um plano) por quatro ângulos (mais a certificação,
quando algum teste alega provar um nó), inclusive cobertura de testes e standard. A reconciliação examina **arquivos quaisquer** que mudaram fora de uma entrega,
e só pelo ângulo da conformidade com os nós que o trace já liga a eles. A revisão usa internamente o
mesmo mecanismo de stage, fold e bind da reconciliação.

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
corrigir o código, ou liberar o arquivo do vínculo com `--replace`) é decisão da pessoa.

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
sobrescrevê-lo apagaria essa justificativa.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md) · Próximo: [Índice alfabético](18-indice-alfabetico.md)
