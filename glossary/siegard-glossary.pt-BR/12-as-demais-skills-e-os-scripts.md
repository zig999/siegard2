> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Adoção e levantamento (`/survey`)](11-adocao-e-levantamento.md) · Próximo: [Os agentes](13-os-agentes.md)

## 12. As demais skills e os scripts auxiliares

### O handoff: a mensagem final de uma skill, e o que ela recomenda
**O que é.** *Handoff* é a última mensagem de uma invocação de skill, aquela em que o controle
volta para você: o relatório, ou a parada que encerrou a execução antes do fim. Desde a 5.5.0 a
forma dessa mensagem é fixada pela especificação do framework (SPEC-006) e vale para todas as
skills que relatam algo.
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

**Nas palavras da pessoa** (desde a 5.7.1 e a 5.7.2). Cada item da abertura diz **o que ele é
para você**, em palavras simples no idioma da conversa: o que precisa ser feito antes de um passo
nomeado rodar; o que pode ser feito sem que nada espere por isso; o que só você decide; o que é
sugerido e por quê. Nunca com uma palavra do framework: "devido", "oferecido", "porta" e
"critério" são vocabulário deste glossário e dos `SKILL.md`, não da abertura. Quem nunca abriu o
arquivo de uma skill lê a abertura inteira. Quando o relatório recomenda uma porta, a abertura já
diz qual e por quê, antes de qualquer explicação, e não só no fechamento.

Depois vem o relatório na ordem que o `SKILL.md` daquela skill define, no idioma da conversa, com
cada termo do Siegard explicado uma vez, na primeira ocorrência. Saídas de comando, notas e
entradas de log são citadas literalmente, sem tradução.
**Porta (door).** Cada ato que o handoff entrega a você, como uma invocação pronta para colar.
**Recomendação.** Quando há mais de uma porta e um **fato no disco** decide entre elas, o handoff
nomeia a porta recomendada com quatro coisas: a porta, o **critério**, o fato que decide e o fato
que inverteria a recomendação. Sem as quatro, nenhuma porta é recomendada. O critério vem de uma
lista fechada:

| Critério | Quando vale |
|---|---|
| `precondition unmet` | a skill da porta recusaria as entradas do jeito que a árvore está (por exemplo, um incremento de prova sem nenhum registro `remainder: testable`) |
| `rule violated` | a porta quebra uma regra do framework (por exemplo, gravar na especificação um fato tirado só da asserção de um teste) |
| `already done` | o trabalho da porta já está na árvore |
| `reading paid twice` | o **mesmo arquivo** seria lido por dois julgamentos: entre duas leituras sobre os mesmos arquivos, a que se paga uma vez é preferida à que se pagaria duas. Duas invocações sobre arquivos **diferentes** são pagas uma vez cada, e a ordem entre elas é uma decisão de custo, que é sua |

**O nome do critério é só para o log** (desde a 5.7.2). No handoff, as quatro coisas aparecem
como frases nas suas palavras: qual porta, por que ela, o que no disco diz isso e o que mudaria a
recomendação. O nome em inglês do critério só é escrito tal como está na linha `recommended:` do
`orchestration.md` (§7). Um rótulo como "Critério: reading paid twice" na prosa é o registro
vazando para a conversa.

**O que nunca é recomendado.** O pedido e o seu escopo; uma contradição entre escopo e
especificação; duas leituras da mesma evidência (o código está certo ou a especificação?); se um
finding importa ou qual rota ele merece; e qualquer decisão de custo, como tentar de novo. Nesses
casos o handoff entrega as portas e não nomeia nenhuma. Os revisores continuam entregando só
evidência, sem veredito, severidade ou ranking.
**Finding não para nada.** Um finding de revisão nunca é uma parada. O handoff só chama algo de
parada quando o `SKILL.md` da skill o chama assim. Quando diz que um passo pode seguir, lista as
verificações que rodou, com a saída de cada uma.

### `/siegard-config`
Escreve ou atualiza o `siegard.json` a partir do que a pessoa diz. É o único que escreve esse
arquivo.

**Skills fechadas ao modelo.** `/siegard-config`, `/siegard-standard`, `/siegard-archive` e
`/clarify-request` só podem ser invocadas por uma pessoa (`disable-model-invocation: true`): o
modelo não as dispara por conta própria, nem de dentro de outra skill. Quando uma skill precisa de
uma delas, entrega a invocação pronta para a pessoa colar. O critério é quem consegue declarar a
entrada: em todas as quatro, só a pessoa.

### `/clarify-request` — reescrever um pedido como uma instrução validada
**O que é.** Desde a 5.16.0, uma skill que recebe um pedido em linguagem natural ("olha essa
implementação e vê se segue o standard que a gente definiu") e o devolve como **uma única
instrução precisa** para o Claude Code. Desde a 5.34.0, uma instrução que só lê ou planeja
(`ANALYZE`, `PLAN`) é executada no mesmo turno, só por leitura; as demais são entregues **sem
execução**. Ela lê o projeto para resolver
referências ("isso", "o standard", "o que decidimos"), pergunta à pessoa só as decisões que são
dela, e mantém exatamente a intenção, o modo e o escopo do pedido.
**Por que existe.** Um pedido vago é executado com palpites, e os palpites não aparecem em lugar
nenhum. A regra que a skill serve é uma só: **esclarecer o que a pessoa quis dizer, nunca
completar o que ela não decidiu**. Uma instrução mais clara que o pedido e também maior que ele
passou de esclarecer para decidir.
**O que ela nunca faz.** Não escreve arquivo nenhum, nem quando executa a instrução (`Write`, `Edit` e `NotebookEdit` ficam
bloqueados enquanto ela roda) e não roda comando nenhum além do validador. Não reescreve um pedido
que já é a invocação de uma skill (`/nome …`): essas skills leem as palavras da própria pessoa, e
algumas tomam essas palavras como autorização. Também não serve para planejar nem especificar
trabalho (isso é `/plan-work` e `/analyse`).
**A ordem:**
1. **Ler a operação do pedido** — qual operação, sobre qual alvo, em qual **modo**. O modo é o que
   as palavras dizem e nunca é elevado: pedir para olhar não é pedir para mudar.
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
8. **Executar, só lendo** (desde a 5.34.0) — quando o validador imprime `in-turn` (`ANALYZE`,
   `PLAN`), a skill executa a instrução no mesmo turno, só com `Read`, `Grep` e `Glob`: nada é
   rodado, enviado ou consultado, nenhuma skill é invocada, e o que a instrução não diz não é
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
impõe), e uma linha sem fonte é apagada. A base de uma suposição é um caminho com linha, as
palavras da pessoa ou uma mensagem anterior marcada como da pessoa ou do assistente (desde a
5.33.0); as palavras do assistente servem de base só para aquilo a que uma referência aponta,
nunca para uma decisão. Uma linha
que o executor cumpriria sem que lhe dissessem ("tenha cuidado", "siga as convenções") não é
escrita. Uma linha `DISCOVERY` diz o que encontrar, nunca o que fazer se não encontrar: uma
condição de parada que a pessoa não pediu é uma decisão que não é da instrução.
**Os modos** (`MODE`):

| Modo | O que autoriza |
|---|---|
| `ANALYZE` | Investigar, explicar, diagnosticar, revisar, comparar, validar. Nenhum arquivo do projeto muda; um comando que só observa (a suíte existente, um linter, uma consulta de leitura) cabe aqui. |
| `PLAN` | Propor uma solução ou um plano. O projeto não muda. |
| `OPERATE` | (desde a 5.17.0) Rodar um comando ou enviar uma requisição cujo efeito **não é observação** — criar ou alterar dados, um deploy, uma instalação, uma exclusão fora dos arquivos do projeto — sem modificar os arquivos do projeto. O efeito é nomeado em `TASK` e limitado em `CONSTRAINTS`. |
| `IMPLEMENT` | Mudar o projeto dentro do escopo esclarecido. |
| `IMPLEMENT_AND_VALIDATE` | Mudar o projeto e verificar a mudança (testes, checagens, build, lint ou uma execução). |

Os três primeiros não autorizam mudança nos arquivos do projeto, e por isso precisam carregar em
`CONSTRAINTS` uma linha que limite o projeto inteiro, começando com `Do not modify the project`
ou `Do not modify code`. Uma linha que limita menos (`Do not modify the CSS file`) deixaria o resto
autorizado. Os dois últimos não podem carregar esse limite, porque ele contradiria o modo.
**Ato sobre os dados versus capacidade** (desde a 5.17.0). Um pedido formulado como um ato sobre
os dados do sistema ("remova os clientes inativos") é aplicado a esses dados, e a instrução diz
isso. Um pedido formulado como uma capacidade ("vamos permitir remover…") constrói o meio e não
aplica nada. Uma chamada que muda estado, como um `POST` que cria uma cobrança, nunca é
`ANALYZE`, qualquer que seja o verbo do pedido.

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
do significado de cada uma e do que cada modo autoriza. `clarify.py` confere uma instrução contra
ele:

```sh
clarify.py <arquivo>      # confere a instrução contida no arquivo
clarify.py -              # confere a instrução lida da entrada padrão
```

Recusa uma seção que o contrato não nomeia, uma seção vazia, uma fora da ordem, texto antes da
primeira seção, a falta de `MODE` ou `TASK`, um modo de leitura sem o limite sobre o projeto
inteiro e um modo de mudança com esse limite. Saída `0` = bem formada, com uma linha dizendo se a
skill executa a instrução no mesmo turno (`in-turn`) ou a entrega (`hand-over`), decidida só pelo
modo e pela lista `x-executes-in-turn` do contrato; `1` = um problema por linha, `2` = não pôde
rodar. Se a instrução preserva o que a pessoa quis dizer não é decidível por
script, e não é verificado.

### `/siegard-standard`
Redige o standard do projeto a partir do que as ferramentas do projeto já impõem (linter,
compilador, verificador de segredos) e do que uma pessoa declara. Nunca inventa uma regra.

### `/siegard-status`
Um panorama amigável e só de leitura do projeto inteiro: integridade da especificação, decisões
recentes, tarefas pendentes e notas `BLOCKING` de cada iniciativa ativa, drift do trace por classe,
trabalho não commitado. Cada afirmação vem com o comando que a sustenta. Termina com a invocação
mais pronta para rodar. Desde a 5.5.0 essa invocação é uma recomendação no sentido do handoff
(acima): traz o critério, o fato que decide e o fato que a inverteria. A skill continua não
decidindo nada por você, porque nomear uma porta não é tomá-la. Desde a 5.6.0 a abertura deriva
os atos devidos do `git status` por raiz: uma raiz com alteração pendente é um ato devido, e a
linha nomeia as skills que se recusam a começar sobre ela (a especificação trava `/analyse`,
`/plan-work` e `/deliver-scope`; a raiz de trabalho, `/plan-work` e `/deliver-scope`; a raiz de
entrega, `/implement-task`, `/review-change` e `/deliver-scope`; a raiz de código de um target,
`/implement-task` e `/deliver-scope`). Drift e findings nunca são devidos. Um par que um
`/reconcile` anterior já julgou e nenhum bind fechou (`reported` no `--owed`) aparece como decisão
pendente com as duas portas — `/plan-work` corretivo se o nó está certo, `/analyse` se o código
está — e nenhuma recomendação, porque é juízo seu. A invocação de `/reconcile` vem do
`--reconcile-set`, nunca de uma composição da skill.

O que mudou depois da 5.6.0:
- **Uma rodada só** (5.6.1). Os comandos rodam como um único lote, cada saída num arquivo, e nunca
  um `head` sobre uma saída: cortar a saída obrigaria a rodar de novo um comando que já custou a
  sua leitura. Na mesma versão, os scripts passaram a ler o frontmatter dos registros de
  reconciliação uma vez por processo (pela libyaml, quando o Python a tem); num corpus grande, o
  `--owed` e o `--convergence` caíram de dezenas de segundos para cerca de um ou dois.
- **Um `--check` por target** (5.7.1). Em cada topo do git, o `--check --reconcile-set` roda sobre
  a raiz de um target nomeado, uma vez por target, nunca sobre o topo (ver "As duas grafias de um
  caminho", §4). A recomendação que fecha o relatório é repetida na abertura.
- **A abertura nas palavras da pessoa** (5.7.2). Um ato devido abre com o que ele destrava ("antes
  que `/plan-work` ou `/deliver-scope` possam rodar: …"), e o conjunto de reconciliação, tal como
  está, é a porta pronta. Os arquivos que um commit devolveria ao conjunto são o fato que
  inverteria a recomendação, nunca um motivo para esperar.
- **O standard fixado** (5.12.0). O relatório cita as linhas do `--outstanding` sobre registros que
  não fixam o standard declarado, como fato, nunca como passo pulado.

### `/siegard-progress`
Uma tabela compacta das tarefas de uma iniciativa (status derivado + porquê), feita para rodar
repetidamente (por exemplo, com `/loop`). Desde a 5.14.0 repassa as linhas do `--outstanding`
sobre registros que não fixam o standard declarado.

### `/siegard-archive`
Remove da árvore de trabalho iniciativas **fechadas** (as pastas de work e delivery), depois de
verificá-las mecanicamente. Nunca toca no arquivo do projeto, no trace, na especificação, no
decision log nem nos registros de reconciliação, e nunca faz commit: entrega os comandos git para a
pessoa.

### `/siegard-telemetry` e `telemetry.py`
Escreve um relatório de **como** um trecho de trabalho aconteceu (agentes disparados, custo em
tokens e em tempo, recusas, execuções, decisões, compactações de contexto), contado a partir do
disco e das transcrições de sessão do Claude Code.

```sh
telemetry.py --probe <project-root> --since last        # as transcrições podem ser lidas?
telemetry.py <project-root> --since 2026-09-29T00:00:00Z [--until …]
```

Saída: `<telemetry_root>/<carimbo>.json` e um relatório Markdown ao lado.

Desde a 5.5.0 (contrato `siegard-telemetry/9`), o relatório tem a seção `recommendations`. Ela lê
cada linha `recommended:` dos `orchestration.md` sob a raiz de entrega e conta as linhas por
critério. Ao lado de cada linha põe o commit que a gravou e o primeiro commit seguinte que tocou
a iniciativa. Se a porta recomendada foi tomada, o script não calcula: o commit seguinte é a
evidência, e quem o lê é uma pessoa. Linhas que não seguem o formato aparecem em `malformed`.

O contrato atual é `siegard-telemetry/12`. Cada versão acrescentou uma contagem; um relatório
antigo continua sendo a contagem que era, e a ausência de um campo nele não significa zero.

| Versão | O que acrescentou |
|---|---|
| `/10` (5.9.0) | `handoffs`: todo turno humano curto que foi uma **confirmação** — autorização de commit (`commit_authorization`), sinal para seguir (`go_ahead`) ou escolha por rótulo (`choice_by_label`) —, com a skill a que respondeu, os segundos de espera e se a mensagem respondida perguntava algo. Por sessão, `skill_calls`, `short_turns` e `confirmations`. Nenhum texto sai das transcrições. |
| `/11` (5.11.0) | `commits` por sessão e `handoffs.in_span_commits`: cada `git commit` ou `git push` que a sessão rodou depois de chamar uma skill e antes do turno seguinte da pessoa, com a skill, se tinha pathspec, se fez push e o que o autorizou (`authorized_by`: `typed`, `loop`, `summary` ou `none`). As notas ganham `live`, que diz se o plano delas ainda está aberto. |
| `/12` (5.18.0) | `prompt_sha256` em cada agente e `repeats` em cada total: uma **repetição** (`repeats_earlier`) é o **mesmo prompt** entregue ao **mesmo tipo de agente**, e não mais a mesma descrição, que não é comparável. Um relatório rodado dentro de um git worktree nomeia o worktree em `harness.worktree` e só admite as sessões cujo diretório de trabalho está dentro dele. |

**Decisões revisadas** (desde a 5.15.0). A seção de decisões não dá uma porcentagem de decisões
revisadas. Ela conta as que continuam como foram gravadas e, ao lado, as revisadas, cada uma
nomeada com a rota e o tempo até a primeira revisão. Só as rotas `corrective` e `hand-edit` são
uma pessoa discordando; `framework` é o próprio framework se revisando.

### `project.py`

```sh
project.py <project-root>
```

Lê e valida o `siegard.json` e imprime cada campo declarado, um por linha. Toda skill roda isto
primeiro. Se encontrar uma cópia antiga das regras no `CLAUDE.md` da raiz do projeto, imprime uma
linha `rules:` pedindo que ela seja removida (as regras agora chegam por hook).

### Fatias de contrato (`--contract`)
`plan.py --contract <branch>` e `deliver.py --contract <branch>` imprimem um pedaço
autossuficiente de um schema (com todas as referências internas já resolvidas), para que um agente
receba exatamente os campos que escreve, e não o schema inteiro. Economiza contexto e impede que o
agente preencha campos que não são dele.

### Códigos de saída (todos os scripts)
| Código | Significado |
|---|---|
| `0` | Íntegro / nada encontrado / feito. |
| `1` | Problemas encontrados (arquivo inválido, drift, um finding que nenhum bind fechou, um registro recusado). |
| `2` | Não pôde rodar (pasta ausente, entrada quebrada). |

Uma saída diferente de zero de um comando de **consulta** (como `--check` ou `--owed`) não é uma
falha da skill: ela **é** a resposta.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Adoção e levantamento (`/survey`)](11-adocao-e-levantamento.md) · Próximo: [Os agentes](13-os-agentes.md)
