# Glossário do Siegard (pt-BR)

Um guia em linguagem simples para as palavras que o Siegard usa: o que cada uma significa, onde
você a encontra e como ela aparece em disco ou na linha de comando.

Descreve o Siegard **4.21.3**. É a tradução de `glossary/siegard-glossary.md`; onde as duas
versões divergirem, vale a inglesa. E onde esta página divergir do `SKILL.md` de uma skill, do
`--help` de um script ou de um schema em `schemas/`, valem esses arquivos: são eles que de fato
rodam. Esta página os explica; não os substitui.

Nomes de campos, flags, comandos, classes e valores (`--stage`, `held_at`, `contradicts`,
`orphaned`…) ficam em inglês, porque são exatamente o que você digita ou lê nos arquivos. As
saídas reais de scripts também ficam em inglês.

---

## Como usar esta página

- **Seção 1** é o panorama de um minuto. Leia primeiro; todo o resto se pendura nele.
- **Seções 2–9** agrupam os termos pelo momento em que você os encontra: configurar o projeto,
  escrever a especificação, planejar, entregar, revisar, o trace, a reconciliação e os comandos
  auxiliares.
- **Seção 10** lista todos os agentes (os "juízes" e "produtores" a quem o Siegard delega).
- **Seção 11** traduz palavras informais usadas em conversa (`unfold`, `refold`, `certificate`,
  "comment findings", "emitted-text findings") para os termos oficiais.
- **Seção 12** percorre um exemplo completo — uma correção feita à mão — do início ao fim.
- **Seção 13** é um índice alfabético que aponta para cada verbete.

Os comandos estão escritos como as skills os executam:

```sh
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/<script>.py ...
```

`${CLAUDE_PLUGIN_ROOT}` é a pasta onde o plugin do Siegard está instalado (contém `bin/`,
`schemas/`, `skills/`, `agents/` e `hooks/`). Para encurtar, esta página escreve
`trace.py ...` onde a forma completa é `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py ...`.

---

## 1. O panorama de um minuto

O Siegard é um framework para o Claude Code que mantém **uma única fonte escrita da verdade sobre
o que o negócio decidiu** (a *especificação*) e faz cada linha de código responder a ela.

```
          o que o negócio decidiu                    o que é construído
 ┌──────────────────────────────┐        ┌────────────────────────────────┐
 │  ESPECIFICAÇÃO (nós, .md)    │        │   CÓDIGO-FONTE (seu repo)      │
 │  rules/, domain/, contracts/ │        │   src/..., tests/...           │
 └──────────────┬───────────────┘        └───────────────▲────────────────┘
                │                                        │
   /analyse  ───┘   /plan-work → /implement-task → /review-change
  (escreve-a)       (plano)      (escreve código+testes) (julga)
                                         │
                                         ▼
                        siegard-trace.json  ("o trace")
             nó  ⇄  arquivo(s), cada um fixado por um digest SHA-256
                                         │
                   depois, alguém edita um arquivo à mão…
                                         ▼
                  trace.py --check  →  "drift"  →  /reconcile
```

Cinco ideias carregam quase todo o resto:

| Ideia | Em uma frase |
|---|---|
| **Especificação** | Arquivos markdown ("nós") que dizem o que o negócio decidiu. É a autoridade. |
| **Plano** | Tarefas recortadas de um escopo, cada uma nomeando os nós da especificação que implementa. |
| **Entrega** | Registros do que foi escrito para cada tarefa, dos testes que provam e da revisão. |
| **Trace** | Um arquivo dizendo qual arquivo de código contém o fato de qual nó, com as impressões digitais de ambos. |
| **Reconciliação** | A rota que relê código alterado fora de uma tarefa e refaz o vínculo. |

E uma regra por baixo de tudo: **um julgamento nunca é feito pelo mesmo contexto que produziu a
coisa julgada**. É por isso que o Siegard dispara agentes separados ("juízes") e salva o que eles
devolvem literalmente, sem alteração.

---

## 2. Configurando um projeto

### `siegard.json` — o arquivo do projeto
**O que é.** O único arquivo em que o projeto declara suas raízes, para que ninguém precise
redigitá-las. Fica na raiz do projeto e é commitado.
**Quem escreve.** Só o `/siegard-config`. Nunca edite à mão.
**Exemplo.**

```json
{
  "specification_root": "specification",
  "targets": { "backend": "backend" },
  "work_root": "work",
  "delivery_root": "delivery",
  "standard": { "backend": "backend/standard.yaml" },
  "telemetry_root": "telemetry",
  "edits_freely": ["frontend"]
}
```

Toda skill começa rodando `project.py <project-root>` para ler este arquivo.

### Raiz do projeto (project root)
A pasta que contém o `siegard.json`. Toda skill pede por ela e nunca a adivinha.

### Target, raiz de código do target (target source root)
Um **target** é uma base de código em que o projeto entrega (`backend`, `frontend`…), nomeada
por uma chave em `targets`. A **raiz de código do target** é a pasta dele (`targets["backend"]`).
Quase todo caminho nos registros do Siegard é escrito *relativo à raiz de código do target*:
`src/orders/place.ts`, e não `backend/src/orders/place.ts`.

### Topo do git (git toplevel)
A pasta de topo do repositório git que contém o target. O trace (`siegard-trace.json`), os
registros de reconciliação (`siegard-reconcile/`) e os registros de checagem (`siegard-check/`)
moram lá, ao lado do `siegard.json`.

> Existem duas grafias de um caminho, e confundi-las é um erro comum. O que o `trace.py`
> **imprime** é escrito a partir do topo do git (`backend/src/case.ts`). Tudo o que você
> **escreve** (conjuntos de arquivos, premissas, findings) é escrito a partir da raiz de código
> do target (`src/case.ts`). O `--stage` recusa a grafia errada e diz qual é a certa.

### `specification_root`, `work_root`, `delivery_root`, `telemetry_root`
As pastas onde moram a especificação, os planos, os registros de entrega e os relatórios de
telemetria. `work_root` e `delivery_root` são *contêineres*: uma subpasta por iniciativa, com o
mesmo slug nas duas.

### Iniciativa
Uma unidade de trabalho de desenvolvimento, do plano à entrega. Tem um **slug** (um nome em
kebab-case como `order-placement`) e ganha `work/<slug>/` e `delivery/<slug>/`.

### Slug
Um nome reduzido a kebab-case (`case-transitions`, `hand-fix-invoicing`). Usado para nomes de
arquivos de nós, iniciativas, execuções e reconciliações. Um slug já usado é recusado — registros
nunca são sobrescritos.

### Standard (o registro de regras)
**O que é.** As regras do próprio projeto sobre como seu código é organizado (nomes, camadas,
lint…), num arquivo YAML/JSON que o projeto escreve. O Siegard entrega o *contrato*
(`schemas/standard.json`), nunca uma regra.
**Onde você o encontra.** O `/siegard-standard` faz um rascunho; o `/review-change` e o
`/check-source` o leem; o `/implement-task` executa os comandos dele.
**Exemplo.**

```yaml
contract_version: siegard-standard/1
standard: backend
summary: How the backend's TypeScript is arranged and checked.
rules:
  - id: ARC-01
    statement: A service or controller never constructs a dependency.
    because: A constructed dependency cannot be replaced in a test.
    decided_by: reading
    applies_to:
      - { under: src, suffix: .service.ts, nested: true }
  - id: STK-02
    statement: The code compiles with no type error.
    because: A type error is a defect the compiler already found.
    decided_by: tool
    tool: typecheck
    applies_to:
      - { under: src, suffix: .ts, nested: true }
commands:
  - step: install
    role: install
    command: npm ci
    timeout_seconds: 300
  - step: typecheck
    command: npx tsc --noEmit
    timeout_seconds: 120
  - step: test
    role: suite
    command: npm test
    timeout_seconds: 600
```

`deliver.py --standard <arquivo>` valida o standard e imprime o que cada fase de uma entrega vai
executar.

Termos dentro do standard:

| Termo | Significado |
|---|---|
| `rules[].id` | Identificador permanente que um finding cita (`ARC-01`). Nunca renomeado, nunca reutilizado. |
| `decided_by: reading` | Uma pessoa ou um agente precisa *ler* o código para saber se a regra vale. |
| `decided_by: tool` | Um comando decide (`tool` nomeia o step). Nenhum agente lê. |
| `applies_to` | Até onde a regra alcança: `under` uma pasta, arquivos terminados em `suffix`, `nested` ou não. |
| `commands[]` | Os comandos do próprio projeto, cada um com nome de `step`, o `command` exato e um `timeout_seconds`. |
| `role` | `prepare` (preparar um worktree novo), `install`, ou `suite` (os testes que provam o trabalho). |
| `decides` | Architecture Constraints que este step verifica (ver §3). |
| `presupposes` | Arquivos que as regras supõem já existirem (um `package.json`, um `tsconfig.json`). |
| `dependencies` | A **lista de permissão** de pacotes que uma entrega pode instalar sem perguntar. |
| `elsewhere` | O que o standard deliberadamente não contém, e onde isso mora. |

### `edits_freely`
Uma lista de targets cuja *superfície* (rótulos, cores, espaçamento, ordem de colunas) uma pessoa
pode mudar sem tarefa. Muda só um relatório: o `trace.py --check` deixa de listar drift `code`
para arquivos sob esses targets (e diz quantos segurou; `--all` mostra todos). Não relaxa nenhuma
regra sobre fatos de negócio.

### O arquivo de regras (`hooks/rules.md`)
O conjunto curto de regras de sessão que o Siegard coloca em toda sessão e todo agente, via hook.
As mais importantes: qual **rota** uma mudança toma (abaixo), nunca editar à mão arquivos
derivados, nunca afirmar um fato de negócio que a especificação não contém, e **código-fonte não
leva comentários**.

### Rotas
As seis maneiras de uma mudança entrar num projeto. Quem escolhe a rota é uma pessoa; ela nunca é
inferida.

| O que mudou | Rota |
|---|---|
| Um fato de negócio (um status, uma recusa, quem pode ver o quê) | `/analyse` → `/plan-work` → `/implement-task` → `/review-change` |
| A superfície de uma capacidade que a especificação já contém (uma tela, um estado) | `/plan-work` → `/implement-task` → `/review-change` |
| Um comportamento errado em código já entregue | **incremento corretivo** do `/plan-work` → `/implement-task` |
| **Só um comentário** (prosa no código violando a regra de comentários) | remover o comentário à mão, depois `/reconcile` sobre aquele arquivo |
| **Só a superfície** (rótulo, cor, espaçamento) | editar direto, num target declarado `edits_freely` |
| **Código que nenhuma entrega escreveu** (adotando o Siegard) | `/analyse` a partir só do código → `/reconcile` como **adoção** |

### A regra de comentários
**Código-fonte não leva comentários**, com duas exceções: uma diretiva consumida por uma
ferramenta nomeada (`// eslint-disable-next-line …`) e a justificativa que o standard exige ao
lado de uma supressão. O que um comentário diria vai para o lugar certo: o fato para o seu nó, a
justificativa para o decision log, o vínculo arquivo-nó para o trace. Um comentário que repete o
fato de um nó é reportado por um juiz como finding `restates` (ver §8).

---

## 3. A especificação

### Especificação, raiz da especificação
O conjunto de arquivos markdown que diz o que o negócio decidiu, sob uma pasta. Cada arquivo é um
**nó**. É validada pelo `spec.py`. É a autoridade: quando o código e um nó discordam, o nó é o que
o negócio decidiu.

### Nó (node)
Um arquivo markdown da especificação: frontmatter YAML (os campos) mais um corpo curto
(`## Description`). Exemplo — um nó de Regra:

```markdown
---
type: invariant
statement: A hypothesis MUST hold at least one piece of evidence before its case resolves.
constrains:
  - domain/troubleshooting/hypothesis
---

## Description

No case resolves on an unsupported explanation.
```

(O conteúdo da especificação é sempre em inglês — é uma regra do próprio Siegard.)

### Identidade
O caminho do nó a partir da raiz da especificação, sem `.md`. O arquivo acima, guardado em
`specification/rules/troubleshooting/hypothesis-requires-evidence.md`, tem a identidade
`rules/troubleshooting/hypothesis-requires-evidence`. É pela identidade que todo registro, plano e
trace nomeia um nó.

### Contexto delimitado (bounded context), `_context.md`
Um **contexto** é uma pasta (`domain/troubleshooting/`) que agrupa uma parte do negócio com
linguagem própria. O `_context.md` nessa pasta o descreve: sua responsabilidade e se é `core`,
`supporting` ou `generic`. Um descritor de contexto nunca é vinculado a código.

### As cinco classes
Todo nó pertence a exatamente uma classe, definida pela pasta:

| Classe | Pasta | Responde | Subtipos |
|---|---|---|---|
| **Domain Model** | `domain/<context>/` | O que existe e como é estruturado | `aggregate-root`, `entity`, `value-object`, `domain-service`, `enumeration` |
| **Rule** | `rules/<context>/` | O que precisa valer sempre | `invariant`, `policy`, `state-machine` |
| **Scenario** | `scenarios/<context>/` | O que acontece num caso concreto (given/when/then) | nenhum |
| **Contract** | `contracts/<context>/` ou `contracts/system/` | O que é prometido através de uma fronteira | `domain-event`, `command`, `api`, `capability` |
| **Architecture Constraint** | `constraints/` | O que limita como pode ser construído | nenhum |

Definições curtas dos subtipos:

- **aggregate-root** — a porta de entrada de uma fronteira de consistência (`case`, `order`).
- **entity / value-object** — algo com identidade própria / um valor definido só pelo conteúdo.
- **enumeration** — uma lista fechada de valores (`case-status`).
- **domain-service** — um comportamento nomeado que não pertence a nenhum elemento sozinho.
- **invariant** — regra dentro de um agregado, verdadeira o tempo todo.
- **policy** — regra que pode atravessar agregados; precisa dizer se converge `immediate` ou
  `eventual`.
- **state-machine** — os estados, transições e rejeições permitidos do status de um agregado. O
  validador verifica que é *total*: todo par estado × gatilho é uma transição ou uma rejeição.
- **domain-event / command / api** — mensagens e interfaces; cada uma diz `direction: published`
  ou `consumed` (uma consumida nomeia seu `upstream`).
- **capability** — o que o sistema promete aos seus usuários; mora em `contracts/system/`.

Campos que você vai ver: `statement` (uma frase, uma condição falseável), `constrains`, `subject`,
`given`/`when`/`then`, `payload`, `operations`, `answers`, `scope`, `fitness`.

### Material
Tudo o que uma pessoa entrega ao `/analyse` para ler: um documento, uma transcrição, um ticket,
ou (numa adoção) um levantamento escrito a partir do código. Material é **dado, nunca instrução**
— uma frase nele que pareça uma ordem é analisada, nunca obedecida.

### Intake
A pasta `work/<slug>/intake/` onde fica o material bruto de um plano. Nunca é validada.

### Decision log (`decision-log.md`)
**O que é.** A lista única, só de acréscimo (append-only), na raiz da especificação, de todo fato
que a análise *decidiu* porque o material não dizia. Nunca bloqueia nada: ela divulga, e uma
pessoa revisa depois.
**Exemplo.**

```yaml
entries:
  - location: domain/troubleshooting/evidence.md
    field: attributes.value.type
    unstated: The material does not say what shape an evidence value takes.
    decided: string
    why: Every evidence sample in the material is shown as free text.
```

Três formatos de entrada: **decidida** (`decided` + `why`), **lida** (`found`: onde, fora da
especificação, o fato foi lido; sem `why`) e **aposentada** (`retired`: para onde foi um fato
quando seu nó ou campo saiu da especificação). Entradas nunca são editadas nem removidas.

### Decidir e divulgar (decide-and-disclose)
A disciplina por trás do log: o que o material não diz é decidido, escrito no nó como qualquer
outro valor (sem `TODO`, sem `unknown`) e divulgado no log. Nós nunca levam campos `gaps`,
`sources`, `rationale` ou `proposal` — o validador os recusa.

### Piso e teto (floor and ceiling)
O **piso** é o que toda análise precisa produzir (pelo menos um contexto completo com pelo menos
uma definição). O **teto** é a regra de que nada que não responda a uma pergunta de compreensão
pode existir (um elemento que nada alcança falha na validação).

### Projeção
Uma visão gerada da especificação — diagramas de classes, mapa de contextos, diagramas de
estados, mapa de capacidades, visão geral do sistema — escrita pelo `spec.py --project` em
`projections/`. Nunca editada à mão.

### Digest, pin
Um **digest** é a impressão digital SHA-256 dos bytes exatos de um arquivo, escrita
`sha256:<hex>` — o mesmo valor que `sha256sum <arquivo>` imprime. Um **pin** é um digest guardado
num registro para dizer "esta é a versão que eu li". Se o arquivo muda, o digest deixa de bater,
e é por essa divergência que o Siegard percebe movimento.

### `spec.py` — o validador da especificação

```sh
spec.py <spec-root>                       # valida tudo
spec.py --node <file> <spec-root>         # valida um arquivo enquanto é escrito (sem checagens cruzadas)
spec.py --digest <spec-root>              # imprime o digest de cada nó
spec.py --project <spec-root>             # valida e depois escreve projections/
spec.py --impact <id>[,<id>...] <spec-root>  # um salto em volta de cada nó, nas duas direções
spec.py --shape [--of <id>,...] <spec-root>  # mede o tamanho dos nós; nunca recusa
```

- **Entrada:** a raiz da especificação (e uma identidade de nó ou um arquivo, em algumas formas).
- **Saída:** "sound" ou uma lista de problemas (saída `0` íntegra, `1` problemas, `2` não pôde
  rodar).
- **`--impact`** é o **conjunto de impacto**: todo nó que um nó referencia, todo nó que o
  referencia e toda entrada do decision log sobre ele. O planejamento usa isso para achar nós
  candidatos.
- **`--shape`** é um relatório, nunca uma recusa: tamanho dos statements, statements com mais de
  uma frase, frases repetidas entre nós, prosa que nomeia nós. `--of` marca os nós pelos quais
  você responde, para que apareçam mesmo além do corte.

---

## 4. Planejamento (`/plan-work`)

### `/plan-work`
Transforma um **escopo** declarado mais uma especificação válida num **plano**: inventário,
épicos e tarefas como arquivos markdown em `work/<slug>/`. Também tem três modos especiais: o
**incremento corretivo**, o **incremento de prova** e o **fechamento** de um plano.

### Escopo
O que a pessoa pede que seja construído, com as palavras dela. O planejamento nunca o amplia por
conta própria.

### Nós do plano: inventário, épico, tarefa
| Tipo | Caminho | O que contém |
|---|---|---|
| **inventory** | `inventory/<slug>.md` | O que já existe onde a mudança cai: `modules`, `conventions` (cada uma com onde foi vista), `must_not_duplicate`, `risks` |
| **epic** | `epic/<slug>.md` | Um grupo de tarefas e os nós pelos quais responde (`covers`), mais o que deixa de fora de propósito (`uncovered`, cada um com o porquê) |
| **task** | `task/<epic>/<slug>.md` | Um `objective` falseável, seus `criteria`, os nós que `implements`, seus `depends_on` |

Exemplo de tarefa:

```markdown
---
title: Record an opened case
summary: The entry point that persists an opened case.
objective: An opened case is persisted and retrievable by its case id.
criteria:
- Opening a case returns its case id.
implements:
- domain/troubleshooting/case
---
## What it is
…
## Notes
None.
```

Campos de tarefa que você vai encontrar:

| Campo | Significado |
|---|---|
| `objective` | O único resultado que a tarefa entrega. Dois resultados = duas tarefas. |
| `criteria` | Condições, cada uma falseável sozinha, sob as quais o objetivo está cumprido. |
| `implements` | Os nós da especificação que a tarefa implementa (decididos pelo binder, abaixo). |
| `depends_on` | Tarefas cujo resultado esta usa como base (dependência, nunca ordem). |
| `produces` | Arquivos que a entrega precisa criar (a metade verificável do objetivo). |
| `stands` | Arquivos onde a implementação já existe — usado pelo incremento de prova, que só escreve testes. |
| `reference` | Material que a entrega precisa ler, como um mockup em `intake/layout/`. |

Não existe campo de status, prioridade ou estimativa: o progresso mora no git e nos registros de
entrega.

### `covers` / `uncovered`
O `covers` de um épico lista os nós pelos quais ele responde. Cada um precisa ser implementado por
uma de suas tarefas ou listado em `uncovered` com um `why` — uma sobra deliberada e declarada,
nunca uma lacuna.

### Binder e notas
O agente **execution-contract-binder** decide, por tarefa, quais nós ela `implements`. Ele nunca
reescreve a tarefa: toda divergência volta como uma **nota** em `## Notes` da tarefa, com uma
**classe**:

| Classe | Pergunta que responde | Efeito |
|---|---|---|
| `compound` | Um critério afirma duas condições? | A tarefa é recortada de novo, uma vez. |
| `blocking` | Algum nó *afirma* algo que a tarefa contradiz ou excede? | **Para a tarefa.** Só uma pessoa resolve. Aparece como `BLOCKING, from the specification — …` |
| `unstated` | A tarefa depende de um fato que nenhum nó afirma? | Vai para o **unstated-fact-decider**; a especificação ganha o fato. |
| `underdetermined` | Existe uma implementação errada que ainda passa em todos os critérios? | Fica registrada; o autor de testes precisa escrever um teste que a exclua. |
| `remainder` | Uma cláusula de uma regra pertence a outra tarefa? | Registra onde ela pertence. |
| `advisory` | Qualquer outra coisa. | Só informação. |

### Fato não declarado (unstated), unstated-fact-decider
Quando o planejamento encontra um fato que nenhum nó afirma, isso não é uma parada. O agente
**unstated-fact-decider** recebe só o fato — nunca a tarefa que o revelou ("decidido às cegas") —
e devolve as edições de nó mais uma entrada no decision log. Um fato que a especificação
*contradiz* nunca é decidido: isso é `blocking`.

### Âncora, re-bind
Quando o `plan.py` deriva o `plan.json`, guarda o digest de cada nó que cada tarefa implementa (a
**âncora**). Se um nó muda depois do planejamento, a tarefa "espera um **re-bind**": o binder
precisa ler o nó de novo antes que alguém entregue essa tarefa.

### Incremento corretivo
Um plano de uma tarefa só para **um comportamento errado em código entregue**: sem levantamento,
sem decomposição. É a rota para um bug encontrado ao rodar o sistema — nunca uma correção digitada
direto no arquivo.

### Incremento de prova (proof increment)
Um plano cujas tarefas escrevem **só testes**, uma tarefa por fato: fatos que um teste finito pode
decidir, já contidos em código entregue (`stands`), provados por nenhum teste. A revisão que lê a
prova então **certifica** o nó (ver §8).

### Fechando um plano, `closure.md`
Quando a pessoa declara uma iniciativa encerrada, o `/plan-work` escreve `closure.md` na raiz de
trabalho. Um plano fechado não aceita mais tarefas; o `/siegard-archive` pode depois removê-lo da
árvore.

### `plan.json`
O índice derivado de um plano (nós e arestas). Escrito pelo `plan.py`, nunca à mão.

### `plan.py` — o validador do plano

```sh
plan.py <work-root> <spec-root>           # valida e escreve plan.json
plan.py --check <work-root> <spec-root>   # valida e compara, não escreve nada
plan.py --node <file> <work-root>         # valida um arquivo
plan.py --standard <file> --against DIR <work-root> <spec-root>
                                          # também confere o que o standard pressupõe vs `produces`
plan.py --unplanned <work-root-parent> <spec-root>
                                          # quais nós nenhuma iniciativa jamais nomeou (consulta, saída 0)
plan.py --contract <branch> [--fields a,b | --without a,b]
                                          # imprime uma fatia de plan-node.json para um agente
```

---

## 5. Entregando (`/implement-task`, `/deliver-scope`)

### `/implement-task`
Entrega **uma tarefa**: escreve o código, escreve os testes, instala pacotes permitidos, roda os
steps do projeto até compilar e a suíte passar, escreve os registros, valida-os e vincula o trace.
Sua ordem:

```
situate → set up → implement → build → prove → suite → validate → bind → report → stop
```

Dois desses passos são de outros agentes (`task-implementer` escreve o código, `test-author`
escreve os testes) — em contextos separados, para que o código e seus testes não concordem "por
construção".

### Raiz de entrega e registros de entrega
`delivery/<slug>/` contém três tipos de registro (markdown com frontmatter):

| Registro | Caminho | Escrito por | Contém |
|---|---|---|---|
| **implementation** | `implementation/<epic>/<task>.md` | `/implement-task` | os arquivos escritos, cada critério respondido, cada nó respondido |
| **proof** | `proof/<epic>/<task>.md` | `/implement-task` | cada teste, o que prova, o que o faria falhar |
| **review** | `review/<name>.md` | `/review-change` | os passes que rodaram, findings, cobertura |

Exemplo de registro de implementação:

```yaml
target: backend
title: Record an opened case
summary: The entry point that persists an opened case.
task: sha256:fd8b6fdb…          # pin do arquivo da tarefa como foi lido
files:
- path: src/troubleshooting/case.ts
  effect: holds the case aggregate and its status vocabulary
criteria:
- criterion: Opening a case returns its case id.
  met: true
  how: the constructor takes the id and the module answers with it
nodes:
- node: domain/troubleshooting/case
  encoded_at:
  - src/troubleshooting/case.ts
  how: the case's identity and status vocabulary are the shape this module holds
```

Campos que vale conhecer:

| Campo | Significado |
|---|---|
| `encoded_at` | O(s) arquivo(s) onde o fato de um nó agora mora. **É isso que é vinculado no trace.** Ausente significa que o nó governou o trabalho sem que um fato próprio chegasse ao código ("honrado, não codificado"). |
| `how` | Como o código responde ao nó ou ao critério — algo que o leitor pode ir olhar. |
| `inferences` | O que o implementador decidiu sem que nada dissesse, e a partir de quê. |
| `divergences` | Onde o código se afasta da tarefa, do inventário ou do standard, com o porquê. |
| `deferred` | O que foi encontrado e deliberadamente não mudado. |
| `preserved` | O que precisava continuar funcionando, escrito antes da mudança. |
| `installed` | Pacotes adicionados (cada um precisa estar na lista de permissão do standard). |
| `tests[].proves` / `fails_when` | O que um teste demonstra / o que teria de quebrar para ele falhar. |
| `tests[].demonstrates` | Um nó que o teste alega provar — uma *alegação* que a revisão certifica ou não. |
| `untested` | Comportamento deixado sem prova, dito com clareza. |
| `contested` | Onde o autor dos testes acredita que a implementação está errada. |
| `not_applicable` | Casos-limite que a tarefa não levanta, cada um com o porquê. |

### Execução capturada, `run.py`
**O que é.** O único jeito de o Siegard executar um comando. O `run.py` roda os comandos do
próprio projeto (sem shell), guarda tudo o que eles imprimiram e registra o resultado. Recusa um
nome de execução que já existe, para que toda tentativa continue legível.

```sh
run.py <delivery-root> --run <slug> --cwd <target-source-root> --timeout-seconds 600 \
    --step install="npm ci" --step test="npm test" [--excerpt 40]
```

- **Entrada:** onde escrever, um slug novo para a execução, a pasta onde rodar, um timeout, um ou
  mais steps.
- **Saída:** `run/<slug>/run.json` mais um log por step e um log combinado. Saída `0` todos os
  steps passaram, `1` um step falhou / estourou o tempo / não foi encontrado, `2` não pôde rodar.
- Um step que falha para a execução; os steps seguintes são registrados como `not_run`.
- `--excerpt N` imprime o final do step que falhou, só na tela.

Resultados de step: `passed`, `failed`, `timed_out`, `not_found`, `not_run`.

### `delivery.json`
O índice derivado de uma raiz de entrega. Escrito pelo `deliver.py`, nunca à mão.

### Substrato, `presupposes`, `produces`
**Substrato** é o que precisa existir antes de uma tarefa poder ser entregue — os arquivos que o
standard `presupposes` ou que uma tarefa anterior `produces`. Uma entrega sobre substrato ausente
é recusada antes de escrever qualquer coisa.

### Conjunto entregável, `--outstanding`
As tarefas que podem ser entregues **agora**: ainda sem registro, dependências entregues e
provadas, substrato presente, nenhuma nota `BLOCKING` pendente, nenhum re-bind pendente.

```sh
deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <spec-root>
```

Imprime cada tarefa sem registro, o que cada uma espera, e o conjunto entregável. É assim que o
Siegard responde "o que falta?" — não existe campo de status em lugar nenhum.

### `--unrecorded`
Antes de validar, uma entrega verifica que todo arquivo que mudou sob o target é nomeado por um de
seus registros. Um arquivo de teste alterado que ninguém registrou seria uma mudança que nenhuma
revisão jamais lê.

```sh
deliver.py --unrecorded <target-source-root> <record> [<record> ...]
```

### Lote em worktrees (worktree batch)
Quando o conjunto entregável tem várias tarefas independentes, elas podem ser entregues em
paralelo, um git worktree para cada. Só `delivery.json` e `siegard-trace.json` podem conflitar no
merge, e os dois são re-derivados em vez de mesclados à mão. `deliver.py --worktreeinclude` lista
os arquivos ignorados pelo git de que um worktree novo precisa.

### `/deliver-scope`, `orchestration.md`
Executa um escopo **de ponta a ponta** — plano, cada tarefa, revisão e uma rodada de prova —
commitando entre os passos. É o único componente autorizado a dar `git commit`, e só quando a
mensagem da própria pessoa pede a rota inteira. Mantém seu log em `orchestration.md` na raiz de
entrega.

```
gate → plan → commit → [deliver → commit, per task] → review → commit
     → [prove → commit, per task left testable] → review → commit → report → stop
```

### `deliver.py` — o validador da entrega

```sh
deliver.py <delivery-root> <work-root> <target-source-root> <spec-root>   # valida, escreve delivery.json
deliver.py --check ...                                  # valida e compara, não escreve nada
deliver.py --outstanding ...                            # o que falta, e por quê
deliver.py --node <file> <delivery-root>                # valida um registro
deliver.py --standard <file> [--against DIR] [--specification DIR]   # valida um standard
deliver.py --standard <file> --reading [--for <path> ...]            # só as regras decididas por leitura
deliver.py --check-record <record> <target-source-root>              # valida um registro do /check-source
deliver.py --unrecorded <target-source-root> <record> ...            # caminhos alterados que nenhum registro nomeia
deliver.py --worktreeinclude <file> <target-source-root> [--write]  # linhas do .worktreeinclude
deliver.py --contract <branch>                          # uma fatia de delivery-node.json para um agente
```

---

## 6. Revisando (`/review-change`)

### `/review-change`
Revisa uma mudança entregue por quatro ângulos, roda os steps do projeto sobre a mudança inteira e
escreve um **registro de revisão**. Produz evidência, nunca uma aprovação.

```
situate → capture → pass → compose → validate → report → stop
```

### Passes
Os quatro julgamentos independentes de uma revisão. Cada um é um agente separado; nenhum lê o
resultado do outro.

| Pass | Agente | Pergunta |
|---|---|---|
| **coverage** | `coverage-auditor` | Os testes falhariam se um critério deixasse de valer? |
| **conformance** | `specification-conformance-reviewer` (um por arquivo) | O código afirma só o que a especificação contém? |
| **standard** | `standard-conformance-reviewer` | O código segue as regras de leitura do próprio projeto? |
| **failures** | `failure-diagnostician` | Por que uma execução capturada falhou? |

Um pass que não pôde rodar é registrado com `missing: <o que faltou>`. Uma revisão relatada como
limpa sobre um pass que nunca rodou é exatamente o que isso impede.

### Finding (achado)
Uma coisa que um julgamento encontrou, sempre com evidência citada. Campos:

| Campo | Significado |
|---|---|
| `file` | Onde foi visto (escrito a partir da raiz de código do target). |
| `where` | A linha ou o trecho. |
| `evidence` | **Citada** do código, nunca parafraseada. |
| `cost` | A consequência, em termos que o leitor pode pesar — não "viola a regra X". |
| `correction` | O que teria de mudar (opcional; não é uma decisão). |
| `cites` | A única regra do standard violada (só no pass standard). |
| `cause` | `code`, `test`, `setup` ou `build` (só no pass failures). |

**Não há severidade nem veredito.** Um finding diz quanto custa; uma pessoa decide o que isso
significa.

### Estados de cobertura
Usados para o critério de uma tarefa numa revisão, e para um nó numa certificação:

| Estado | Significado |
|---|---|
| `covered` | Os testes nomeados falhariam se aquilo deixasse de valer — o teste inteiro de um teste. |
| `partial` | Uma parte declarada fica sem exercício. |
| `uncovered` | Nada exercita. |
| `unauditable` | Não dá para ler bem o bastante para procurar. |

### `unpaired`
Testes do conjunto que não se relacionam com **nenhum** critério de nenhuma tarefa sob revisão,
cada um com o que afirma. É uma leitura, nunca uma recomendação para apagar.

### Palavras da disciplina de testes (SPEC-004)
- **Obrigação** — algo a que uma prova deve evidência: um critério, o fato de um nó, ou uma nota
  `underdetermined`.
- **Evidência** — um teste que falha quando a obrigação é violada.
- **Teste finito** — um teste que decide um fato por inteiro: uma entrada contra um resultado
  esperado, ou todos os pares de um conjunto finito (por exemplo todo estado × gatilho de uma
  máquina de estados).
- **Teste redundante** — um teste cuja remoção deixa toda obrigação protegida. Não é escrito.

### `/check-source`, `siegard-check/`
Lê arquivos **que nenhuma tarefa entregou** contra as regras de leitura do standard, e escreve um
registro em `siegard-check/<slug>.md` ao lado do trace. Não executa nada e nunca escreve código.
Validado por `deliver.py --check-record`.

---

## 7. O trace

### Trace, `siegard-trace.json`
**O que é.** O único vínculo de longa duração entre a especificação e o código. Planos e registros
de entrega podem ser arquivados; o trace fica. Para cada nó ele guarda o digest do nó e o(s)
arquivo(s) que contêm o fato dele, cada um com seu digest.
**Quem escreve.** Só o `trace.py`. Nunca edite à mão.
**Exemplo.**

```json
{
  "specification": "specification",
  "bindings": [
    {
      "node": "domain/troubleshooting/case",
      "digest": "sha256:9e85d914…",
      "files": [
        { "path": "backend/src/troubleshooting/case.ts",
          "digest": "sha256:dce326b5…",
          "judged": true }
      ]
    },
    {
      "node": "rules/sales/invoice-immutable",
      "digest": "sha256:…",
      "files": [ { "path": "backend/src/billing/raise.ts", "digest": "sha256:…" } ],
      "decided_by": "test",
      "step": "test",
      "proof": [ { "path": "backend/tests/billing/raise.spec.ts", "digest": "sha256:…" } ]
    }
  ]
}
```

(Os caminhos dentro do arquivo de trace são relativos à pasta do próprio arquivo, o topo do git.)

### Binding (vínculo)
Uma entrada do trace: *o fato deste nó mora nestes arquivos*. Um **par nó-arquivo** é um nó mais
um de seus arquivos; a maior parte da reconciliação raciocina par a par.

`judged` num arquivo significa que o julgamento de uma reconciliação liberou aquele par naquele
digest. Ausente significa que foi carimbado por uma entrega (ou à mão) e não foi relido desde
então.

### Bind (vincular)
Escrever ou estender um binding. Normalmente feito por uma skill a partir de um registro:

```sh
trace.py --bind-record <target-root> <spec-root> <record>                 # a partir de um registro de implementação
trace.py --bind-record <target-root> <spec-root> <record> --workspace <dir>  # a partir de um registro de reconciliação
```

Vincula exatamente os nós que o registro lista com `encoded_at`, e nada mais. Por padrão
**acrescenta** ao que o nó já tinha (a "união"): um arquivo que um bind anterior pôs no nó
continua lá.

`--bind <target-root> <spec-root> <node> <file> ...` é a forma crua, que nenhum registro sustenta;
ela imprime um aviso de que o julgamento por trás da entrada não está registrado em lugar nenhum.

### Rebind (revincular)
Vincular um nó de novo para que os digests do trace batam com o que está em disco agora. Acontece
quando uma entrega recarimba os nós da sua tarefa, ou quando uma reconciliação libera um par.
"Mudou sem rebind" é o problema central: alguém editou um arquivo e ninguém atualizou o trace.

### `--replace`
Faz um bind **substituir a entrada inteira** em vez de acrescentar — para quando um fato realmente
saiu de um arquivo. Todo caminho que ele deixa de reivindicar é impresso como **recibo**. O
`/reconcile` nunca passa essa flag; ele entrega o comando para você rodar.

### Recibo (receipt)
As linhas que um comando imprime sobre o que ele *não* fez ou descartou (nós não vinculados,
caminhos liberados, certificações liberadas, drift retido). Leve os recibos para o relatório: são
o único lugar em que uma ação parcial diz que foi parcial.

### Drift, `--check`
**Drift** é qualquer divergência entre o trace e o que está em disco agora. O `--check` recalcula
todos os digests e reporta o drift em quatro **classes**:

| Classe | Significado | Resolvido por |
|---|---|---|
| `orphaned` | Vinculado a um nó que a especificação não contém mais | `trace.py --prune` |
| `moved` | O texto do nó mudou desde o bind | `/reconcile` sobre os arquivos vinculados, ou uma entrega que implemente o nó |
| `code` | Um arquivo vinculado mudou (ou sumiu) | `/reconcile` sobre o arquivo; `--release` se ele sumiu |
| `proof` | O teste que decide um binding certificado mudou | uma nova certificação |

Saída real (de uma fixture de teste):

```
$ trace.py --check backend
domain/troubleshooting/gone-from-the-base: no longer in the specification; the binding is stale
domain/troubleshooting/evidence: bound at sha256:0000…, now sha256:52f0…; the specification moved since this bind
backend/src/troubleshooting/case.ts: the file changed without a rebind — 1 binding(s): domain/troubleshooting/case

3 drift finding(s) over 3 binding(s):
  1 orphaned: …
  1 moved: …
  0 proof: …
  1 code over 1 file(s): …
```

Saída `0` significa nenhum drift; `1` significa drift (um CI pode rodar isso). `--all` também lista
o drift retido por `edits_freely`.

### `--prune`
Remove só os bindings da classe `orphaned` — depois que um `/analyse` removeu nós. Se o git mostra
que o arquivo do nó foi renomeado, segue a renomeação em vez de remover. Nunca use para silenciar
drift `code` ou `moved`.

### `--release`
Remove um arquivo **que a árvore não tem mais** de todo binding que o nomeia. Recusa um arquivo que
ainda existe (esse é reconciliado, nunca liberado).

```sh
trace.py --release <target-root> src/legacy/old-handler.ts
```

### `--encodes`
Quais nós cada arquivo tem vinculados — a pergunta inversa, que o `--check` não responde para
arquivos que não tiveram drift.

```
$ trace.py --encodes backend src/troubleshooting/case.ts
backend/src/troubleshooting/case.ts: 2 binding(s)
  domain/troubleshooting/case — stale: the file changed without a rebind
  domain/troubleshooting/gone-from-the-base — matches
```

- `--encodes --changed <target-root> [<ref>]` — o mesmo sobre o que o git diz que mudou (contra
  `HEAD`, ou desde `<ref>`).
- `--encodes --rank <target-root>` — as **contagens de acúmulo**: arquivos por quantos bindings
  contêm, nós por quantos arquivos estão vinculados. Costuma ser de onde sai o conjunto de arquivos
  de uma auditoria.

### `--untraced` e os quatro estados de arquivo
Lista todo arquivo rastreado pelo git sob um target que nenhum binding nomeia. Cada arquivo está
em exatamente um estado:

| Estado | Significado |
|---|---|
| **bound** | Um binding o nomeia. |
| **holds-nothing** | Uma adoção o julgou e não vinculou nenhum candidato a ele. |
| **outside** | Uma adoção o deixou deliberadamente fora do julgamento (configuração, fiação). |
| **unsurveyed** | Nenhum dos anteriores — ninguém olhou para ele ainda. |

```
$ trace.py --untraced backend
3 tracked file(s) under backend: 2 bound, 1 no binding names
  0 holds-nothing: judged by an adoption, which bound none of its candidates to it
  0 outside: kept outside an adoption's judgment
  1 unsurveyed: no binding and no adoption names it
```

Não recusa nada: a maioria dos arquivos de um sistema real não carrega fato de negócio e nunca é
vinculada.

### `--convergence` e os cinco estados de nó
Todo nó da especificação em exatamente um estado, considerando o trace e todas as iniciativas:

| Estado | Significado |
|---|---|
| `current` | Vinculado, e todo digest ainda bate. |
| `stale` | Vinculado, e algum binding teve drift (ver `--check`). |
| `planned-unbound` | Uma tarefa o implementa ou um épico o cobre, mas nada o vincula. |
| `declared-uncovered` | Um épico olhou para ele e escreveu por que não está sendo construído. |
| `unreached` | Nenhuma iniciativa o nomeia e nada o vincula. |

```sh
trace.py --convergence <target-root> <spec-root> <work-root-parent>
```

É uma consulta: saída sempre `0`, sem nota.

---

## 8. Reconciliação (`/reconcile`)

É aqui que mora a maior parte das palavras estranhas. Na primeira vez, leia os verbetes em ordem.

### Para que serve a reconciliação
Todo bind normal sai de uma entrega. Mas o código também muda de outros jeitos: uma correção
digitada durante um incidente, um conflito de merge resolvido à mão, uma entrega que reescreveu um
arquivo que outros nós também reivindicam. O trace então continua afirmando digests que não são
mais verdade. O `/reconcile` pega um **conjunto de arquivos que você nomeia**, faz juízes
independentes lerem esses arquivos contra todo nó que o trace vincula a eles, escreve um
**registro de reconciliação** e **revincula só o que os juízes liberaram**.

Nunca escreve código e nunca escreve um nó da especificação.

### Seus três modos
| Modo | Quando | Flag no `--stage` |
|---|---|---|
| **ordinário** | Arquivos mudaram sem rebind (edição à mão, merge). | *(nenhuma)* |
| **auditoria** | Bindings que nunca tiveram drift mas podem estar errados (largos demais desde o primeiro dia). | `--audit` |
| **adoção** | Código que nenhuma entrega escreveu — adotando o Siegard num projeto existente. | `--adopt --node … [--outside …]` |

(`--stage --review` é o mesmo preparo usado de dentro do `/review-change`.)

### A ordem

```
situate → stage → judge → capture → fold → bind → report → stop
```

### Entradas obrigatórias
1. **O conjunto de arquivos** — cada caminho, relativo à raiz de código do target. Nomeado pela
   pessoa, nunca descoberto.
2. **A raiz do projeto.**
3. **O target** (decidido automaticamente quando o `siegard.json` declara só um).
4. **O slug** — o nome do registro em `siegard-reconcile/`. Um slug já usado é uma parada.

Opcional: **certificações** (testes que a pessoa oferece como prova de um nó). Palavras de modo:
**audit**, **adoption** (com seus **candidatos** e, opcionalmente, arquivos **outside**).

### Situate (situar)
Verifica que a especificação é válida (`spec.py`), que o trace é válido (`trace.py`), que o
caminho do registro está livre, e que os arquivos nomeados estão **commitados** (o digest de uma
edição não commitada aponta para conteúdo que o próximo checkout apaga).

### `--stage` — preparando o workspace
**O que faz.** Calcula, mecanicamente, todo nó a que cada arquivo nomeado está vinculado, e prepara
tudo de que os juízes precisam, numa pasta descartável (o **workspace**, normalmente criado com
`mktemp -d`).

```sh
trace.py --stage <target-root> <spec-root> <slug> <workspace> <file> [<file> ...] \
    [--audit | --review [--node <n> ...] [--demonstrated <proof-record> ...] \
     | --adopt --node <candidate> ... [--outside <file> ...]] \
    [--certify <certifications.yaml>]
```

**Entradas:** raiz do target, raiz da especificação, slug, pasta do workspace, o conjunto de
arquivos e as flags de modo.
**Saída, no workspace:**

| Item | O que é |
|---|---|
| `manifest.json` | O conjunto de nós por arquivo, mais `unbound`, `omitted`, `mechanical`, `certify`, `candidates` |
| `packs/<arquivo com / trocado por __>.md` | Um **pacote de nós** (node pack) por arquivo: o texto completo de todo nó que o juiz daquele arquivo precisa ler, cada um com o caminho de origem e o digest |
| `packs/certify__<node>.md` | Um **pacote de certificação** por nó sendo certificado |
| `candidates.txt` | O **índice de candidatos** do lote inteiro |

Também cria `siegard-reconcile/<slug>.returns/` (vazia) no topo do git, onde as respostas dos
juízes serão salvas.

**Nunca** monte um conjunto de nós lendo o `siegard-trace.json` você mesmo; um nó esquecido à mão
é um juiz recebendo um conjunto incompleto, e a resposta dele parece exatamente igual a uma
completa.

### As quatro coisas que o stage separa
| O quê | O que acontece |
|---|---|
| Um arquivo com nós no manifest | Recebe um juiz. |
| Um arquivo a que o trace não vincula nada (**unbound**) | Só é reportado (exceto numa adoção, em que os candidatos são lidos contra ele). |
| Um arquivo cujos pares foram todos omitidos | Nada a julgar; registrado em `pairs_omitted`. |
| Um nó na classe `orphaned` | Parada para esse nó; a rota é `--prune`. |

### `pairs_omitted` (a guarda de omissão)
Um par é pulado quando rejulgá-lo não compraria nada: seu binding ainda bate com os bytes atuais
do arquivo **e** nenhum registro em `siegard-reconcile/` tem um finding aberto contra ele. O bind
recalcula as duas condições depois; se alguma deixou de valer, o registro inteiro é recusado.
`--audit` desliga isso: toda alegação existente é julgada.

### Camada mecânica (`mechanical`)
Pares que uma **execução** pode decidir não vão para um juiz: uma constraint que um step do
registro `decides`, ou um nó que um **teste certificado** decide. Em vez disso, você captura o step
uma vez:

```sh
run.py siegard-reconcile/<slug>.returns --run <slug> --cwd <target-source-root> \
    --timeout-seconds <limite> --step test="npm test"
```

e passa para o fold com `--run`. Um step vermelho é um resultado, não uma parada.

### Candidato, índice de candidatos, camada de candidatos
Um **candidato** é um nó que um juiz *pode* abrir quando seu arquivo afirma um fato que os nós do
próprio conjunto não resolvem — para dizer "este fato pertence àquele nó" em vez de "nenhum nó
contém isto". O **índice de candidatos** lista todo nó pelo qual o lote responde, com seus
arquivos. Numa reconciliação ordinária, a pessoa também pode nomear como candidatos os nós
**escritos desde o último bind** (os que o `/analyse` acabou de listar). Numa auditoria, nenhuma
camada de candidatos é passada.

Numa **adoção**, "candidato" tem um sentido mais forte: são os nós que o `/analyse` escreveu a
partir do código, nomeados com `--node`, lidos pelo juiz de **todo** arquivo — a leitura deles
decide se serão vinculados ou não.

### `--certify` e o arquivo de certificações
Oferece testes como prova de um nó. Um pequeno arquivo YAML no workspace:

```yaml
- node: rules/sales/invoice-immutable
  proof:
    - tests/billing/raise.spec.ts
  step: test
```

O stage recusa um nó que os arquivos não codificam, um arquivo de prova que não existe, ou um step
que o registro não declara.

### Juiz — o julgamento de conformidade
Um agente **`siegard:specification-conformance-reviewer`** **por arquivo**, disparados juntos.
Cada um recebe: seu único arquivo (caminho absoluto), o caminho do seu pacote de nós, o caminho do
índice de candidatos, a raiz da especificação e o caminho de `schemas/conformance-return.json`. Um
juiz por arquivo porque um contexto lendo tudo de uma vez "satura" e declara limpo pares que nunca
pesou.

Para cada certificação, um agente **`siegard:coverage-auditor`** recebe o pacote de certificação.

A sessão que orquestra **nunca lê os arquivos e decide ela mesma** — ela aceitou a premissa da
pessoa de que o código está certo, e estaria julgando a partir dessa premissa.

### O retorno (conformance return)
O que um juiz responde: YAML puro, **só quatro chaves permitidas em qualquer profundidade** —
`findings`, `read`, `looked_past`, `candidates_opened`. Uma quinta chave faz o retorno ser recusado
no fold.

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here, so the next reader looks
      for it in the specification and does not find it
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule the file cites governs modification of a raised invoice;
      `if (order.invoices.length >= 1)` states a cap no node holds
candidates_opened:
  - rules/sales/invoice-immutable
```

As chaves, uma a uma:

| Chave | Significado |
|---|---|
| **`findings`** | O que o juiz encontrou contra, cada um com `where`, `evidence`, `cost`, `kind` e, opcionalmente, `file`, `node`, `correction`. **A chave ausente significa "nada encontrado" — um resultado real e uma afirmação**: sobre este arquivo e estes nós, o código afirma o que a especificação contém e nada além disso. As pessoas muitas vezes *dizem* "`findings: []`" para isso, mas num retorno salvo a lista vazia é recusada pelo contrato (exige pelo menos um item): omita a chave. |
| **`read`** | **Uma entrada por nó do conjunto do próprio juiz, na ordem — nunca um subconjunto, nunca um candidato.** Diz, por nó, onde o fato dele está agora. É daqui que se escreve o `how` de um nó liberado. |
| `read[].node` | A identidade do nó. |
| `read[].held_at` | Onde no arquivo o fato do nó está agora (`the return statement of place(), line 41`), **ou a palavra `nowhere`** (em lugar nenhum). Um fato é contido por *código*, nunca por um comentário sobre ele. A resposta é lida pela primeira palavra: `nowhere. The file does no ranking.` continua significando "em lugar nenhum". |
| `read[].evidence` | Código citado que mostra isso. Onde `held_at` é `nowhere`, cita o que foi examinado. |
| **`looked_past`** | Uma frase nomeando o que foi visto e não reportado porque pertence a outro julgamento (por exemplo, um problema de estilo). |
| **`candidates_opened`** | Todo nó candidato que o juiz de fato abriu, tenha ou não saído um finding disso. **`candidates_opened: []` (ou a chave ausente) significa que não abriu nenhum.** Mede se vale a pena oferecer a camada de candidatos. |

Valores de texto livre são escritos como block scalars (`|-`) para que um dois-pontos solto não
quebre o YAML.

### `kind` — os três tipos de finding
Um julgamento responde a perguntas diferentes, e o `kind` diz qual:

| `kind` | Significa | Bloqueia o binding do nó? | Rota |
|---|---|---|---|
| **`contradicts`** | O código diz o que o nó nega, ou não carrega mais o fato do nó, ou virou uma segunda casa para ele. | **Sim** — o nó não é vinculado. | `/analyse` (a especificação está atrasada) ou corretivo do `/plan-work` (o código está errado) |
| **`unstated`** | O código afirma um fato que **nenhum nó contém**. | Não — nenhum rebind poderia fechá-lo. | `/analyse` |
| **`restates`** | Um **comentário** ou uma **docstring** — prosa que nenhum sistema em execução emite — diz o fato de um nó, **enquanto algum código também contém esse fato** (neste arquivo ou em outro que o finding nomeia). | Não — o par está conforme e é vinculado onde o código está. | Remover a prosa (a rota de comentários), depois `/reconcile` sobre o arquivo de novo |

Se nenhum código em lugar nenhum contém o fato, um comentário que o afirma é `contradicts`, não
`restates`.

**Texto que o sistema em execução emite é comportamento, nunca `restates`** — a descrição de uma
ferramenta, uma mensagem de erro, um prompt enviado a um modelo, uma linha de log. É o que o
sistema diz a alguém, então removê-lo mudaria o comportamento. Onde ele afirma corretamente o fato
de um nó, **não é finding** nenhum; onde afirma o fato de forma diferente do nó, é `contradicts`.

### Salvar os retornos literalmente
Cada retorno é salvo no momento em que chega, como cópia e nada mais, em:

```
siegard-reconcile/<slug>.returns/<caminho do arquivo com cada '/' trocado por '__'>.yaml
siegard-reconcile/<slug>.returns/certify__<nó com cada '/' trocado por '__'>.yaml
```

Nunca reformate, corte ou conserte um retorno. Os retornos são a **evidência** a partir da qual o
registro é dobrado, e eles sobrevivem à sessão. Um retorno inutilizável (campo faltando, nó sem
resposta) significa que o prompt estava errado: faça uma **delegação nova** com o prompt corrigido
— nunca pergunte algo a mais ao mesmo juiz, nunca edite a resposta dele. Duas respostas divergentes
do mesmo juiz anulam uma à outra.

### Premissa
A única parte do registro que é da pessoa: um pequeno arquivo YAML no workspace.

```yaml
title: Hand correction to invoicing
summary: The nightly run raised two invoices for one order; the guard was added by
  hand and the behavior is correct.
target: backend
files:
  - path: src/billing/raise.ts
    change: refuses a second invoice for an order that already has one
```

O `summary` diz **por que a pessoa afirma que o código está certo** — como afirmação da pessoa,
nunca como finding. O `change` diz o que o arquivo agora *faz* de diferente, não o que foi
digitado.

### `--fold` — escrevendo o registro
**O que faz.** Combina ("dobra") mecanicamente todos os retornos salvos mais a premissa no
registro de reconciliação. Nenhum julgamento acontece aqui — só regras fixas.

```sh
trace.py --fold <target-root> <workspace> <premise.yaml> siegard-reconcile/<slug>.md \
    [--run siegard-reconcile/<slug>.returns/run/<slug>]
```

**Entradas:** o workspace (manifest, retornos), a premissa, o caminho do registro, e `--run`
exatamente quando houve camada mecânica.
**Saída:** `siegard-reconcile/<slug>.md`, validado antes de ser gravado.
**Regras que aplica:** um nó está conforme só onde todo juiz que leu um de seus arquivos o liberou;
um finding que nomeia um nó cai nesse nó; um finding que **não** nomeia nó cai em todo nó daquele
arquivo (esses ficam marcados `collateral`); findings `unstated` e `restates` vão para listas
próprias; uma certificação só é escrita onde o auditor respondeu `covered` **e** a leitura do
próprio nó o liberou.

**Nunca edite o que o fold escreveu.** Se o fold recusar: recusa que nomeia uma delegação →
delegação nova; recusa sobre a premissa → corrija a premissa.

### O registro de reconciliação (`siegard-reconcile/<slug>.md`)
Mora no topo do git, ao lado do trace, e **nunca é apagado** (nem pelo `/siegard-archive`): é a
justificativa de bindings que ainda estão no trace. Contrato: `schemas/reconciliation.json`
(versão atual `siegard-reconcile/8`).

```yaml
contract_version: siegard-reconcile/8
title: Hand correction to invoicing
summary: …                                   # a premissa da pessoa
target: backend
files:
  - path: src/billing/raise.ts
    change: refuses a second invoice for an order that already has one
nodes:
  - node: rules/sales/invoice-immutable
    conforms: false
    how: the source now states `if (order.invoices.length >= 1) return existing`, and
      no node holds that an order carries at most one invoice
    observed_at:
      - src/billing/raise.ts
notes: The behavior is right and the specification is behind it.
```

Campos:

| Campo | Significado |
|---|---|
| `files` | O conjunto de arquivos que a pessoa nomeou, cada um com seu `change`. |
| `nodes[]` | Todo nó que o trace vincula a um arquivo nomeado, com a resposta. |
| `conforms` | `true` = o julgamento liberou o nó; `false` = há um finding de pé. |
| `how` | Por quê — com o que foi lido, citado. |
| `encoded_at` | Só num nó liberado: os arquivos que contêm o fato dele. **É exatamente isso que é vinculado.** |
| `observed_at` | Só num nó não liberado: arquivos que foram lidos, sem afirmar nada sobre eles. |
| `collateral` | Num nó não liberado: nada foi encontrado contra a substância **dele**; ele divide o arquivo com um finding que não nomeou nó. Resolva o finding e ele é liberado junto. |
| `decided_by`, `step`, `proof` | Uma certificação que se sustentou: o nó agora é decidido por um teste. |
| `remainder`, `remainder_why` | Uma certificação que não se sustentou: se um teste *poderia* fechar a lacuna (`testable`) ou não (`untestable`), e a asserção que fecharia. |
| `unstated` | Fatos que o código afirma e nenhum nó contém, por arquivo. |
| `restates` | Lugares em que um comentário ou docstring repete o fato de um nó que o código já contém. |
| `unbound` | Arquivos nomeados a que o trace não vincula nada. |
| `adopted` | Presente num registro de adoção. |
| `unheld` | Só em adoção: candidatos que **nenhum arquivo do conjunto contém** e contra os quais nada foi encontrado — todo juiz respondeu `nowhere`. Não reivindicam arquivo nenhum. |
| `outside` | Só em adoção: arquivos que a pessoa deixou fora do julgamento. |
| `pairs_omitted` | Pares não rejulgados, cada um com o motivo. |
| `notes` | Prosa de que um leitor futuro precisa; nunca uma decisão. Uma nota terminando em "owed a route of its own" precisa ser levada para o relatório. |

### `--reconciliation` — validando o registro

```sh
trace.py --reconciliation siegard-reconcile/<slug>.md
```

Não escreve nada. Confere o registro contra o contrato e a contabilidade (todo caminho reivindicado
está em `files`; todo arquivo nomeado é reivindicado ou declarado unbound).

### Bind (na reconciliação)

```sh
trace.py --bind-record <target-root> <spec-root> siegard-reconcile/<slug>.md --workspace <workspace>
```

Vincula **só os nós que têm `encoded_at`** — os liberados — e nada mais. Os nós com findings ficam
exatamente como estavam. `--workspace` faz ele recusar se algum arquivo ou nó mudou desde o stage.
Rode uma vez, tenha tudo sido liberado ou não, e leia o recibo.

### `--owed` — o que ainda está em aberto
**O que faz.** Lê todos os registros em `siegard-reconcile/` como um corpo de evidência (o
"corpus") e lista os findings que **nenhum bind fechou**. Não escreve e não decide nada.

```sh
trace.py --owed <target-root> [--all]
```

É necessário porque o `--check` não enxerga esses casos: um nó que o julgamento recusou não ganha
digest novo, então pode não haver nada para o `--check` comparar. Cada finding aberto está em um de
três estados:

| Estado | Significado |
|---|---|
| `unseen` | Nada vincula o par — o `--check` nunca poderá reportá-lo. |
| `covered` | Vinculado no conteúdo de hoje — um bind posterior escreveu por cima do único sintoma; o finding continua de pé. |
| `reported` | O binding está defasado, então o `--check` já o mostra; o registro diz o que foi encontrado. |

Também lista os fatos `unstated`, os textos `restates`, pares respondidos dos dois jeitos por
registros diferentes, e as **sobras testáveis** (nós que um teste poderia fechar). Saída `0` =
nada devido. (Não confunda este `covered` com o estado de cobertura `covered` da §6.)

### Certificação, `decided_by: test`
Uma **certificação** é o julgamento de que os testes que a pessoa ofereceu **falhariam se o fato do
nó deixasse de valer**. Quando se sustenta (o auditor responde `covered`), o binding passa a ser
**decidido por teste**: dali em diante, drift nos seus arquivos é respondido rodando o step em vez
de uma nova leitura, e nenhum juiz lê aquele par de novo. Os digests da prova são fixados no trace;
se o arquivo de teste muda, o `--check` reporta drift `proof` e o binding volta a ser decidido por
leitura.

O padrão de todo binding é `decided_by: reading`. Uma certificação é oferecida pela pessoa
(`--certify`) ou montada a partir dos registros de prova durante uma revisão (`--demonstrated`);
nunca é inventada pela skill.

### Sobra (remainder): `testable` / `untestable`
Quando uma certificação fica aquém de `covered`, o auditor diz se o que falta poderia ser fechado
por um teste:

- **`testable`** — uma entrada contra um resultado esperado fecharia. O `remainder_why` nomeia a
  asserção. O `--owed` lista essas; o relatório entrega um **incremento de prova** para fechá-las.
- **`untestable`** — nenhum teste finito fecha (uma identidade que atravessa arquivos, uma
  totalidade sobre um conjunto que nada enumera).

### Adoção
A rota para **código escrito antes do Siegard**. Passos:

1. `trace.py --untraced <target>` — no início, todo arquivo está `unsurveyed`.
2. Escreva o material **só a partir do código** (comportamento observável, cada fato ao lado do seu
   caminho).
3. `/analyse` sobre ele → lista os nós que escreveu.
4. `/reconcile` como adoção sobre os arquivos do contexto, com esses nós como candidatos `--node` e
   configuração/fiação como `--outside`. A primeira adoção cria o `siegard-trace.json`.
5. Leia o que volta: candidatos `unheld`, `contradicts` e `unstated` → de volta ao `/analyse`;
   `restates` → remova o comentário, reconcilie de novo.
6. Depois, a documentação, como um incremento ordinário do `/analyse`.

A adoção está **completa** quando o `--untraced` não mostra nenhum arquivo `unsurveyed` e o
`--convergence` nenhum nó `unreached`. É calculado, nunca registrado, e nada espera por isso.

### O relatório e a próxima invocação
O `/reconcile` termina dizendo: o conjunto de arquivos; o que o stage separou por arquivo; quantos
juízes; a resposta por nó com evidência; o que foi vinculado e o que não foi; certificações que se
sustentaram ou não; e o **próximo conjunto de arquivos = a sobra** (só os arquivos cujos nós ainda
estão devidos). Para cada nó não liberado, entrega **as duas portas** sem escolher — `/analyse` (a
especificação está atrasada) ou corretivo do `/plan-work` (o código está errado) — mais a rota de
comentários para `restates`.

---

## 9. As outras skills e scripts auxiliares

### `/analyse`
Transforma material em nós da especificação, valida-os (`spec.py`) e deriva as projeções. Termina
listando as identidades que escreveu — as que você pode passar como candidatas ao `/reconcile`.

### `/siegard-config`
Escreve ou atualiza o `siegard.json` a partir do que você diz. O único que escreve esse arquivo.

### `/siegard-standard`
Faz o rascunho do standard do projeto a partir do que suas ferramentas já impõem (linter,
compilador, scanner de segredos) e do que uma pessoa declara. Nunca inventa regra.

### `/siegard-status`
Um status amigável e só de leitura do projeto inteiro: integridade da especificação, decisões
recentes, tarefas pendentes e notas `BLOCKING` de cada iniciativa viva, drift do trace por classe,
trabalho não commitado. Cita um comando para cada afirmação.

### `/siegard-progress`
Uma tabela compacta das tarefas de uma iniciativa (status + porquê), feita para rodar
repetidamente (por exemplo com `/loop`).

### `/siegard-archive`
Remove da árvore de trabalho iniciativas **fechadas** (work + delivery), depois de verificá-las
mecanicamente. Nunca toca no arquivo do projeto, no trace, na especificação, no decision log nem
nos registros de reconciliação, e nunca commita — entrega os comandos git para você.

### `/siegard-telemetry` e `telemetry.py`
Escreve um relatório de **como** um trecho de trabalho aconteceu (agentes, custo em tokens e tempo,
recusas, execuções, decisões, compactações), contado a partir do disco e das transcrições de sessão
do harness.

```sh
telemetry.py --probe <project-root> --since last        # as transcrições podem ser lidas?
telemetry.py <project-root> --since 2026-09-29T00:00:00Z [--until …]
```

Saída: `<telemetry_root>/<stamp>.json` mais um relatório Markdown ao lado.

### `project.py`

```sh
project.py <project-root>
```

Lê e valida o `siegard.json` e imprime cada campo que ele declara, um por linha. Toda skill roda
isso primeiro. Se uma cópia antiga das regras estiver no `CLAUDE.md` da raiz do projeto, imprime
uma linha `rules:` pedindo que você a remova.

### Fatias de contrato (`--contract`)
`plan.py --contract <branch>` e `deliver.py --contract <branch>` imprimem um pedaço autossuficiente
de um schema, para que um agente receba exatamente os campos que escreve em vez do schema inteiro.

### Códigos de saída (todos os scripts)
| Código | Significado |
|---|---|
| `0` | Íntegro / nada encontrado / feito. |
| `1` | Problemas encontrados (arquivo inválido, drift, um finding que nenhum bind fechou, um registro recusado). |
| `2` | Não pôde rodar (pasta ausente, entrada quebrada). |

Uma saída diferente de zero de um comando de *status* não é falha da skill: ela **é** o status.

---

## 10. Os agentes

As skills delegam julgamento e produção a estes agentes, sempre pelo nome com escopo de plugin
(`siegard:<name>`). Nenhum agente tem shell. Só os dois produtores podem escrever arquivos.

| Agente | Usado por | Faz | Escreve arquivos? |
|---|---|---|---|
| `codebase-surveyor` | `/plan-work` | Levanta o código; devolve nós de inventário | Não |
| `backlog-decomposer` | `/plan-work` | Recorta o escopo em épicos e esqueletos de tarefa | Não |
| `execution-contract-binder` | `/plan-work` | Decide o `implements` de cada tarefa; devolve notas classificadas | Não |
| `unstated-fact-decider` | `/plan-work` | Decide um fato não declarado, às cegas quanto à tarefa; devolve edições de nó + entrada no log | Não |
| `task-implementer` | `/implement-task` | Escreve o código de uma tarefa e seu registro de implementação | **Sim** |
| `test-author` | `/implement-task` | Escreve os testes e o registro de prova | **Sim** |
| `failure-diagnostician` | `/implement-task`, `/review-change` | Diz por que cada falha de uma execução capturada falhou | Não |
| `coverage-auditor` | `/review-change`, `/reconcile` | Pareia critérios com testes; certifica os testes de um nó | Não |
| `specification-conformance-reviewer` | `/review-change`, `/reconcile` | Lê um arquivo contra seus nós; devolve findings + `read` | Não |
| `standard-conformance-reviewer` | `/review-change`, `/check-source` | Lê arquivos contra as regras de leitura do standard | Não |

**Delegação** = disparar um destes num contexto limpo. **Inline** = o recurso quando a sessão não
consegue disparar agentes: a própria sessão aplica o arquivo do agente, e o relatório precisa dizer
isso. O `/reconcile` se recusa a rodar inline se a mesma sessão escreveu algum dos nós julgados.

---

## 11. Palavras informais que você pode encontrar

Estas palavras aparecem em conversas, notas de sessão ou mensagens de commit. **Não** são campos
nem flags do framework; eis o termo oficial que cada uma representa.

| Você pode ouvir | Significa | Termo oficial |
|---|---|---|
| **fold** (dobrar) | Combinar os retornos salvos dos juízes + a premissa no registro. | `trace.py --fold` |
| **refold / re-fold** (redobrar) | Rodar o `--fold` de novo sobre os **mesmos retornos salvos** — tipicamente depois que uma correção no framework mudou uma regra do fold, e antes de o registro ser commitado. Só é possível porque os retornos são guardados literalmente e o fold é mecânico. Nunca é uma edição à mão do registro, e nunca pergunta de novo aos juízes. | `trace.py --fold` (de novo) |
| **unfold / unfolded** | Aparece só como nome interno no `deliver.py`: uma revisão cujo pass de conformidade rodou sobre um target com trace mas **não dobrou nenhum registro de reconciliação**. O `deliver.py` imprime um recibo para ela: os outros nós vinculados aos arquivos revisados ainda carregam digests antigos, e um `/reconcile` sobre esses arquivos os fecha. | o recibo de "revisão não reconciliada" |
| **certificate** (certificado) | Uma certificação que se sustentou. | `decided_by: test` (+ `step`, `proof`) |
| **comment findings** | Findings `restates` em que o texto é um **comentário** ou docstring no código. | `kind: restates` |
| **emitted-text findings** | Findings sobre texto que o **sistema em execução emite** — descrição de ferramenta/API, mensagem de erro, prompt, linha de log. Desde a 4.21.3 esse texto é comportamento, nunca `restates`: se concorda com o nó, não é finding; se discorda, é `contradicts`. (Antes da 4.21.3 uma descrição repetindo um fato que o código impunha era registrada como `restates`, então registros antigos ainda podem ter entradas assim.) | nenhum finding, ou `kind: contradicts` |
| **unheld** | *(este é oficial)* um candidato de adoção que nenhum arquivo contém. | `unheld` no registro |
| **o corpus** | Todos os registros em `siegard-reconcile/`, lidos em conjunto. | lido pelo `--owed` |
| **par** | Um nó + um de seus arquivos. | par nó-arquivo |
| **liberar / liberado** (clear / cleared) | O julgamento não encontrou nada contra um nó: ele está conforme e é vinculado. | `conforms: true` + `encoded_at` |
| **carimbar / recarimbar** (stamp / restamp) | Escrever os digests atuais no trace. | bind / rebind |
| **juiz** | Um agente a quem foi delegado um julgamento. | uma delegação |
| **porta** (door) | Uma invocação pronta para colar que um relatório entrega. | "the invocation ready to paste" |

---

## 12. Um exemplo completo: uma correção feita à mão

**A situação.** Durante um incidente, alguém acrescentou uma guarda em `src/billing/raise.ts` para
que um pedido não possa ter duas faturas, e commitou. O comportamento está correto.

**1. Algo percebe.** Um CI roda:

```
$ trace.py --check backend
backend/src/billing/raise.ts: the file changed without a rebind — 1 binding(s): rules/sales/invoice-immutable
...
1 code over 1 file(s): …
```

**2. Você invoca a rota**, nomeando o conjunto de arquivos, a raiz do projeto e um slug novo:

```
/siegard:reconcile  file set: src/billing/raise.ts   project root: .   slug: hand-fix-invoicing
```

**3. Stage.** A skill roda:

```sh
trace.py --stage backend specification hand-fix-invoicing /tmp/ws src/billing/raise.ts
```

O workspace agora contém `manifest.json`, `packs/src__billing__raise.ts.md` (o texto de
`rules/sales/invoice-immutable`) e `candidates.txt`; a pasta vazia
`siegard-reconcile/hand-fix-invoicing.returns/` existe.

**4. Julgar.** Um `siegard:specification-conformance-reviewer` lê o arquivo contra seu pacote.
Devolve (salvo literalmente como
`siegard-reconcile/hand-fix-invoicing.returns/src__billing__raise.ts.yaml`):

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule governs modification of a raised invoice; the guard states a cap no node holds
candidates_opened:
  - rules/sales/invoice-immutable
```

**5. Fold.** A skill escreve a premissa ("acrescentado à mão durante um incidente; correto") e roda
`trace.py --fold …`. O registro diz `conforms: false`, `observed_at: [src/billing/raise.ts]`. O
`trace.py --reconciliation` passa.

**6. Bind.** `trace.py --bind-record … --workspace /tmp/ws` não vincula nada (nenhum nó tem
`encoded_at`) e o recibo diz isso.

**7. Relatório.** Duas portas, e a skill não escolhe nenhuma:
- **O código está certo, a especificação está atrasada** → `/analyse` com o finding como material,
  para que um nó ganhe "um pedido tem no máximo uma fatura"; depois `/reconcile` de novo sobre o
  mesmo arquivo, com um slug novo.
- **A especificação está certa, o código está errado** → incremento corretivo do `/plan-work`.

**8. Depois.** `trace.py --owed backend` continua listando o finding até que algum registro libere o
par.

Se o único problema fosse um comentário — digamos `// an order may only have one invoice` acima de
um código que já impõe um nó de regra — o juiz teria registrado `kind: restates`, o nó teria sido
vinculado, e o relatório entregaria a rota de comentários: apagar o comentário, commitar,
`/reconcile` naquele arquivo com um slug novo. Se, em vez de comentário, fosse a **mensagem de
erro** que o sistema devolve dizendo a mesma coisa que o nó, não haveria finding nenhum: é
comportamento que concorda com o nó.

---

## 13. Índice alfabético

| Termo | Seção |
|---|---|
| `_context.md` | 3 |
| adoção, `--adopt` | 8 |
| advisory (nota) | 4 |
| aggregate-root | 3 |
| âncora | 4 |
| auditoria, `--audit` | 8 |
| bind, `--bind`, `--bind-record` | 7, 8 |
| binding (vínculo) | 7 |
| blocking, `BLOCKING` | 4 |
| bounded context (contexto delimitado) | 3 |
| camada mecânica (`mechanical`) | 8 |
| candidato, índice de candidatos, camada de candidatos | 8 |
| `candidates_opened` | 8 |
| capability | 3 |
| certificação, pacote de certificação, `--certify` | 8 |
| certificate (informal) | 11 |
| `--changed` | 7 |
| `--check` | 7 |
| `/check-source`, `--check-record` | 6 |
| classes (as cinco) | 3 |
| `closure.md`, fechamento | 4 |
| `code` (drift) | 7 |
| códigos de saída | 9 |
| collateral | 8 |
| comment findings (informal) | 11 |
| compound (nota) | 4 |
| conformance (pass) | 6 |
| conformance return (retorno) | 8 |
| `conforms` | 8 |
| conjunto entregável | 5 |
| contagens de acúmulo (`--rank`) | 7 |
| `contested` | 5 |
| contract (classe) | 3 |
| `--contract` (fatias) | 9 |
| `contradicts` | 8 |
| `--convergence` | 7 |
| coverage (pass) | 6 |
| `covered` / `partial` / `uncovered` / `unauditable` | 6 |
| `covered` / `unseen` / `reported` (`--owed`) | 8 |
| `covers` / `uncovered` | 4 |
| critérios (`criteria`) | 4 |
| `decided_by` (standard) | 2 |
| `decided_by: test` / `reading` (trace) | 8 |
| decidir e divulgar | 3 |
| decision log | 3 |
| `deferred` | 5 |
| `/deliver-scope`, `orchestration.md` | 5 |
| `delivery.json` | 5 |
| `demonstrates`, `--demonstrated` | 5, 8 |
| `depends_on` | 4 |
| digest | 3 |
| divergences | 5 |
| drift | 7 |
| `edits_freely` | 2 |
| emitted-text findings (informal) | 11 |
| `encoded_at` | 5, 8 |
| `--encodes` | 7 |
| épico | 4 |
| escopo | 4 |
| evidência | 6, 8 |
| execução capturada | 5 |
| failures (pass), `cause` | 6 |
| finding | 6, 8 |
| `--fold` | 8 |
| `held_at` | 8 |
| `holds-nothing` / `outside` / `unsurveyed` | 7 |
| `how` | 5, 8 |
| identidade | 3 |
| impacto, `--impact` | 3 |
| incremento corretivo | 4 |
| incremento de prova | 4 |
| inferences | 5 |
| iniciativa | 2 |
| inline | 10 |
| intake | 3 |
| inventário | 4 |
| invariant / policy / state-machine | 3 |
| juiz | 8 |
| `kind` | 8 |
| `looked_past` | 8 |
| manifest | 8 |
| material | 3 |
| `moved` | 7 |
| nó | 3 |
| `nowhere` | 8 |
| obrigação | 6 |
| `observed_at` | 8 |
| `orphaned` | 7 |
| `--outstanding` | 5 |
| `--owed` | 8 |
| pacote de nós (node pack) | 8 |
| `pairs_omitted` | 8 |
| par nó-arquivo | 7 |
| passes | 6 |
| pin | 3 |
| piso / teto | 3 |
| premissa | 8 |
| `presupposes`, `produces`, substrato | 5 |
| `project.py` | 9 |
| projeção | 3 |
| `proof` (drift) | 7 |
| `--prune` | 7 |
| raiz de código do target | 2 |
| `read` | 8 |
| rebind | 7 |
| re-bind (planejamento) | 4 |
| recibo | 7 |
| refold (informal) | 11 |
| registro de implementação / prova / revisão | 5, 6 |
| registro de reconciliação | 8 |
| `--reconciliation` | 8 |
| regra de comentários | 2 |
| `--release` | 7 |
| remainder (nota) | 4 |
| `remainder` `testable`/`untestable` | 8 |
| `--replace` | 7 |
| `restates` | 8 |
| retornos, `.returns/` | 8 |
| rotas | 2 |
| `run.py` | 5 |
| scenario | 3 |
| `--shape`, `--of` | 3 |
| `siegard.json` | 2 |
| `siegard-check/` | 6 |
| `siegard-reconcile/` | 8 |
| `siegard-trace.json` | 7 |
| slug | 2 |
| `--stage` | 8 |
| standard (registro de regras) | 2 |
| standard (pass) | 6 |
| `stands` | 4 |
| target | 2 |
| tarefa | 4 |
| telemetria | 9 |
| teste finito | 6 |
| topo do git | 2 |
| trace | 7 |
| underdetermined (nota) | 4 |
| `unbound` | 8 |
| unfold / unfolded (informal) | 11 |
| `unheld` | 8 |
| `unpaired` | 6 |
| `--unplanned` | 4 |
| `--unrecorded` | 5 |
| `unstated` (finding) | 8 |
| unstated (nota), unstated-fact-decider | 4 |
| `--untraced` | 7 |
| workspace | 8 |
| worktrees (lote) | 5 |
