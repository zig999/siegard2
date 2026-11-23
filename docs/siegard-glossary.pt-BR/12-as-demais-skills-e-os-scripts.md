> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Adoção e levantamento (`/survey`)](11-adocao-e-levantamento.md) · Próximo: [Os agentes](13-os-agentes.md)

## 12. As demais skills e os scripts auxiliares

### O handoff: a mensagem final de uma skill, e o que ela recomenda
**O que é.** *Handoff* é a última mensagem de uma invocação de skill, aquela em que o controle
volta para você: o relatório, ou a parada que encerrou a execução antes do fim. A forma dessa
mensagem é fixada pela especificação do framework (SPEC-006) e vale para todas as skills que
relatam algo. O retorno de um agente disparado nunca é um handoff.
**Como abre.** Antes de qualquer explicação vem o que precisa de você, nesta ordem e omitindo o
que estiver vazio:
1. o estado em uma linha (concluído, parado e por quê, ou aguardando você);
2. o que o relatório retira do que a mesma invocação disse antes (uma correção do próprio agente);
3. cada decisão pendente, com suas portas, o que cada porta faz e o que fica como está se nenhuma
   for tomada;
4. cada ato **devido** (*owed*), com a invocação pronta e o passo que ele destrava, separado dos
   atos apenas **oferecidos** (*offered*).

Nenhuma das listas é ordenada por preferência: uma ordem que nenhum comando imprimiu seria uma
preferência disfarçada.

**Nas palavras da pessoa.** Cada item da abertura diz **o que ele é para você**, em palavras
simples no idioma da conversa: o que precisa ser feito antes de um passo nomeado rodar; o que pode
ser feito sem que nada espere por isso; o que só você decide; o que é sugerido e por quê. Nunca com
uma palavra do framework: "devido", "oferecido", "porta" e "critério" são vocabulário deste
glossário e dos `SKILL.md`, não da abertura. Quem nunca abriu o arquivo de uma skill lê a abertura
inteira. Quando o relatório recomenda uma porta, a abertura já diz qual e por quê, antes de
qualquer explicação.

**Um bloco por decisão.** Cada decisão pendente e cada ato devido vira um bloco: a porta
recomendada, com o porquê em uma frase e o fato que a mudaria (ou, quando a escolha é sua, o que a
resolveria); as demais portas, na ordem em que um comando as imprimiu; o que fica como está se
nenhuma for tomada; e, por último, a invocação pronta para colar. Uma decisão com duas portas ou
mais diz, numa linha logo acima delas, como as portas se relacionam (`relation`): `one-of` (você
toma uma), `in-order` (são os passos de um caminho, todos tomados na ordem listada, numerados) ou
`independent` (cada uma vale sozinha). Uma decisão sozinha não é numerada, porque um "1." solto
parece o primeiro passo de uma sequência.

Depois vem o relatório na ordem que o `SKILL.md` daquela skill define, no idioma da conversa, com
cada termo do Siegard explicado uma vez, na primeira ocorrência. Saídas de comando, notas e
entradas de log são citadas literalmente, sem tradução.
**Porta (door).** Cada ato que o handoff entrega a você, como uma invocação pronta para colar.
**Não confundir com.** O relatório completo, que fica num arquivo (abaixo) e guarda o que a
abertura não repete.

### Recomendação derivada e recomendação julgada
**O que é.** Quando há mais de uma porta, o handoff nomeia a que recomenda, ou diz por que a
escolha é só sua. Uma recomendação nomeia quatro coisas: a porta, o **critério**, o fato que decide
e o fato que a inverteria. Sem as quatro, nenhuma porta é recomendada. Há dois tipos, e o handoff
diz qual é.
**Derivada (derived).** Um **fato no disco** decide. O critério é um destes quatro, e nenhum outro:

| Critério | Quando vale |
|---|---|
| `precondition unmet` | a skill da porta recusaria as entradas do jeito que a árvore está (é o que o `door.py --check` responde, abaixo) |
| `rule violated` | a porta quebra uma regra do framework (por exemplo, gravar na especificação um fato tirado só da asserção de um teste) |
| `already done` | o trabalho da porta já está na árvore |
| `reading paid twice` | o **mesmo arquivo** seria lido por dois julgamentos: entre duas leituras sobre os mesmos arquivos, a que se paga uma vez é preferida à que se pagaria duas. Duas invocações sobre arquivos **diferentes** são pagas uma vez cada |

Uma porta excluída por um desses motivos é dita excluída, ao lado do seu fato. Quando sobra uma só,
ela é a recomendada.
**Julgada (judged).** Nenhum fato exclui uma porta, e o que sobra é uma escolha de custo ou de
leitura do pedido. O critério é o primeiro degrau desta escada que separa as portas, e nenhum
outro. A escada é uma só para todos os handoffs:

| Degrau | Quando separa |
|---|---|
| `keeps the route` | a porta segue a rota do framework |
| `serves the stated goal` | a porta alcança um objetivo que o pedido (ou a sua intake) declara, **citado literalmente**; sem a citação, o degrau não vale |
| `can be undone` | a porta pode ser desfeita e a outra não |
| `costs less` | um custo que **um comando imprimiu**, nunca uma estimativa |

O handoff diz que a recomendação julgada é um juízo.
**O nome do critério é só para o log.** No handoff, as quatro coisas aparecem como frases nas suas
palavras: qual porta, por que ela, o que no disco diz isso e o que mudaria a recomendação. O nome
em inglês do critério só é escrito na linha `recommended:` ou `decided:` do `orchestration.md`
(§7). Um rótulo como "Critério: reading paid twice" na prosa é o registro vazando para a conversa.
**Onde nenhuma porta segue a rota.** Quando todas as portas estão excluídas, a abertura diz isso,
nomeia a recusa ou a regra de cada uma, não recomenda nenhuma, e aponta a rota que recupera do
trabalho feito fora do framework, onde ela existir.

**O que nunca é recomendado.** Três perguntas são sempre da pessoa: uma contradição entre escopo e
especificação; duas leituras da mesma evidência (o código está certo ou a especificação?); e se um
finding importa ou qual rota ele merece. Nesses casos o handoff entrega as portas, não nomeia
nenhuma, e diz o que cada porta supõe verdadeiro e o que resolveria a escolha. A única exceção é o
valor de um finding decidido **de antemão** por você, como a política de findings de um goal
(`--correct contradicts`, abaixo): aí ela é aplicada por classe, nunca julgada. Os revisores
continuam entregando só evidência, sem veredito, severidade ou ranking.
**Finding não para nada.** Um finding de revisão nunca é uma parada. O handoff só chama algo de
parada quando o `SKILL.md` da skill o chama assim. Quando diz que um passo pode seguir, lista as
verificações que rodou, com a saída de cada uma.

### Tomar uma porta: as linhas `decided:` e `recommended:`
**O que é.** Às vezes a própria execução toma a porta, sem voltar a você. Cada porta tomada é uma
linha no log de orquestração da execução:

```
decided: <porta> — <critério> — <fato que decide>
recommended: <porta> — <critério> — <fato que decide>
```

`decided:` é uma porta tomada; `recommended:` é uma recomendação que um orquestrador repassou sem
tomar. O nome do critério já diz se ela foi derivada ou julgada.
**Quando uma porta derivada é tomada.**
- Dentro do `/deliver-scope`: o pedido que invocou a execução já é o "pode seguir", com ou sem
  goal. A porta é tomada quando é uma entrada que a rota invoca, o `door.py --check` a aceita e
  nenhuma linha `decided:` da mesma execução já a tomou sobre a mesma tarefa.
- Fora de um orquestrador: só quando a **sua** mensagem diz para seguir, o `door.py --check` aceita
  a porta e todas as outras estão excluídas. A linha `decided:` vai para o log da execução que ela
  continua, ou, se não houver log, para o corpo do commit seguinte.

**Quando uma porta julgada é tomada.** Só sob um **grant** que você armou (abaixo), como o
`door-decider` a devolveu (§13), às cegas quanto ao goal e ao grant, e dentro do orçamento do grant
para aquela iniciativa. Um goal armado sozinho não arma porta julgada nenhuma.
**Quem confere.** O hook `PreToolUse` do plugin (`hooks/commit_check.py`, abaixo) recusa um
`git commit` que acrescente a um log de orquestração uma linha `decided:` ou `recommended:` fora
dessa forma, ou uma `decided:` julgada sem um grant armado que cubra a iniciativa daquele log.
**Não confundir com.** A linha `decided:` que o `door.py --check` imprime (abaixo), que é uma
entrada que a própria skill decide (o único target, a única iniciativa viva), não uma porta tomada.

### Renderizado, nunca redigido (`handoff.py`)
Um handoff que entrega uma decisão sai de um **registro** (`schemas/handoff.json`), não de texto
livre:

```sh
handoff.py --prepare --skill <skill> --project <project-root> [--slug <slug>] [--target <key>] [--file <caminho>]... [--ledger <ledger.md>] [--language <en|pt-BR>]
handoff.py --save-report <caminho>       # relatório completo, lido da entrada padrão
handoff.py --render <registro>|-         # a mensagem que você lê
handoff.py --check <mensagem>|-          # confere uma mensagem já escrita como texto livre
```

- **`--prepare`** imprime o esqueleto do registro. O estado (`state`) já vem escrito por um script,
  e `state_from` diz qual: a primeira linha do `goal.py --state` quando há goal armado, senão o
  segmento do `progress.py` da iniciativa, senão a linha do projeto, senão as palavras fixas para um
  projeto sem nada em andamento. Cada porta já vem com a resposta do `door.py --check`, e nenhuma
  vem recomendada. Com `--ledger`, a contagem de linhas ainda abertas do material abre o estado, e a
  própria skill vira uma porta. Na saída de erro, linhas `limits:` dizem a que o `--render` vai
  segurar o registro, e linhas `next:` trazem as invocações seguintes prontas. A sessão só preenche
  os campos vazios.
- **`--save-report`** grava o relatório completo em `siegard/handoff/`, dentro do diretório do git,
  fora de toda raiz que o `git status` confere. Recusa um caminho fora dali e um relatório já
  escrito.
- **`--render`** recusa um registro cujo estado mudou desde o `--prepare`, uma porta recomendada que
  o `door.py` recusou, uma recomendação sem o porquê ou sem o fato que a inverteria, uma decisão de
  duas portas ou mais sem `relation`, jargão do framework na prosa e texto acima dos limites: estado
  até 200 caracteres, cada bloco de decisão até 700, a mensagem inteira até 1500. Guarda o registro
  em JSON ao lado do relatório, que é onde o `grant.py --decide --latest` o lê.
- **`--check`** confere um handoff escrito como texto livre só no que o texto decide: nenhum termo
  do jargão nos primeiros 450 caracteres e, quando entrega uma decisão, tamanho até 1500 e uma
  palavra de decisão nesses 450. Um texto livre que entrega uma decisão sem a linha que o `--render`
  escreve para "o que fica se nenhuma for tomada" é recusado como redigido, e o script nomeia o
  `--render`.

Os registros são de dois tipos (`kind`): `decision`, que entrega decisões, e `report`, para uma
resposta de status ou uma conversa de projeto, com `state` e um `body` curto, o caminho do relatório
ou os dois. O hook `Stop` mede cada handoff (abaixo, "Os hooks do plugin").

### Verificação de porta (`door.py`)
Diz, lendo só o disco e o git, se a skill de uma porta recusaria as entradas dela do jeito que a
árvore está agora:

```sh
door.py --check <skill> [--project <dir>] [--target <key>] [--slug <slug>] [--task <id>]... [--name <review-name>] [--scope <id>]... [--file <caminho>]... [--standard <file>]
door.py --check commit [--project <dir>] [--slug <slug>] [--file <caminho>]...
```

As portas conferidas são as cinco que um handoff entrega: `implement-task`, `plan-work`,
`review-change`, `deliver-scope` e `reconcile`. Cada uma é conferida pelas recusas que o próprio
arquivo da skill declara antes da primeira escrita, rodando o script que decide cada uma
(`project.py`, `spec.py`, `plan.py --check`, `deliver.py --check`, `deliver.py --outstanding`,
`deliver.py --standard`, `trace.py`) e citando o que ele imprimiu.

A primeira linha é `accepts` ou `refuses`. Depois vêm `refused:` (cada recusa, com a saída do
comando que a decidiu), `checked:` (cada verificação que passou), `decided:` (uma entrada que a
skill decide sozinha porque só há uma opção) e `not decided:` (uma recusa que nenhum script decide,
como as palavras da pessoa), que nunca é lida como aceite. Uma porta recusada aparece como
excluída, nunca recomendada.

**A verificação `commit`** confere o commit da entrega de uma iniciativa: recusa um commit que
acrescente uma linha de parada ao log e leve mais que a medição (a raiz de telemetria, o log com a
linha de parada e as execuções capturadas que terminaram `passed`), e um commit que leve uma
execução vermelha que nenhum registro nomeia e que nenhuma tentativa posterior respondeu. Se as
suas palavras autorizam o commit não é decidível por arquivo, e aparece como `not decided:`.

### Goal (`/siegard-goal` e `goal.py`)
**O que é.** Um *goal* é uma condição que a sessão persegue até ela valer: um escopo (um objetivo
em prosa, um épico ou um conjunto de tarefas de um plano vivo) levado de ponta a ponta sem que
ninguém seja consultado no caminho. O fim é decidido por um script, não pela leitura de um modelo.
**Por que existe.** Uma condição escrita em prosa deixa o fim para uma leitura, e uma leitura que
não enxerga o fim pede trabalho à sessão sem parar. Aqui a condição nomeia um comando, e a primeira
linha desse comando é a resposta.
**Como armar.** Só pela `/siegard:siegard-goal`, e só quando a sua invocação **começa** com
`--arm`. A skill é fechada ao modelo (abaixo), então os argumentos são as suas palavras:

```
/siegard:siegard-goal [--arm] [<project-root>] (epic/<n> | task/<epic>/<n> ... | <objetivo em prosa> | --objective-file <caminho>) [--slug <slug>] [--target <key>] [--correct contradicts] [--no-specify]
```

Sem `--arm`, a skill só **compõe**: confere tudo e entrega a linha `--arm` pronta para você colar.
Um objetivo que aponta para um texto da conversa ("as partes 2 e 3 acima") é uma **citação**: o
texto é copiado literalmente para um arquivo, que você lê antes de armar por `--objective-file`.
**Especificar antes do plano.** Um objetivo em prosa roda o `/analyse` uma vez sobre ele antes do
plano, a menos que você diga `--no-specify`. Um escopo de épicos ou tarefas nunca especifica.
**Política de findings.** `--correct contradicts` diz que os findings de conformidade da classe
`contradicts` são corrigidos por um incremento corretivo. É a única classe que uma rota corrige.
Sem ela, todo finding é relatado e nenhum é corrigido.

```sh
goal.py --compose <project-root> --slug <slug> (--scope <id>... | --objective <texto> | --objective-file <file|->) [--target <key>] [--correct contradicts] [--no-specify]
goal.py --arm <project-root> (os mesmos argumentos)
goal.py --state <project-root> --slug <slug> --since <commit> --version <versão> [--target <key>] [--scope <id>]... [--untouched <caminho>]...
goal.py --disarm <project-root>
```

**Como funciona.** O `--compose` confere o que o `/deliver-scope` recusaria primeiro (especificação
íntegra, nada pendente nas raízes que a rota escreve, slug não fechado, ids que o plano tem), fixa
onde o `HEAD` está, a versão do plugin e tudo o que já estava pendente fora dessas raízes (declarado
`untouched`), e imprime a condição. O `--arm` faz as mesmas verificações, recusa um projeto que já
tem goal armado e grava `siegard/goal.json` dentro do diretório do git, nunca na árvore. Um goal não
carrega orçamento: porta julgada só sob grant.
**Os três estados** (`goal.py --state`, primeira linha):
- `state A` — toda tarefa do escopo entregue, provada (ou entregue só como substrato) e revisada,
  a medição commitada depois do último registro, a árvore limpa a não ser pelo que foi declarado
  `untouched`, todo commit desde o início nomeando uma skill e o slug, nada enviado ao remoto, e o
  plugin na mesma versão.
- `state B` — a execução parou num ponto que só uma pessoa move: o log de orquestração termina numa
  linha de parada de uma das classes conhecidas (`blocking`, `silence`, `contradiction`,
  `gave-up`, `infrastructure`, `already-met`, entre outras); a versão do plugin mudou; um commit
  tocou o `siegard.json` ou o standard; um commit não nomeia skill e slug; ou um critério foi
  registrado como não atendido.
- `not yet` — nenhum dos dois; as verificações que falharam dizem o que falta.

Em qualquer estado, a verificação `criteria` também nomeia os critérios que as revisões deixaram
sem cobertura, sem reprovar nada.
**O hook `Stop`.** A cada parada da sessão, o hook roda o mesmo cálculo. `state A` ou `state B`
encerra o goal e deixa a sessão parar. `not yet` bloqueia a parada com as verificações que
falharam, e a sessão responde com o próximo passo da rota. O quarto `not yet` idêntico seguido
encerra o goal como pausado (`paused`). O goal se liga à primeira sessão cuja parada o alcança; um
goal encerrado vai para `siegard/goals-ended.jsonl`.
**O que um goal parado ainda commita.** Depois de uma linha de parada, a execução não commita nada
além da medição (a raiz de telemetria, o log com a linha de parada e as execuções que terminaram
`passed`). O resto fica para você.
**Encerrar.** Só você: `! python3 -B <raiz do plugin>/bin/goal.py --disarm <project-root>`. Nenhuma
sessão roda `--disarm` sem que você peça.
**Não confundir com.** O `/goal` do próprio harness, em que um modelo lê a transcrição para decidir
o fim. A condição composta pode ser colada depois de `/goal`, mas a linha que o relatório entrega é
a do framework, que termina na resposta do script. E com o **grant**, que não leva nada até o fim:
só autoriza decisões nas paradas.

### Grant (`/siegard-grant` e `grant.py`)
**O que é.** A autorização que você dá **de antemão** para as paradas que o framework devolveria:
tomar uma porta, commitar o que a rota escreveu, fechar uma iniciativa, sem perguntar a cada parada.
Vale para o projeto (todas as iniciativas vivas) ou para uma iniciativa (`--slug`), até você
limpá-lo. É o único lugar em que uma porta julgada é armada, com ou sem goal.
**Como armar.** Só pela `/siegard:siegard-grant`, fechada ao modelo. A sua invocação, tal como
digitada (flags, valores e uma frase opcional), **é** a autorização, e é gravada literalmente:

```
/siegard:siegard-grant [<project-root>] [--clear | [--slug <slug>] [--target <key>] [--doors <skill>,...|none] [--budget <n>] [--commits] [--close] [<uma frase sua>]]
```

Sem argumento nenhum, a skill não arma nada: só mostra o grant armado (`grant.py --read`).
**As cláusulas** (pelo menos uma):

| Cláusula | O que deixa a sessão fazer |
|---|---|
| `doors` | Tomar portas destas entradas: `plan-work`, `implement-task`, `review-change`, `reconcile`, `deliver-scope`, `analyse` (as seis, se você não nomear nenhuma; `none` deixa vazio). Vem com um **orçamento** (`--budget`) de portas julgadas **por iniciativa**, zero se você não disser outro número. |
| `commits` | Commitar o que a rota escreveu. |
| `close` | Fechar uma iniciativa quando tudo nela está entregue, provado e revisado, com as suas palavras como motivo do fechamento. |

**A marca (mark).** Cada grant é identificado pelo digest das suas palavras junto com o instante em
que foi armado, para que dois grants armados com a mesma invocação nunca se confundam. Toda linha
`decided:` tomada sob o grant termina com `(grant sha256 <mark>)`, e o orçamento só conta as linhas
com a marca dele.

```sh
grant.py --arm <project-root> [--slug <slug>] [--target <key>] [--doors <skill>[,<skill>...]|none] [--budget <n>] [--commits] [--close] --words-file <file|->
grant.py --disarm <project-root>                    # o que /siegard-grant --clear roda
grant.py --read <project-root>
grant.py --decide <project-root> (--record <file> | --latest <skill> --after <commit>) --slug <slug>
grant.py --commit <project-root> --file <caminho>...
grant.py --close <project-root> [--slug <slug>]
```

**Numa parada (`--decide`).** Sobre o registro do handoff da parada, responde uma linha por
decisão:
- `stop: <por quê>` — a escolha é sua (a decisão traz `settles`), nenhuma porta se qualifica, a
  porta está fora de `doors`, não foi conferida, ou o orçamento acabou;
- `take: <porta> — precondition unmet — <fato>` — sobrou exatamente uma porta depois das recusas,
  ela está em `doors` e o `door.py` a aceitou;
- `judge:` — a porta recomendada foi aceita ao lado de outra porta aberta: as portas, o orçamento
  que resta e os fatos vão para o `door-decider` (§13), que escolhe às cegas.

O orçamento que resta é o do grant menos as linhas `decided:` julgadas que o log daquela iniciativa
ganhou desde que o grant foi armado, cada iniciativa contada à parte. O `/deliver-scope` pergunta ao
`--decide --latest` antes de encerrar numa parada, e as regras de sessão mandam qualquer sessão
perguntar ao `--decide` sobre o registro do handoff antes de entregar uma decisão a você. A mesma
porta sobre a mesma tarefa é tomada uma vez só numa execução.
**Os portões (`--commit` e `--close`).** A primeira linha é `accepts` ou `refuses`, seguida de
linhas `refused:` e `checked:`.
- `--commit` aceita só se o grant tem `commits` e todo caminho é um que a rota escreve (a raiz de
  entrega ou de trabalho de uma iniciativa coberta, a raiz de telemetria, `siegard-reconcile/`, o
  trace, ou um caminho que um registro dessas iniciativas nomeia). Recusa o `siegard.json`, um
  standard declarado, o `CLAUDE.md`, um arquivo com credenciais, um caminho fora do projeto, um
  `closure.md` sem a cláusula `close`, e um arquivo da especificação que o `HEAD` já tem e o commit
  modifica, exceto o decision log.
- `--close` (com `--slug`) aceita só se o grant tem `close` e o cálculo do goal sobre a iniciativa
  encontra toda tarefa entregue, provada e revisada, nenhum critério não atendido sem resposta e a
  especificação íntegra. O fechamento pergunta isso **antes** de escrever o `closure.md`.

Um `refuses` para o commit ou o fechamento, a menos que as suas palavras na sessão nomeiem aquele
commit ou aquele fechamento: um commit que você nomeia não é uma "tomada".
**O que o grant nunca toma**, diga o que disser: uma das três escolhas que são só suas, um push,
uma branch, uma reescrita de histórico, uma edição feita pela sessão fora de uma skill, nada em outro
projeto, nenhum comando que o registry do projeto não declara, e nada que a verificação da porta
recuse. Enquanto um grant (ou um goal) está armado, o hook `bounds.py` recusa push, branch e
reescrita (abaixo).
**Quando termina.** Quando você o limpa (`/siegard:siegard-grant <project-root> --clear`), quando a
versão do plugin deixa de ser a que ele foi armado, e, se nomeia uma iniciativa, quando o `HEAD`
dessa iniciativa passa a ter `closure.md`. Um grant encerrado vai, com o motivo, para
`siegard/grants-ended.jsonl`. Armar por cima de um grant que já terminou assim o encerra e arma; armar por cima de um grant que ainda vale o encerra como `replaced`, diz o que ele cobria e arma, sem precisar de `--clear` antes.
O registro armado fica em `siegard/grant.json`, dentro do diretório do git; as palavras ficam na
raiz de telemetria, e a medição as commita.
**Não confundir com.** O **goal**, que leva um escopo até o fim e termina sozinho. O grant não leva
nada: só decide paradas. Os dois podem estar armados juntos, e só o grant arma portas julgadas.

### Pedido gravado (`ask.py`)
Uma compactação guarda um resumo do que a pessoa disse, nunca as palavras dela. O `ask.py` grava as
palavras que autorizam uma rota, byte a byte, num arquivo `ask-<carimbo>.md` na raiz de telemetria,
com um digest (os 16 primeiros caracteres hexadecimais do sha256):

```sh
ask.py --record <project-root> --text-file <file|->
ask.py --read <project-root> [--path <file>] [--sha256 <digest>]
```

O `--read` imprime `ask: <caminho> (sha256 <digest>)` e, abaixo, o texto literal. Com `--sha256`,
recusa (`refused:`) um arquivo que não bate mais com o digest, sem mostrar o texto. Assim, uma rota
retomada depois de uma compactação lê a autorização nas palavras da pessoa, não num resumo. Gravar
não amplia nada: o que o pedido autoriza continua sendo lido das palavras dele. A medição commita a
raiz de telemetria inteira, e o pedido gravado vai junto.

### Relay (`relay.py`)
Texto destinado à sessão de outro projeto (um "irmão"):

```sh
relay.py --to <raiz-do-irmão> --from <project-root> --text-file <file|->
relay.py --confirm <arquivo-de-relay>
```

O `--to` grava o texto em `relay-<carimbo>-<irmão>.md` na raiz de telemetria **deste** projeto,
nunca no repositório do irmão, e imprime uma linha `confirm:`. A sessão do irmão roda essa linha
primeiro: a primeira linha é `confirmed` ou `refuses`. Recusa, sem mostrar o texto, quando a sessão
está no projeto errado, roda outra versão do plugin ou o texto não bate com o digest. Um irmão sem
`siegard.json`, ou que é o próprio projeto, é recusado e nada é gravado.

### `/siegard-config`
Escreve ou atualiza o `siegard.json` a partir do que a pessoa diz. É o único que escreve esse
arquivo (§4). Também liga ou desliga a linha de progresso na barra de status, quando a pessoa pede
(`progress.py --install`, abaixo).

**Skills fechadas ao modelo.** `/siegard-config`, `/siegard-archive`, `/clarify-request`,
`/siegard-goal` e `/siegard-grant` só podem ser invocadas por uma pessoa
(`disable-model-invocation: true`): o modelo não as dispara por conta própria, nem de dentro de
outra skill. Quando uma skill precisa de uma delas, entrega a invocação pronta para a pessoa colar.
O critério é quem consegue declarar a entrada: em todas as cinco, só a pessoa. O
`/siegard-standard` é aberto à sessão com a trava dentro: invocado por ela, só escreve o que um
pedido gravado com `ask.py --record` nomeia. No `/siegard-goal` e
no `/siegard-grant`, as palavras digitadas são a própria autorização.

### `/clarify-request` — reescrever um pedido como uma instrução validada
**O que é.** Uma skill que recebe um pedido em linguagem natural ("olha essa implementação e vê se
segue o standard que a gente definiu") e o devolve como **uma única instrução precisa** para o
Claude Code. Uma instrução que só lê ou planeja (`ANALYZE`, `PLAN`) é executada no mesmo turno, só
por leitura; as demais são entregues **sem execução**. Ela lê o projeto para resolver referências
("isso", "o standard", "o que decidimos"), pergunta à pessoa só as decisões que são dela, e mantém
exatamente a intenção, o modo e o escopo do pedido.
**Por que existe.** Um pedido vago é executado com palpites, e os palpites não aparecem em lugar
nenhum. A regra que a skill serve é uma só: **esclarecer o que a pessoa quis dizer, nunca
completar o que ela não decidiu**. Uma instrução mais clara que o pedido e também maior que ele
passou de esclarecer para decidir.
**O que ela nunca faz.** Não escreve arquivo nenhum, nem quando executa a instrução (`Write`, `Edit`
e `NotebookEdit` ficam bloqueados enquanto ela roda) e não roda comando nenhum além do validador.
Não reescreve um pedido que já é a invocação de uma skill (`/nome …`): essas skills leem as palavras
da própria pessoa, e algumas tomam essas palavras como autorização. Também não serve para planejar
nem especificar trabalho (isso é `/plan-work` e `/analyse`).
**A ordem:**
1. **Ler a operação do pedido** — qual operação, sobre qual alvo, em qual **modo**. O modo é o que
   as palavras dizem e nunca é elevado: pedir para olhar não é pedir para mudar. Um pedido que já é
   uma operação precisa, num modo declarado, sobre um alvo que se resolve, pula os passos 3 a 5.
2. **Tomar o que já foi decidido** na conversa, como requisito, sem perguntar de novo. O que o
   assistente propôs, recomendou ou concluiu não é decisão enquanto as palavras da pessoa não o
   tomarem: uma recomendação que ela não aceitou continua sendo uma opção.
3. **Resolver o que a leitura resolve** — primeiro pela conversa, depois pelo projeto, parando na
   primeira evidência. Uma referência a uma mensagem anterior ("o plano acima") resolve para essa
   mensagem, e o trecho sobre o qual o pedido age entra na instrução **citado literalmente**, marcado
   como da pessoa ou do assistente. Um resumo de compactação não resolve nada, nem uma memória da
   sessão: ela pode dizer onde procurar, e o que a instrução cita é o que foi encontrado lá. O que o
   executor pode descobrir sozinho vira uma linha `DISCOVERY`.
4. **Decidir o que é bloqueante** pelo teste de três partes (abaixo).
5. **Perguntar, se e somente se algo for bloqueante** — por `AskUserQuestion`, no idioma da
   pessoa, em no máximo duas chamadas. O que continuar em aberto depois da segunda é uma parada sem
   instrução, nunca um palpite.
6. **Escrever a instrução e validá-la** com `clarify.py`. Uma instrução nunca validada não é
   entregue.
7. **Entregar** — a mensagem contém a instrução num bloco cercado **sem rótulo de linguagem**, sem
   preâmbulo nem justificativa. Quando o validador imprime `hand-over` (modos `OPERATE`,
   `IMPLEMENT`, `IMPLEMENT_AND_VALIDATE`), ou quando executar exigiria mais que leitura (rodar um
   comando, chamar algo, consultar por um conector), nada vem depois do bloco e o turno termina ali
   de propósito: nada desta skill (as ferramentas bloqueadas, o esforço de raciocínio) chega ao
   trabalho que vem depois. A pessoa executa a instrução como executaria uma mensagem própria, ou
   diz o que mudar.
8. **Executar, só lendo** — quando o validador imprime `in-turn` (`ANALYZE`, `PLAN`), a skill
   executa a instrução no mesmo turno, só com `Read`, `Grep` e `Glob`: nenhum comando de shell é
   rodado, nada é enviado ou consultado, nenhuma skill é invocada, e o que a instrução não diz não é
   feito. Uma decisão que a leitura encontra e a instrução não resolve aparece no resultado como
   da pessoa. As suposições ficam no topo, acima do resultado; se uma estiver errada, a pessoa diz
   o que mudar e invoca de novo.

**O teste do bloqueante.** Uma incerteza só é bloqueante quando valem as três condições:
**divergência** (duas leituras plausíveis levam a resultados materialmente diferentes — regra de
negócio, modelo de dados, interface pública, escopo, segurança, compatibilidade, um ato
destrutivo ou irreversível, o próprio modo); **não resolvida** (nem a conversa nem o projeto
decidem); e **cara de errar** (um palpite errado não se desfaz facilmente). Faltando uma das
três, não é bloqueante: um detalhe reversível vira uma **suposição** (`ASSUMPTIONS`), com a sua
base.

**A instrução.** É escrita em inglês, em seções, cada uma aberta pelo nome em maiúsculas seguido de
dois-pontos, nesta ordem: `MODE`, `TASK`, `CONTEXT`, `OBJECTIVE`, `SCOPE`, `REQUIREMENTS`,
`CONSTRAINTS`, `ASSUMPTIONS`, `DISCOVERY`, `PROCESS`, `VALIDATION`, `OUTPUT`. Só `MODE` e `TASK`
são obrigatórias, e uma seção vazia é recusada: ausência já diz que nada foi decidido. Cada linha
tem exatamente uma fonte (as palavras da pessoa, uma decisão dela, uma mensagem anterior da conversa
citada literalmente, um fato lido do projeto como base de uma suposição, ou o limite que o modo
impõe), e uma linha sem fonte é apagada. As palavras do assistente servem de base só para aquilo a
que uma referência aponta, nunca para uma decisão. Uma linha que o executor cumpriria sem que lhe
dissessem ("tenha cuidado", "siga as convenções") não é escrita. Uma linha `DISCOVERY` diz o que
encontrar, nunca o que fazer se não encontrar: uma condição de parada que a pessoa não pediu é uma
decisão que não é da instrução.
**Os modos** (`MODE`):

| Modo | O que autoriza |
|---|---|
| `ANALYZE` | Investigar, explicar, diagnosticar, revisar, comparar, validar. Nenhum arquivo do projeto muda; um comando que só observa (a suíte existente, um linter, uma consulta de leitura) cabe aqui. |
| `PLAN` | Propor uma solução ou um plano. O projeto não muda. |
| `OPERATE` | Rodar um comando ou enviar uma requisição cujo efeito **não é observação** — criar ou alterar dados, um deploy, uma instalação, uma exclusão fora dos arquivos do projeto — sem modificar os arquivos do projeto. O efeito é nomeado em `TASK` e limitado em `CONSTRAINTS`. |
| `IMPLEMENT` | Mudar o projeto dentro do escopo esclarecido. |
| `IMPLEMENT_AND_VALIDATE` | Mudar o projeto e verificar a mudança (testes, checagens, build, lint ou uma execução). |

Os três primeiros não autorizam mudança nos arquivos do projeto, e por isso precisam carregar em
`CONSTRAINTS` uma linha que limite o projeto inteiro, começando com `Do not modify the project`
ou `Do not modify code`. Uma linha que limita menos (`Do not modify the CSS file`) deixaria o resto
autorizado. Os dois últimos não podem carregar esse limite, porque ele contradiria o modo.
**Ato sobre os dados versus capacidade.** Um pedido formulado como um ato sobre os dados do sistema
("remova os clientes inativos") é aplicado a esses dados, e a instrução diz isso. Um pedido
formulado como uma capacidade ("vamos permitir remover…") constrói o meio e não aplica nada. Uma
chamada que muda estado, como um `POST` que cria uma cobrança, nunca é `ANALYZE`, qualquer que seja
o verbo do pedido.

```
MODE: ANALYZE
TASK: Validate the implementation in src/billing/invoice.py against the project's standard.
SCOPE:
- src/billing/invoice.py and the tests that exercise it.
CONSTRAINTS:
- Do not modify code.
ASSUMPTIONS:
- "essa implementação" is src/billing/invoice.py: the operator's previous message, "terminei o invoice.py".
DISCOVERY:
- Identify which rules of standards/backend.md apply to the target.
```

**Contrato e validador.** `schemas/clarified-request.json` é a casa única das seções, da ordem,
do significado de cada uma, do que cada modo autoriza e de quais modos rodam no mesmo turno
(`x-executes-in-turn`). `clarify.py` confere uma instrução contra ele:

```sh
clarify.py <arquivo>      # confere a instrução contida no arquivo
clarify.py -              # confere a instrução lida da entrada padrão
```

Recusa uma seção que o contrato não nomeia, uma seção vazia, uma fora da ordem, texto antes da
primeira seção, a falta de `MODE` ou `TASK`, um modo de leitura sem o limite sobre o projeto
inteiro e um modo de mudança com esse limite. Saída `0` = bem formada, com uma linha dizendo se a
skill executa a instrução no mesmo turno (`in-turn`) ou a entrega (`hand-over`), decidida só pelo
modo; `1` = um problema por linha, `2` = não pôde rodar. Se a instrução preserva o que a pessoa quis
dizer não é decidível por script, e não é verificado.

### `/siegard-standard`
Redige o standard do projeto a partir do que as ferramentas do projeto já impõem (linter,
compilador, verificador de estilo, verificador de segredos) e do que uma pessoa declara, segurado a
`schemas/standard.json` (§4). Nunca inventa uma regra, nunca afia um limite que a pessoa não nomeou,
nunca apaga em silêncio uma regra que o arquivo já tinha, e nunca faz commit: o `git diff` é a
revisão da pessoa.

### `/check-source`
Lê código que nenhuma tarefa entregou contra as regras do standard que uma leitura decide, e grava
cada desvio num registro em `siegard-check/`. Ver §8.

### `/siegard-status`
**O que é.** Um panorama amigável e só de leitura do projeto inteiro, recalculado a cada pedido:
o framework não guarda status em lugar nenhum, de propósito. Toda pergunta sobre "como está", "o
que falta", "o que está bloqueado" ou "qual a versão" é respondida rodando esta skill, nunca pela
memória da conversa.
**O que lê.** Num único lote, cada saída num arquivo (nunca um `head` sobre uma saída):
- a especificação: `spec.py` e os cinco últimos commits que tocaram um decision log (as decisões
  tomadas por você mais recentes);
- cada iniciativa viva: `plan.py --check` e `deliver.py --outstanding` (uma vez por target),
  incluindo as tarefas entregues que nenhuma revisão nomeia e os registros que não fixam o standard
  declarado, como fato, nunca como passo pulado;
- o trace, uma vez por arquivo de trace: `trace.py --check --reconcile-set` sobre um target (nunca
  sobre o topo do git), depois `--convergence`, `--owed` quando o lado julgado não é zero, e
  `--encodes --rank`;
- o repositório: `git log` e `git status --porcelain`.

**O que entrega.** Uma forma curta (no máximo 8 linhas como renderizadas, um registro de kind
`report`) e o status completo em arquivo. Uma raiz com alteração pendente é um ato devido, e a
linha nomeia as skills que se recusam a começar sobre ela (a especificação trava `/analyse`,
`/plan-work` e `/deliver-scope`; a raiz de trabalho, `/plan-work` e `/deliver-scope`; a raiz de
entrega, `/implement-task`, `/review-change` e `/deliver-scope`; a raiz de código de um target,
`/implement-task` e `/deliver-scope`). Drift, findings e a falta de revisão nunca são devidos. Um
par que um `/reconcile` anterior já julgou e nenhum bind fechou (`reported` no `--owed`) aparece
como decisão sua, com as duas portas — `/plan-work` corretivo se o nó está certo, `/analyse` se o
código está — e nenhuma recomendação. A invocação de `/reconcile` vem do `--reconcile-set`, com o
slug que a linha `free slug:` imprimiu, nunca de uma composição da skill.
**O fechamento.** Termina com a invocação mais pronta para rodar, conferida pelo `door.py --check`:
é uma recomendação derivada, com critério `precondition unmet` ou `reading paid twice`, o fato que
decide e o que a inverteria.
**O que nunca faz.** Porcentagem, "quase pronto", nota de saúde ou qualquer número que nenhum
comando imprimiu; escolher a próxima tarefa; commitar.

### `/siegard-progress`
Uma tabela compacta das tarefas de **uma** iniciativa (`Task | Epic | Status | Detail`), feita para
rodar repetidamente (por exemplo, com `/loop`). O status de cada linha (`done`, `implemented,
unproven`, `blocked`, `waiting`, `ready`) é derivado do `deliver.py --outstanding`, e as notas
`BLOCKING` e `UNDERDETERMINED` vêm citadas inteiras abaixo da tabela, junto com as linhas sobre
registros que não fixam o standard declarado. Infere a iniciativa quando só há uma viva; com mais
de uma, para e lista os slugs. Se o `plan.py --check` acusa problema ou plano `STALE`, essa é a
resposta, e não há tabela.

### Linha de progresso (`progress.py`)
Uma linha por iniciativa viva, lida do disco sem nenhum modelo, unidas por ` | `:

```
<slug> · task 3/7 delivered · phase delivery · last: <última linha do orchestration.md>
```

A fase é a primeira que vale entre `plan`, `delivery`, `proof`, `review` e `reviewed`. Ela diz
quais registros existem, nunca o que é devido (uma tarefa entregue só como substrato aparece em
`proof`). Fora de um projeto com `siegard.json`, ou quando nada pode ser lido, a linha fica vazia.
Aparece na barra de status do Claude Code quando a pessoa pede ao `/siegard-config`:

```sh
progress.py [<dir>]
progress.py --install <project-root>     # grava no .claude/settings.local.json do projeto
progress.py --uninstall <project-root>   # remove a entrada, se foi este script que a gravou
```

O arquivo local fica fora do controle de versão, porque o caminho é desta máquina. Uma `statusLine`
que o script não escreveu é recusada, nunca sobrescrita. Depois de uma atualização do plugin, a
linha diz que a versão carregada é outra e nomeia o `--install` que a atualiza.

### `/siegard-archive` e `archive.py`
Remove da árvore de trabalho iniciativas **fechadas** (as pastas de work e delivery, juntas e
inteiras), depois de o `archive.py` verificá-las mecanicamente, nesta ordem: fechadas (`closure.md`),
commitadas (nada pendente nem ignorado no par) e ainda válidas como histórico (`plan.py --check` e
`deliver.py --check`). Nunca toca no arquivo do projeto, no trace, na especificação, no decision log
nem nos registros de reconciliação, e nunca faz commit: entrega os atos de git para a pessoa (uma tag
no commit de partida e o commit da remoção, restrito aos pares removidos).

```sh
archive.py --check <project-root> (--all | <slug>...) [--target <key>]    # quais sairiam, e por que as outras não
archive.py --remove <project-root> (--all | <slug>...) [--target <key>]   # relê tudo, remove os pares elegíveis
```

O escopo nunca é inferido: só a pessoa diz o que arquivar, e por isso a skill é fechada ao modelo.

### `/siegard-telemetry` e `telemetry.py`
Escreve um relatório de **como** um trecho de trabalho aconteceu (agentes disparados, custo em
tokens e em tempo, recusas, execuções, paradas, decisões, compactações de contexto), contado a
partir do disco e das transcrições de sessão do Claude Code. Todo número sai de um arquivo.

```sh
telemetry.py --probe <project-root> --since <instante|last> [--until …]   # as transcrições podem ser lidas? não grava nada
telemetry.py <project-root> --since <instante|last> [--until …] [--transcripts DIR]
```

A skill roda o `--probe` primeiro e cita a saída para a pessoa antes da leitura completa. Das
transcrições só saem contagens, nomes, instantes, um digest de cada prompt de agente e as linhas de
comando dos scripts do framework, nunca texto. `--since last` continua de onde o relatório anterior
parou. Saída: `<telemetry_root>/<carimbo>.json` e um relatório Markdown ao lado.

O contrato atual é `siegard-telemetry/19`. Cada versão acrescentou uma contagem; um relatório
antigo continua sendo a contagem que era, e a ausência de um campo nele não significa zero. Entre as
seções:

| Seção | O que conta |
|---|---|
| agentes e `agent_totals` | Cada agente disparado, em qualquer profundidade, com tokens e tempo; `repeats_earlier` marca o **mesmo prompt** entregue ao **mesmo tipo de agente**. Dentro de um worktree, `harness.worktree` o nomeia. |
| compactações | Cada compactação, com a skill em que caiu. |
| decisões | As entradas de decision log da janela, cada uma com `outcome`: se o campo ainda lê como o commit gravou e, se não, por qual rota mudou. Só as rotas `corrective` e `hand-edit` são uma pessoa discordando; `framework` é o próprio framework se revisando. |
| `recommendations` | Cada linha `recommended:` e `decided:` dos logs de orquestração, por critério e por tipo (`derived`/`judged`), com o commit que a gravou e o seguinte que tocou a iniciativa. Se a porta foi tomada, quem lê o commit é uma pessoa. Linhas fora da forma aparecem em `malformed`. |
| `handoffs` | Os turnos humanos curtos que foram confirmações (`commit_authorization`, `go_ahead`, `choice_by_label`), os commits feitos entre uma skill e o turno seguinte (`in_span_commits`, com `authorized_by`), e as perguntas (`questions`), sem texto. |
| `handoff_form` | A forma de cada mensagem que a pessoa respondeu, lida pelas mesmas funções do `handoff.py --check`, e `stop_checks`, o que o hook `Stop` mediu. |
| contexto por chamada | O que cada chamada de uma sessão orquestradora leu e o que as compactações deixaram. |
| `proofs` | As revisões da janela, o estado de cada critério que o passe de cobertura nomeou e os vínculos que um teste decide no trace. |

### `project.py`

```sh
project.py <project-root>                                   # lê e valida o siegard.json, imprime cada campo
project.py --here                                           # sem raiz nomeada: o topo do git do diretório atual
project.py <project-root> --declared-tests <target> <caminho>...   # quais caminhos são testes declarados
```

O único leitor do `siegard.json`, contra `schemas/project.json`. Toda skill roda isto primeiro. Com
`--here`, imprime antes `project_root: <caminho>`, e recusa quando o topo do git não tem
`siegard.json`: nada é criado numa raiz que ninguém nomeou. Um standard por target sai como
`standard <target>: <caminho>` (ou `declared none`), e os testes como `tests <target>: …`. Se
encontrar uma cópia das regras de sessão no `CLAUDE.md` da raiz do projeto (pela linha-marcador),
imprime uma linha `rules:` sugerindo removê-la, porque as regras já chegam por hook (§4). É um aviso,
nunca uma recusa.

### Os hooks do plugin
O plugin registra hooks no Claude Code (`hooks/hooks.json`). Todos agem só num projeto que declara
`siegard.json`, e nenhum derruba uma sessão: quando não conseguem ler algo, deixam o ato seguir.

| Hook | Evento | O que faz |
|---|---|---|
| `rules.py` | `SessionStart`, `SubagentStart` | Coloca `hooks/rules.md` literalmente no contexto da sessão e de cada agente (§4). |
| `drift.py` | `SessionStart` | Coloca na abertura da sessão a contagem de drift por classe (do `trace.py --check`) e o que o `--owed` ainda deve, como contagem e nunca como lista. Com um goal armado, avisa quando a versão do plugin carregada é outra ou quando o goal está ligado a outra sessão. |
| `goal_stop.py` | `Stop` | Com um goal armado, responde a cada parada pelo `goal.py --state` (acima). Sem goal, ou quando o goal acabou de terminar, passa a parada primeiro ao grant e depois ao `handoff_stop.py`. Uma parada liberada apaga o registro de turno da sessão. |
| `after_tool.py` | `PostToolUse` (Bash, `Skill`, `Agent`) | Grava o registro de turno da sessão em `siegard/turn/<sessão>.json`, no diretório do git: o instante em que uma skill que termina num render foi invocada (a `route` do turno) e, com grant armado, as obrigações que o grant respondeu e quem as cumpriu. |
| `handoff_stop.py` | (chamado pelo `goal_stop.py`) | Mede a mensagem em que a sessão parou com as funções do `handoff.py --check` e acrescenta uma linha a `siegard/handoff-checks.jsonl`, no diretório do git, com `route` e `rendered` lidos do registro de turno. Por padrão só mede; com `SIEGARD_HANDOFF_STOP=enforce`, bloqueia uma vez o turno que rodou uma skill de rota e não guardou nenhum render. A forma da mensagem (tamanho, abertura, recomendação) é medida e nunca bloqueia. |
| `commit_check.py` | `PreToolUse` (Bash) | Num `git commit`, recusa uma linha `decided:` ou `recommended:` fora da forma, uma `decided:` julgada sem grant que cubra aquela iniciativa, e um commit que registra uma parada levando mais que a medição. |
| `bounds.py` | `PreToolUse` (Bash, `Write`, `Edit`, `MultiEdit`) | Com goal ou grant armado, recusa `git push`, criar, renomear ou apagar branch, `rebase`, `commit --amend`, `reset --hard`, `filter-branch`, `filter-repo`, `stash` (exceto `list` e `show`), e `add`/`commit` de tudo o que é rastreado (`-A`, `-u`, `.`, `-a`). Em qualquer estado, recusa uma escrita à mão de `siegard-trace.json`, do `plan.json` de uma iniciativa, do `delivery.json` de uma entrega e de qualquer coisa em `run/`, que são arquivos de script. |

Fora de um goal ou grant, push, branch e reescrita dependem só das suas palavras na sessão.

#### O que responde a uma parada
Cada parada passa pelas verificações abaixo, nesta ordem; a primeira que bloqueia responde, e
uma parada com trabalho em segundo plano em andamento não é lida.

| Verificação | Quando age | Bloqueia? | Onde registra | Controle |
|---|---|---|---|---|
| Goal (`goal.py --state`) | goal armado para esta sessão | `not yet`: sim, até três vezes; `state A`, `state B` ou pausado: não, e a parada segue para a checagem do handoff | registro do goal | nenhum |
| Obrigação do grant | grant armado e um `take:` ou `judge:` impresso e não cumprido | uma vez | `grant-checks.jsonl`, com `mode` | `SIEGARD_GRANT_STOP` (padrão `enforce`; `measure` só registra) |
| Checagem do handoff | toda parada que entrega decisão ou cujo turno rodou uma skill de rota | uma vez, só se a rota não guardou render | `handoff-checks.jsonl`, com `mode`, `route` e `rendered` | `SIEGARD_HANDOFF_STOP` (padrão `measure`; `enforce` bloqueia) |

As variáveis ficam no `env` das configurações do Claude Code do projeto, por exemplo em
`.claude/settings.local.json`: `{"env": {"SIEGARD_HANDOFF_STOP": "enforce"}}`.

### Os outros scripts
Os scripts de cada fase têm o seu capítulo: `spec.py` (§5), `plan.py` (§6), `deliver.py` e `run.py`
(§7), `trace.py` (§9 e §10, e as formas de adoção no §11).

### Fatias de contrato (`--contract`)
`plan.py --contract <branch>` e `deliver.py --contract <branch>` imprimem um pedaço
autossuficiente de um schema (com todas as referências internas já resolvidas), para que um agente
receba exatamente os campos que escreve, e não o schema inteiro. Economiza contexto e impede que o
agente preencha campos que não são dele.

### Códigos de saída (todos os scripts)
| Código | Significado |
|---|---|
| `0` | Íntegro / nada encontrado / feito / aceito. |
| `1` | Problemas encontrados (arquivo inválido, drift, um finding que nenhum bind fechou, um registro recusado, uma porta ou um portão que responde `refuses`, `not yet`). |
| `2` | Não pôde rodar (pasta ausente, entrada quebrada). |

Uma saída diferente de zero de um comando de **consulta** (como `--check`, `--owed` ou
`door.py --check`) não é uma falha da skill: ela **é** a resposta.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Adoção e levantamento (`/survey`)](11-adocao-e-levantamento.md) · Próximo: [Os agentes](13-os-agentes.md)
