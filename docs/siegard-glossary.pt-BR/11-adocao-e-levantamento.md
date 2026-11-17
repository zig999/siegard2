> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Reconciliação (`/reconcile`)](10-reconciliacao.md) · Próximo: [As demais skills e os scripts auxiliares](12-as-demais-skills-e-os-scripts.md)

## 11. Adoção e levantamento (`/survey`)

### Adoção
**O que é.** A rota para **código escrito antes do Siegard** (ou fora dele): o projeto já tem um
sistema funcionando, e quer passar a mantê-lo sob a especificação.
**O desafio.** Não há especificação, não há plano, não há registro de entrega e não há trace.
Alguém precisa ler o código, dizer o que ele faz em termos de negócio, transformar isso em nós e,
finalmente, vincular cada nó aos arquivos que de fato o contêm.
**Os passos**, um contexto delimitado por vez:

1. `trace.py --untraced <target>` — no início, todo arquivo está `unsurveyed` (ou `uncertified`,
   se for um teste que o target declara em `tests`). Declarar os testes antes do primeiro
   levantamento é o que os mantém fora das áreas.
2. **`/survey`** — agentes leem o código, área por área, e devolvem o **material de
   levantamento**: os fatos de domínio que o código exibe, cada um ao lado do arquivo onde foi
   lido.
3. **`/analyse`** sobre esse material — escreve os nós e o **ledger**, que diz em qual nó foi parar
   cada fato do material, ou por que ficou de fora.
4. **`/reconcile` como adoção**, com o ledger — cada arquivo é lido contra os candidatos em que os
   seus próprios fatos foram parar. A primeira adoção cria o `siegard-trace.json`.
5. Ler o que voltou: candidatos `unheld`, findings `contradicts` e `unstated` → de volta ao
   `/analyse`; `restates` → remover o comentário e reconciliar de novo.
6. Só então, os incrementos seguintes: o que os testes declarados afirmam, lido pela forma de
   testes do `/survey` como **material de intenção**, e a documentação existente (manuais,
   wikis), cada um como material de um incremento comum do `/analyse`.

O `/adopt-scope` executa os passos 2 a 4 de ponta a ponta, sob um único pedido (verbete
próprio, abaixo).

**Por que a documentação vem depois.** O primeiro material de um sistema adotado é lido **só do
código**, descrevendo comportamento observável. Uma documentação pode estar desatualizada; o código
é o que de fato roda.
**Quando está completa.** A adoção está completa quando o `--untraced` não mostra nenhum arquivo
`unsurveyed` e o `--convergence` não mostra nenhum nó `unreached`. Isso é calculado, nunca
registrado, e nada espera por isso. Um teste `uncertified` não impede a conclusão: um teste é
certificado quando a pessoa o oferece, nunca é uma dívida.

### `/survey` — o levantamento
**O que é.** A skill que lê código que nenhuma entrega escreveu e grava o **material de
levantamento**, um arquivo por área, e entrega a invocação do `/analyse` que o transformará em nós.
**As duas formas.** A **forma de código** (o padrão) lê o código e grava material de
levantamento. A **forma de testes**, pedida pela pessoa, lê os testes que o target declara em
`tests` e grava **material de intenção** (verbete próprio, abaixo). Um teste diz o que o código
deveria fazer e um levantamento lê o que ele faz, por isso as duas formas nunca dividem um arquivo.
A forma de testes exige os testes declarados; um target que não os declara é uma parada que
entrega o `/siegard-config`.
**Entradas obrigatórias.** A raiz do projeto; o target; o **slug** do levantamento (uma pasta em
`siegard-survey/`, no topo do git — slug já usado é parada); e as **áreas**, nomeadas pela pessoa,
cada uma com um nome curto e os caminhos ou pastas que contém. Na forma de código, testes não são
área: um teste é material de certificação, não de levantamento. Na forma de testes, a área são os
testes declarados que esses caminhos contêm, e nada mais. Um arquivo em duas áreas é parada.
**Pré-condição.** Todo arquivo de toda área precisa estar commitado.
**A ordem:**

```mermaid
flowchart LR
    n0["situate"] --> n1["delegate"] --> n2["hold"] --> n3["report"] --> n4["stop"]
```

1. **situate** — roda `spec.py --digest` (as identidades já existentes são o "contexto até agora",
   para que a mesma coisa receba o mesmo nome) e `trace.py --untraced` (o ponto de partida). Para
   cada área, roda `trace.py --area`: os arquivos que ele lista **são** a área — nunca uma listagem
   própria da skill —, e os testes declarados que ele deixa de fora são nomeados no relatório (na
   forma de testes, a área é justamente essa segunda metade da saída).
2. **delegate (delegar)** — dispara um agente por área — `domain-surveyor` na forma de código,
   `test-intent-reader` na forma de testes —, em ondas de no máximo vinte (§10, "Ondas de
   delegação"), e salva cada retorno **literalmente** como `siegard-survey/<slug>/<area>.md`.
3. **hold (conferir)** — `trace.py --survey` confere cada arquivo contra o contrato que o seu
   `contract_version` nomeia (`schemas/survey.json` ou `schemas/intent.json`) e conta as linhas de
   fato por cabeçalho. Um arquivo recusado é refeito pelo agente, nunca consertado à mão (um fato
   acrescentado à mão seria um fato que ninguém leu).
4. **report** — relata as áreas, os arquivos que o `--area` listou e os testes que deixou de fora,
   as contagens, tudo o que ficou em "observado e não decidido aqui" (dois comportamentos do código
   que discordam), os arquivos lidos fora das áreas, e entrega a invocação do `/analyse` com os
   arquivos do levantamento como material.

**O que nunca faz.** Não lê documentação como material; não lê um teste como material de
levantamento nem o código como material de intenção; não escreve nó, ledger nem vínculo; não faz
commit.

### `domain-surveyor` — o agente de levantamento
Lê **uma área** de código e devolve o material de levantamento no formato de
`schemas/survey.json`. Só lê (ferramentas `Read`, `Grep`, `Glob`); devolve texto, e a skill grava.
Sua regra principal: **código é evidência; texto nunca é**. Comentários, docstrings, READMEs e
mensagens de commit dizem o que alguém acreditava; o agente lê os desvios, as comparações e as
respostas do código. Toda recusa entra com a resposta que ela devolve, e a ordem das verificações é
lida operação por operação, nunca generalizada.
**O que não é fato de domínio.** O que a implementação escolheu (rotas de transporte, fiação do
framework, eventos de log, limites de desempenho) vai para `## Outside the domain`. O mesmo vale
para um texto que só nomeia um controle (o rótulo de um botão, coluna, aba ou menu, um nome
acessível, um placeholder) e para o ajuste que um cliente faz das próprias requisições (tempo de
cache, número de tentativas). Já um texto que muda o que uma pessoa pode saber ou fazer (uma
mensagem de recusa ou de falha, o rótulo de um vocabulário fechado, um aviso de resultado) é fato.

### `test-intent-reader` — o agente da forma de testes
Lê **uma área de testes declarados** e devolve material de intenção no formato de
`schemas/intent.json`: o que o código deveria fazer, segundo o que os testes **afirmam**. Só lê
(ferramentas `Read`, `Grep`, `Glob`); devolve texto, e a skill grava. A evidência é a asserção,
nunca o título do teste. O código só é aberto para dizer qual arquivo cada teste governa.

### Material de levantamento (survey material)
**O que é.** Um arquivo markdown por área, com frontmatter `contract_version: siegard-survey/1`,
`target`, `files` (os arquivos da área) e `read_outside_area` (outros arquivos abertos para
entender a área, cada um com o porquê — lidos, mas sem fatos atribuídos).
**Corpo:** seis cabeçalhos, nesta ordem:

| Cabeçalho | O que contém |
|---|---|
| `## Facts` | Os fatos de domínio que o código exibe. |
| `## Answers` | Toda recusa com a resposta que ela devolve; formatos, limites e ordem de verificação de cada operação. |
| `## Vocabularies` | Os vocabulários fechados (listas de status, tipos, códigos). |
| `## Upstream artifacts` | O que sistemas externos impõem (tabelas, colunas, códigos, tópicos). |
| `## Outside the domain` | O que foi lido e deixado de fora por não ser domínio. |
| `## Observed and not decided here` | Comportamentos observados que o levantamento não decide (por exemplo, dois trechos que discordam). |

Um cabeçalho sem nada a dizer leva a linha `None.`.

**Linha de fato (fact line).** Um item de lista de primeiro nível (`- `) sob um dos quatro
primeiros cabeçalhos, terminando com o caminho onde foi lido, entre crases. Um item recuado
pertence ao fato acima dele. Exemplo:

```markdown
## Answers

- Placing an order for a customer with an overdue invoice is refused with `CUSTOMER_BLOCKED`. `src/orders/place.ts`
```

### Material de intenção (intent material)
**O que é.** O material lido dos **testes declarados** de um target pela forma de testes do
`/survey`: o que o código **deveria** fazer, cada fato ao lado do teste onde foi lido **e** do
arquivo de código que ele governa. Contrato: `schemas/intent.json` (`siegard-intent/1`).
**Quando aparece.** Nunca no primeiro material de um sistema adotado, que é lido só do código: o
material de intenção é um dos incrementos que vêm depois da adoção, e o que ele corrige entra como
uma mudança comum à especificação.
**Formato.** O frontmatter traz `contract_version`, `target`, `tests` (todo teste lido, cada um no
escopo de testes declarado), `files` (todo arquivo de código que algum fato governa, nenhum deles
um teste) e, opcionalmente, `read_outside_area`. O corpo tem os mesmos seis cabeçalhos do material
de levantamento, na mesma ordem.
**Linha de fato.** Nomeia, entre crases, o teste onde o fato foi lido **e** cada arquivo de `files`
que ele governa. Uma linha que não nomeia teste ou não nomeia arquivo governado é recusada.
**Para que a adoção o usa.** O `/analyse` escreve sobre ele o mesmo ledger, e a adoção sobre esse
ledger entrega a cada **arquivo governado** os nós em que os seus fatos foram parar. Um teste é só
o lugar onde um fato foi lido: nunca é um arquivo do conjunto julgado.

### Ledger (livro-razão do material)
**O que é.** O arquivo `ledger.md`, escrito pelo `/analyse` **ao lado do material** que leu (nunca
dentro da especificação), que diz para onde foi **cada linha** do material. Contrato:
`schemas/ledger.json` (`siegard-ledger/1`). O material pode ser de levantamento, de intenção ou
qualquer outro arquivo entregue ao `/analyse` (prosa, por exemplo). No material de levantamento e
de intenção, as linhas contadas são as linhas de fato; num arquivo sem contrato de material do
Siegard, o `trace.py` enumera as linhas de item (uma linha que abre com negrito, um item de lista
no começo da linha, uma linha de corpo de tabela ou a primeira linha de um parágrafo).
**Por que existe.** Sem ele, um fato que o material declarava e a análise não transformou em nó
simplesmente desapareceria — e só seria redescoberto, arquivo por arquivo e a alto custo, pelos
juízes da adoção, como finding `unstated`. O ledger torna essa perda visível **antes** da adoção:
toda linha cai num nó, é deixada de fora com um motivo declarado, ou fica **em aberto** com o que
falta responder.
**Formato.** O frontmatter tem `material` (os arquivos que o ledger cobre, com caminho relativo à
pasta do ledger), `digests` (o `sha256:` de cada arquivo como estava quando o ledger foi respondido;
obrigatório para material sem contrato, porque um digest que não bate mais significa que os
números de linha deixaram de localizar os itens) e `entries`, uma entrada por linha:

| Campo | Significado |
|---|---|
| `at` | A linha: `<arquivo do material>:<número da linha>`. |
| `node` | O nó cujos campos agora contêm o fato. Se um fato cai em vários nós, uma entrada por nó. |
| `outside` | Por que nenhum nó contém a linha: conhecimento de implementação, fato que pertence a outro contexto ou sistema, comportamento observado e não decidido, ou uma linha que não declara fato. Uma única justificativa que um revisor possa rejeitar. |
| `open` | O que da linha ainda falta responder, e que um incremento seguinte da análise responde. Uma linha respondida em parte cai nos nós que a respondem e fica `open` pelo resto. |

Uma entrada tem `node`, `outside` ou `open`, nunca dois deles. Uma linha sem entrada é um fato que
a análise deixou cair, e o ledger é recusado.
**Para que a adoção o usa.** O `--stage --adopt --ledger` lê o ledger para entregar a cada juiz,
no seu pacote, **só os candidatos em que os fatos daquele arquivo foram parar** — em vez de todos
os candidatos do incremento. Isso reduz muito o que cada juiz precisa ler. A adoção só aceita um
ledger cujo material todo seja de levantamento ou de intenção e que não tenha nenhuma linha `open`.
**Por quanto tempo existe.** O ledger vive enquanto o material está em uso. Com alguma linha `open`,
ou enquanto uma adoção ainda vai lê-lo, ele é commitado junto com a especificação. Sem linha aberta
e sem adoção que o leia (algum material é prosa), o commit do incremento que o fechou o remove, e a
mensagem desse commit traz a saída do `trace.py --ledger`. Um ledger lido por uma adoção é removido
pelo commit dessa adoção; uma adoção parada o deixa. A última linha do `--ledger` diz qual dos
casos vale: `ledger: keep` ou `ledger: remove`. As versões anteriores ficam no histórico do git.
**Não confundir com.** O decision log ao lado de cada nó (§5), que registra **o que** foi decidido
sobre um nó. O ledger registra **para onde** foi cada linha do material, e não guarda fato nenhum.

### `trace.py --area`, `trace.py --survey` e `trace.py --ledger`

```sh
trace.py --area <target-root> <caminho-ou-pasta> ...  # os arquivos de uma área, sem os testes declarados
trace.py --survey <material.md> ...          # confere material contra o seu contrato e conta fatos por cabeçalho
trace.py --ledger <ledger.md> <spec-root>    # confere o ledger contra o material e os nós
trace.py --untraced <target-root> [--all]    # os arquivos rastreados que nenhum vínculo nomeia, por estado
```

- `--area` lista os arquivos rastreados que os caminhos de uma área contêm, deixa de fora os
  testes que o target declara (e os nomeia) e também deixa de fora um submódulo. Para quando um
  teste declarado é nomeado sozinho como arquivo da área: quem o nomeou queria uma certificação.
  Se o target não declara testes, o script diz isso e não deixa nada de fora.
- `--survey` recusa um arquivo cujo frontmatter não cumpre o contrato, cujo `files` não é a área,
  ou cujo corpo não tem um dos cabeçalhos — e, no material de levantamento, um arquivo que seja
  teste declarado; no material de intenção, um teste que o target não declara, um arquivo
  governado que seja teste, ou uma linha de fato sem teste ou sem arquivo governado. Íntegro, conta
  as linhas de fato por cabeçalho e aponta os arquivos da área que nenhum fato menciona (isso é um
  dado a relatar, não um erro: o arquivo pode não conter nada de domínio) e, no material de
  intenção, os testes em que nenhum fato foi lido.
- `--ledger` recusa um ledger ao qual falte uma linha, uma entrada que não aponte para uma linha
  do material, um nó que não existe e um digest que não bate mais com o arquivo. Íntegro, imprime
  `ledger sound:` com as contagens (linhas que caíram em nós, deixadas de fora, em aberto), as
  linhas ainda `open` com o que falta em cada uma, os motivos de exclusão agrupados por contagem
  (o maior primeiro), o conjunto de arquivos que o material leu e os candidatos por arquivo — o que
  a adoção vai usar —, e termina com `ledger: keep` ou `ledger: remove`.
- `--untraced` lista os arquivos rastreados sob o target que nenhum vínculo nomeia, por diretório,
  com a contagem de cada estado (`holds-nothing`, `outside`, `uncertified`, `unsurveyed`; ver §9).
  Não recusa nada: a maioria dos arquivos de um sistema real não carrega fato de domínio.

### O stage da adoção

```sh
trace.py --stage <target-root> <spec-root> <slug> <workspace> \
    --adopt --ledger <ledger.md> [<arquivos>] [--outside <arquivo> ...] [--certify <arquivo-de-certificações>]
trace.py --stage <target-root> <spec-root> <slug> <workspace> \
    --adopt --node <candidato> ... [--outside <arquivo> ...] [--certify <arquivo-de-certificações>]
```

- O ledger só é aceito quando todo o material é de levantamento ou de intenção e nenhuma linha
  está `open`; senão, o stage não roda e diz por quê.

- O conjunto de arquivos é, por padrão, o das áreas do material — no material de intenção, os
  arquivos que ele governa, nunca os testes — (ou o subconjunto nomeado).
- Um arquivo que o target declara como teste é recusado no conjunto: um teste nunca é código
  adotado. A recusa diz para tirá-lo do conjunto e entrega, pronta, a entrada de `--certify` que o
  oferece como prova de um nó (`{node: …, proof: […], step: …}`).
- Cada arquivo recebe os candidatos em que o ledger colocou os seus fatos. Um arquivo que nenhum
  fato menciona não recebe juiz e fica sem vínculo.
- O índice de candidatos continua listando todos os candidatos, com os arquivos de cada um, para
  um fato que o juiz encontre e o seu pacote não resolva.
- **Sem ledger**, cada candidato é nomeado com `--node`, e o juiz de todo arquivo lê todos eles.
- Não é preciso trace para começar. Nenhum candidato é omitido nem respondido por execução: é a
  leitura dele que decide se será vinculado.
- `--outside` nomeia arquivos (configuração, fiação) que ficam fora do julgamento — inclusive um
  submódulo — e é passado junto com a adoção do contexto a que esses arquivos pertencem. Um
  teste declarado nunca é `outside`: fica `uncertified` até que uma certificação o nomeie.

### Como uma adoção termina para cada candidato
- **Liberado** → vinculado aos arquivos cujo juiz leu o fato ali, e a nenhum outro.
- **`unheld`** → nenhum juiz encontrou o fato em nenhum arquivo do conjunto, e nada foi encontrado
  contra ele. Ou o código não carrega esse nó, ou ele está em arquivos fora deste conjunto: cabe à
  análise revisitar, ou à adoção desses outros arquivos.
- **`contradicts`** → o nó descreve mal o código: volta ao `/analyse`.

### `/adopt-scope` — a adoção de ponta a ponta
**O que é.** A skill que leva **um contexto** de código adotado pela rota inteira — `/survey` sobre
as áreas do pedido, `/analyse` sobre o material que ele escreveu, `/reconcile` como adoção sobre o
ledger —, fazendo commit entre os passos. Uma invocação = um contexto adotado. É o segundo
orquestrador, construído como o `/deliver-scope` (§7).
**Autorização.** Só quando a mensagem da própria pessoa pede a rota inteira para aquele contexto
(citada literalmente). Um pedido que nomeia uma só fase recebe aquela skill, não esta. Commits
sempre restritos a caminhos (pathspec), um por passo, com a mensagem
`adopt-scope <slug>: survey|analyse|adopt|measure` — nunca cria branch, nunca faz push, nunca
reescreve histórico.
**A diferença em relação ao `/deliver-scope`.** Esta skill **invoca o `/analyse`**, porque
escrever a especificação a partir do código adotado é a sua rota. O que faz as vezes da revisão
que uma pessoa daria ao diff antes do commit é a divulgação completa: o ledger (todo fato cai num
nó ou fica de fora com motivo), o decision log ao lado de cada nó, o validador e o relatório. A
pessoa revisa o intervalo de commits depois. Em compensação, **nunca** invoca `/plan-work`,
`/implement-task`, `/review-change` nem `/deliver-scope`: a adoção não muda código, e um
comportamento errado que ela encontre é um novo pedido.
**Entradas.** O pedido (literal), a raiz do projeto, o target, o slug do contexto e as áreas; e,
opcionalmente, os arquivos `outside` e as certificações, sempre nas palavras do pedido. Um slug cujo
log de orquestração (`siegard-survey/<slug>/orchestration.md`) já existe é uma **retomada**: a
skill continua do passo cujo commit o log não tem, e o relatório diz isso.
**Antes de tudo.** O `spec.py` precisa passar sobre uma raiz de especificação commitada, e o
`git status --porcelain` sobre a especificação, a raiz de código do target, o `siegard-trace.json`,
o `siegard-reconcile` e o `siegard-survey/<slug>` não pode imprimir nada. A skill commita onde o
`HEAD` já está; começar numa branch própria é ato da pessoa, oferecido na abertura do relatório.

```mermaid
flowchart TB
    n0["gate"] --> n1["survey"] --> n2["commit"] --> n3["analyse"] --> n4["commit"] --> n5["adopt"] --> n6["commit"] --> n7["measure"] --> n8["commit"] --> n9["report"] --> n10["stop"]
```

**Duas regras.** **Colar, nunca compor**: cada skill termina entregando a próxima invocação
pronta, e esta skill a usa literalmente, preenchendo só as lacunas que o pedido cobre. **Toda
decisão de rota é a resposta de um script** (`--survey`, `--ledger`, `spec.py`, o fold,
`--reconciliation`, `--untraced`): uma parada de script é parada desta skill.
**Os passos.**
1. **survey** — invoca o `/survey` com as áreas do pedido; commit de `siegard-survey/<slug>` como
   `adopt-scope <slug>: survey`.
2. **analyse** — invoca o `/analyse` que o relatório do survey entregou; commit da raiz de
   especificação e de `siegard-survey/<slug>` (nós, logs e ledger são um incremento) como
   `adopt-scope <slug>: analyse`.
3. **adopt** — invoca o `/reconcile` como adoção que o relatório da análise entregou, com o
   `outside` e as certificações do pedido; commit do `siegard-trace.json`, do `siegard-reconcile` e
   de `siegard-survey/<slug>` (já sem o ledger, que a adoção remove) como `adopt-scope <slug>: adopt`.
4. **measure** — `telemetry.py --probe` desde o início do passo 1, o anúncio da leitura e a
   telemetria; commit da raiz de telemetria como `adopt-scope <slug>: measure`. Uma sonda que não
   consegue ler é uma linha no relatório, nunca uma parada.

**Log.** Mantém `orchestration.md` em `siegard-survey/<slug>/`, uma linha por passo (o que foi
invocado, o hash do commit e o resultado) — um marcador, nunca um nó. É o único lugar em que as
decisões da própria execução (slug derivado, target decidido, passo retomado, parada final)
sobrevivem à conversa.
**Paradas.** Toda parada de uma skill interna encerra a execução, com as portas repassadas
literalmente; nenhuma é contornada nem repetida. Também param: um ledger que ainda tem linha `open`,
um campo que o `siegard.json` não declara e uma alteração pendente que a skill não fez. Quando o
relatório que parou recomendava uma porta, o log ganha uma linha
`recommended: <porta> — <critério> — <fato que decide>` (§12). Candidatos `unheld`, findings
(`contradicts`, `unstated`, `restates`), fatos deixados de fora pelo ledger, decisões registradas e
uma certificação recusada **não** param nada: são divulgação, e vão para o relatório.
**O relatório.** Sai por `handoff.py --prepare`/`--render` (§12): onde o `HEAD` estava no início,
cada commit da execução e o intervalo do `git log` que os contém (é a revisão, e é da pessoa), cada
entrada decidida e não recebida, as contagens do `--survey`, a saída do `--ledger`, as decisões
registradas, as contagens da adoção, o `trace.py --untraced` depois do bind, o recibo da telemetria
e o que a skill nunca fez.

### Outras "adoções" que não são esta rota
**Não confundir com.**
- **A adoção que uma entrega pede.** Quando o implementador de uma tarefa descobre que o código já
  cumpre a tarefa, o registro de implementação leva `stands`; se o trace não tem os vínculos, o
  gravador do registro entrega uma porta de `/reconcile` como adoção, cujos candidatos são os nós
  da tarefa que nenhum dos arquivos vincula (§7, §10). É a mesma adoção do `/reconcile`, mas sem
  levantamento nem ledger: os arquivos são os que o implementador encontrou.
- **O teste "adotado" por uma entrega.** O `deliver.py --test-owner` responde `adopt` quando uma
  suíte fica vermelha num teste de outra tarefa cujos planos donos estão todos fechados: a entrega
  atual assume esse teste e o reescreve (§7). Isso é sobre um teste, não sobre código que nenhuma
  entrega escreveu.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Reconciliação (`/reconcile`)](10-reconciliacao.md) · Próximo: [As demais skills e os scripts auxiliares](12-as-demais-skills-e-os-scripts.md)
