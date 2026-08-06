# Siegard explicado do zero

> **Sobre este manual.** Ele descreve o motor deste repositório a partir do zero, sem supor
> conhecimento prévio. Cobre a versão **2.0.0** (contratos `siegard/1`, `siegard-plan/2`,
> `siegard-delivery/1`).
>
> **Sobre o idioma.** A seção Language de `/CLAUDE.md` exige que todo artefato do repositório seja
> em inglês (en-US), e nomeia `docs` entre eles. Este arquivo é a exceção deliberada, decidida pelo
> mantenedor com a regra sobre a mesa, e é o único artefato do repositório fora dela.
>
> **Sobre os exemplos.** Todos os nós vieram dos campos `examples` dos próprios schemas, então são
> formas que o contrato admite por construção. Toda saída de validador citada é real, capturada
> rodando o motor sobre bases construídas para este manual.

---

## Índice

1. [Que problema isso resolve](#1-que-problema-isso-resolve)
2. [A ideia central em uma página](#2-a-ideia-central-em-uma-página)
3. [O nó: a unidade de tudo](#3-o-nó-a-unidade-de-tudo)
4. [O caminho é a identidade](#4-o-caminho-é-a-identidade)
5. [O índice derivado](#5-o-índice-derivado)
6. [O gap: o que o material não disse](#6-o-gap-o-que-o-material-não-disse)
7. [Os sete tipos de nó, com exemplos reais](#7-os-sete-tipos-de-nó-com-exemplos-reais)
8. [Do conhecimento ao plano: a vinculação](#8-do-conhecimento-ao-plano-a-vinculação)
9. [O digest: qual versão a vinculação leu](#9-o-digest-qual-versão-a-vinculação-leu)
10. [As totalidades: nada passa em silêncio](#10-as-totalidades-nada-passa-em-silêncio)
11. [A entrega](#11-a-entrega)
12. [Os quatro pontos de entrada](#12-os-quatro-pontos-de-entrada)
13. [A parada é a funcionalidade](#13-a-parada-é-a-funcionalidade)
14. [Exemplo completo de ponta a ponta](#14-exemplo-completo-de-ponta-a-ponta)
15. [Glossário](#15-glossário)
16. [Erros comuns e o que significam](#16-erros-comuns-e-o-que-significam)
17. [Migrando de 1.x para 2.0.0](#17-migrando-de-1x-para-200)

---

## 1. Que problema isso resolve

Considere um projeto de software comum. Alguém do negócio explica uma regra numa reunião. Um
desenvolvedor entende e escreve o código. Seis meses depois:

- A regra está no código, misturada a detalhes técnicos.
- Está também num Jira fechado, com a redação de quem abriu o ticket.
- Está num comentário `// pedido não pode ter total zero`, que ninguém atualizou.
- Está na cabeça de duas pessoas, uma das quais saiu.

E quando alguém pergunta *"por que o sistema recusa esse pedido?"*, a resposta honesta é "vamos ler
o código e descobrir". O código passou a ser a fonte da verdade sobre o que o **negócio decidiu** —
e isso é uma inversão. O código deveria ser consequência da decisão, não o lugar onde ela mora.

Pior: quando o código é a única fonte, **não existe diferença visível entre uma decisão do negócio e
um chute de quem programou**. As duas coisas parecem exatamente iguais no arquivo. Um
`if total <= 0: reject()` pode ser uma regra que o cliente ditou ou uma suposição de terça-feira à
tarde.

### O que o Siegard faz

Separa isso em três camadas e obriga cada uma a apontar para a anterior:

```
   O que o negócio decidiu   →   O que vamos construir   →   O que foi construído
        (conhecimento)                  (plano)                    (entrega)
```

E acrescenta uma regra que muda tudo:

> **Um fato que ninguém disse não é inventado. É declarado como ausente.**

É essa regra que torna visível a diferença entre decisão e chute. Se o material nunca disse qual é o
total mínimo de um pedido, o nó **não escreve zero**. Ele escreve: *este fato está em falta, e só
quem conhece o domínio pode preenchê-lo.*

---

## 2. A ideia central em uma página

Três diretórios. Cada um cheio de arquivos markdown. Cada um com um índice gerado por script e um
validador que **se recusa** a gerar o índice se as coisas não fecharem.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RAIZ DE CONHECIMENTO          "o que o negócio decidiu"                    │
│  knowledge/                                                                 │
│    context/sales.md                    ← um arquivo = um fato do domínio    │
│    definition/sales/order.md                                                │
│    rule/sales/total-positive.md                                             │
│    graph.json                          ← GERADO. nunca editado à mão.       │
│                                                                             │
│  validador: bin/graph.py                                                    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  cada task "vincula" os nós que a governam
                               │  e guarda o digest de cada um que leu
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RAIZ DE TRABALHO              "o que vamos construir"                      │
│  work/                                                                      │
│    inventory/order-service.md          ← o que já existe no código          │
│    epic/checkout.md                    ← uma fatia de escopo                │
│    task/checkout/record-order.md       ← uma unidade de trabalho            │
│    plan.json                           ← GERADO.                            │
│                                                                             │
│  validador: bin/plan.py   (valida o plano CONTRA a base)                    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  cada record responde a uma task
                               │  e pina a versão da task que respondeu
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RAIZ DE ENTREGA               "o que foi construído"                       │
│  delivery/                                                                  │
│    implementation/checkout/record-order.md   ← o que o código faz           │
│    proof/checkout/record-order.md            ← o que os testes provam       │
│    review/first.md                           ← o que a revisão achou        │
│    run/first/                                ← o que a suite imprimiu       │
│    delivery.json                             ← GERADO.                      │
│                                                                             │
│  validador: bin/deliver.py  (valida a entrega CONTRA o plano)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Três coisas para guardar desde já:**

1. **Tudo é markdown.** Nada de banco de dados, nada de estado escondido. Basta abrir no editor e
   ler.
2. **Nenhum nó tem status.** Não existe campo "em andamento", "pronto", "aprovado". O estado da
   execução mora no git. Um plano que registrasse progresso seria um arquivo de estado de
   orquestrador, e o framework recusa ter um.
3. **Os `.json` são derivados.** Nunca se edita um. Muda-se o markdown e roda-se o script. Um json
   editado à mão é acusado pelo próximo `--check`.

---

## 3. O nó: a unidade de tudo

Um **nó** é um arquivo markdown com duas partes: um cabeçalho de dados (o *frontmatter*, entre
`---`) e um corpo de prosa.

```markdown
---
title: Order
summary: A customer's order.
ddd: aggregate-root
aggregate: orders
identity:
  - order_number
attributes:
  - name: order_number
    type: string
    max_length: 20
---
## What it is
What the customer placed, from the moment it is submitted.

## Rules
None.
```

### As duas metades, e por que são separadas

| metade | o que carrega | quem lê |
|---|---|---|
| **frontmatter** (YAML) | os fatos, em campos com nome e forma fixos | o validador, mecanicamente |
| **corpo** (markdown) | prosa para um humano entender | uma pessoa |

O validador **só valida o frontmatter**. O corpo é para o leitor. Mas mesmo o corpo tem forma
obrigatória: exatamente dois cabeçalhos, na ordem. Num nó de conhecimento são `## What it is` e
`## Rules`. Numa task ou num record são `## What it is` e `## Notes`. Uma seção sem nada a dizer
carrega literalmente a linha `None.` — porque uma seção ausente e uma seção vazia contam histórias
diferentes, e o framework quer a diferença explícita.

> **Por que isso importa:** um fato que more só na prosa é um fato que duas pessoas leem de dois
> jeitos. Se é fato, vai no frontmatter, onde tem nome e o validador o alcança.

---

## 4. O caminho é a identidade

Esta é **a ideia mais importante do motor inteiro**. Quem entender só uma coisa deste manual, que
entenda esta.

Num sistema comum, um registro tem um `id`:

```yaml
id: order-definition-001     # ← um campo
type: definition             # ← outro campo
context: sales               # ← outro campo
```

Três campos que podem **discordar** do lugar onde o arquivo está. Basta mover o arquivo e esquecer
de atualizar o `context`: agora existem duas respostas para "a que contexto isso pertence", e
nenhuma é autoridade.

No Siegard, o caminho **é** o identificador:

```
knowledge/definition/sales/order.md
          └────┬───┘ └─┬─┘ └─┬─┘
              tipo  contexto  nome
```

E por isso **não existe campo `id`, nem `type`, nem `context`**. Não podem discordar do caminho
porque não existem. O validador extrai o tipo e o contexto do caminho e pronto.

```
 ┌──────────────────────────────────────────────────────────────┐
 │  O identificador de um nó é seu caminho sem o `.md`:         │
 │                                                              │
 │  knowledge/definition/sales/order.md                         │
 │            └──────────────────────┘                          │
 │                       ↓                                      │
 │            "definition/sales/order"                          │
 │                                                              │
 │  É assim que outros nós se referem a ele.                    │
 └──────────────────────────────────────────────────────────────┘
```

### As formas de caminho, por raiz

```
CONHECIMENTO
  context/<nome>.md                    ← contexto: só um nível
  <tipo>/<contexto>/<nome>.md          ← todo o resto: dentro de um contexto

  exemplos reais:
    context/sales.md                   → "context/sales"
    definition/sales/order.md          → "definition/sales/order"
    rule/sales/total-positive.md       → "rule/sales/total-positive"

PLANO
  inventory/<nome>.md                  → "inventory/order-service"
  epic/<nome>.md                       → "epic/checkout"
  task/<epico>/<nome>.md               → "task/checkout/record-order"
                └─ o épico está NO CAMINHO. a task não tem campo "epic".

ENTREGA
  implementation/<epico>/<nome>.md     → mesmo épico e nome da task que responde
  proof/<epico>/<nome>.md              → idem
  review/<nome>.md
```

A entrega merece atenção. Um record de implementação fica **no mesmo caminho da task que responde**.
Logo, `implementation/checkout/record-order.md` responde a `task/checkout/record-order` — e **nenhum
campo diz isso**. Não pode haver desacordo.

### O `<nome>` (o "slug")

É só o nome do arquivo, reduzido a minúsculas com hífens: `record-order`, `total-positive`. A regra
do contrato:

> *"A name reduced to kebab-case. A name that will not reduce is a refusal, not a transliteration."*

Ou seja: `Pedido Não Confirmado` vira `pedido-nao-confirmado`? **Não.** O contrato diz que um nome
que não reduz é uma **recusa**, não uma transliteração — o motor não chuta como transformar acentos.
Nomes vão para inglês em kebab-case.

---

## 5. O índice derivado

Cada raiz tem um `.json` ao lado dos markdown. Ele **nunca é editado**. É gerado:

```bash
python3 bin/graph.py knowledge/
```

Saída real:

```
derived knowledge/graph.json: 6 node(s), 5 edge(s), contract siegard/1
  1 context, 1 aggregate, 2 definition, 1 rule, 1 lifecycle; 2 gap(s); 0 node(s) with rationale
```

### Por que existir um índice, se os arquivos já estão ali?

Porque ler 200 arquivos para responder "quem depende de quem" é caro. O índice tem os **nós** (os
arquivos) e as **arestas** (as referências que os frontmatters declaram), então uma pergunta sobre
estrutura se responde num arquivo só.

```
   knowledge/                                    graph.json
   ┌───────────────────────┐                  ┌──────────────────────────┐
   │ context/sales.md      │                  │ nodes:                   │
   │ definition/sales/     │    graph.py      │   context/sales           │
   │   order.md            │  ──────────────► │   definition/sales/order  │
   │ rule/sales/           │   (deriva E      │ edges:                   │
   │   total-positive.md   │    valida)       │   rule → constrains →     │
   └───────────────────────┘                  │     definition/.../order │
                                              └──────────────────────────┘
```

Uma entrada real do índice:

```json
{
 "id": "definition/sales/order",
 "kind": "definition",
 "file": "definition/sales/order.md",
 "context": "sales",
 "title": "Order",
 "summary": "A customer's order.",
 "digest": "sha256:ea0d00a2b7e35cb1926eb5b81a699e2917318f4a4a867d3c986500bf23bcab02",
 "aggregate": "orders",
 "ddd": "aggregate-root",
 "gaps": ["attributes.[]"]
}
```

Repare no **`digest`**: é o SHA-256 do arquivo `definition/sales/order.md`, e é o valor que uma task
carrega quando vincula esse nó. A [seção 9](#9-o-digest-qual-versão-a-vinculação-leu) explica para
quê.

**Ponto crítico:** o mesmo script é o validador. Ele **se recusa** a gerar o índice sobre uma base
que não fecha. Não existe estado "índice gerado, mas com problemas".

### Os três códigos de saída

Todos os scripts do motor usam os mesmos três:

| código | significa |
|---|---|
| `0` | está tudo de pé |
| `1` | há problemas, ou o índice está desatualizado (*stale*) |
| `2` | não deu para rodar (falta argumento, dependência, arquivo ilegível) |

E a aresta só existe se o **frontmatter** declarar. Uma relação escrita só na prosa não é aresta —
porque duas leituras de um parágrafo produzem dois grafos.

---

## 6. O gap: o que o material não disse

Este é o conceito que mais diferencia o Siegard de qualquer outra coisa.

Suponha a análise de um documento do cliente sobre pedidos. Ele diz o que é um pedido, diz que tem
número e total. **Não diz** quais são todos os campos. O que fazer?

**Errado** (o que qualquer um faria):

```yaml
attributes:
  - name: order_number
    type: string
  - name: total
    type: decimal
  - name: created_at      # ← ninguém disse isso. pareceu razoável.
    type: datetime
```

Esse `created_at` agora é indistinguível de um campo que o cliente ditou. Daqui a um ano ninguém
sabe qual dos três o negócio decidiu.

**Certo** — e aqui há uma sutileza que o validador cobra:

```yaml
# CASO A: o material não deu nenhum campo. O nó não declara `attributes`.
#         Nome nu, porque o campo inteiro está ausente.
gaps:
  - field: attributes
    why: The material describes the order and lists no fields at all.
```

```yaml
# CASO B: o material deu ALGUNS campos. O nó declara `attributes` com o que sabe,
#         e o gap aponta para DENTRO do campo, com caminho pontilhado.
attributes:
  - name: order_number
    type: string
    max_length: 20
  - name: total
    type: decimal
    precision: 12
    scale: 2
gaps:
  - field: attributes.[]           # ← "faltam entradas cujos nomes ninguém deu"
    why: The material names the number and the total, and no complete list.
```

Usar o nome nu no caso B é recusado, e a mensagem ensina o conserto:

```
definition/sales/order: gaps[0]: `attributes` is declared by the node; a gap names
an absent fact. An absence inside `attributes` takes a dotted path
(`attributes.<what-is-missing>`)
```

Existem duas caudas canônicas, e elas mantêm gaps comparáveis entre análises:

| forma | significa |
|---|---|
| `<campo>` | o campo inteiro está ausente (e o nó não o declara) |
| `<campo>.[]` | faltam **entradas** cujos nomes o material não dá |
| `<campo>.<rótulo>` | falta **aquela** coisa nomeada |

Um **gap** é uma declaração formal de ausência. Ele diz: *"este campo está faltando, e a razão é
esta"*. E — aqui está o truque — **o validador aceita um gap no lugar de qualquer campo
obrigatório**. O nó vale, e a falta fica registrada.

```
      ┌──────────────────────────────────────────────────────────┐
      │  material disse?                                         │
      │                                                          │
      │       SIM  ───────────►  escreve o valor no campo        │
      │                                                          │
      │       NÃO  ───────────►  declara um gap nomeando o campo │
      │                                                          │
      │       "é o que dá para ler do que foi dito"              │
      │            ───────────►  escreve o valor + `rationale`   │
      └──────────────────────────────────────────────────────────┘
```

Esse terceiro caso é sutil e importante. `rationale` cobre uma **leitura** do material declarado —
onde cai uma fronteira, que tipo de coisa é algo que foi dito. **Nunca** cobre um valor sobre o qual
o material é silencioso. Um valor plausível é um gap.

### Como ver os gaps abertos

```bash
python3 bin/graph.py --gaps knowledge/
```

Saída real:

```
definition/sales/order: attributes.[]
definition/sales/order-already-placed: attributes
```

Imprime `<identificador>: <campos>` direto dos nós — nunca lendo o `graph.json`. Essa é uma regra de
projeto: relatórios pontuais se pedem ao script, contexto em massa se lê do índice, e os dois
derivam do mesmo pipeline, então não podem discordar.

### A regra de ouro dos gaps

> **Nunca feche um gap com um chute.** Um gap nomeia um fato que só quem conhece o domínio pode
> resolver, e um valor inventado se lê exatamente como um que o negócio ditou.

---

## 7. Os sete tipos de nó, com exemplos reais

Todos os exemplos abaixo saíram dos `examples` do próprio `schemas/node.json` — são formas válidas
por construção.

### 1. `context` — uma fronteira do negócio

```yaml
title: Sales
summary: Ordering, from placement to invoicing.
strategic: core
relationships:
  - with: shipping
    pattern: customer-supplier
    role: upstream
```
*Caminho: `context/sales.md`. É o único tipo com um nível só.*

### 2. `aggregate` — uma fronteira de consistência

```yaml
title: Orders
summary: An order and its lines change together or not at all.
rationale: The material treats order lines as editable rows; making them part of one
  consistency boundary is the analysis's reading.
```
*Caminho: `aggregate/sales/orders.md`. Note o `rationale`: essa fronteira foi uma leitura da
analista, não algo que o material disse com essas palavras. Marcado, e portanto contestável por um
revisor.*

### 3. `definition` — uma coisa do domínio

```yaml
title: Order
summary: A customer's order, from placement to invoicing.
ddd: aggregate-root
aggregate: orders
identity:
  - order_number
aliases:
  - purchase-order
attributes:
  - name: order_number
    type: string
    max_length: 20
    required: true
  - name: total
    type: decimal
    precision: 12
    scale: 2
  - name: customer
    type: ref
    target: definition/sales/customer     # ← isto gera uma aresta no grafo
    binding: by-identity
  - name: state
    type: enum
    lifecycle: lifecycle/sales/order      # ← e isto também
```

### 4. `rule` — uma invariante

```yaml
title: Order total is positive
summary: No order may be placed with a non-positive total.
ddd: invariant
aggregate: orders
statement: An order total MUST be greater than zero.
expression: order.total > 0
constrains:
  - definition/sales/order
```
*`statement` é a regra em prosa normativa. `expression` é a mesma coisa checável. `constrains` diz o
que ela governa — e é uma aresta.*

### 5. `lifecycle` — os estados de algo

```yaml
title: Order lifecycle
summary: The states an order passes through, from draft to closure.
subject: definition/sales/order
states: [draft, placed, cancelled]
initial: draft
terminal: [cancelled]
transitions:
  - from: draft
    trigger: place
    to: placed
    emits: [interface/sales/order-placed]
  - from: draft
    trigger: cancel
    to: cancelled
  - from: placed
    trigger: cancel
    to: cancelled
rejections:
  - from: placed
    trigger: place
    error: definition/sales/order-already-placed
```

Desenhando:

```
         place                cancel
  draft ────────► placed ──────────────► cancelled  (terminal)
    │                │
    │ cancel         │ place  ✗ REJEITA
    └────────────────┴──► definition/sales/order-already-placed
                 ▼
             cancelled
```

**Aqui entra uma verificação bonita do motor: a totalidade.** Para cada par (estado × gatilho), o nó
tem de dizer *alguma coisa* — uma transição, uma rejeição, ou um gap. Se `placed` × `place` não
estivesse coberto, o validador recusa:

```
definition/sales/order: state `placed` has no transition, no rejection and no gap
for trigger `place`; an uncovered pairing is where behaviour gets invented later
```

Vale reler a última parte: *"um par não coberto é onde comportamento é inventado depois"*. É
exatamente o que acontece na vida real — o desenvolvedor chega nesse caso, não acha resposta, e
decide sozinho.

### 6. `interface` — uma mensagem que cruza a fronteira

```yaml
title: Shipment requested
summary: The message this context sends to have an order shipped.
ddd: command
ownership: consumed
payload: definition/sales/shipment-request
gaps:
  - field: upstream
    why: The material does not say which published contract of the shipping context
      this consumes.
```
*Um gap da vida real: sabe-se que consome algo de fora, não se sabe qual contrato. Registrado, não
inventado.*

### 7. `process` — uma sequência que atravessa coisas

```yaml
title: Checkout
summary: Place the order, charge the customer, compensate on failure.
ddd: saga
steps:
  - node: interface/sales/order-placed
  - node: process/payment/charge
    compensated_by: process/payment/refund
```

---

## 8. Do conhecimento ao plano: a vinculação

Agora a segunda camada. Algo vai ser construído. O plano tem três tipos de nó:

| tipo | o que é |
|---|---|
| `inventory` | o que **já existe** no código: módulos, convenções observadas, pontos de reuso, riscos |
| `epic` | uma fatia de escopo, que **declara quais nós da base ela responde** |
| `task` | uma unidade de trabalho: um objetivo, critérios, e a **vinculação** |

### O que é "vincular" (bind)

Uma task **vincula** os nós da base que a governam. Cada entrada carrega o identificador do nó e o
digest daquele nó como a vinculação o leu:

```yaml
title: Record order
summary: Persist a placed order.
objective: A valid order is persisted and retrievable by its order_number.
criteria:
  - Submitting a valid order returns its order_number.
  - An order with a total of zero or less is refused.
nodes:                                              # ← ESTA é a vinculação
  - node: definition/sales/order
    digest: sha256:ea0d00a2b7e35cb1926eb5b81a699e2917318f4a4a867d3c986500bf23bcab02
  - node: rule/sales/total-positive
    digest: sha256:24a0256bf0e8f1df690bbed925f57801ff4a58209c0797a952cd09329a9b9565
  - node: lifecycle/sales/order
    digest: sha256:fc9f08af5d0bdd1f5476238d43f454f61169398a7ab2f73e3fbaf831958db00c
unresolved:
  - gap: definition/sales/order#attributes.[]
```

A definição no contrato:

> *"The base nodes that govern this task, each with the digest of the node as this binding read it.
> **This is the binding**: the executor reads exactly these."*

Repare em "**exatamente estes**". Quem for implementar a task lê esses nós e mais nenhum. Isso é o
que faz a task ser autocontida: não é "leia a base e se vire", é "estes três fatos governam este
trabalho".

```
  BASE                                    PLANO
  ┌────────────────────────┐              ┌──────────────────────────┐
  │ definition/sales/order │◄─── binds ───│ task/checkout/           │
  │ rule/sales/total-pos.  │◄─── binds ───│   record-order           │
  │ lifecycle/sales/order  │◄─── binds ───│                          │
  │ definition/sales/coupon│              │ (não vincula o cupom —   │
  └────────────────────────┘              │  não governa este work)  │
                                          └──────────────────────────┘
```

O par (nó, digest) fica numa entrada só, e não em duas listas paralelas, pelo mesmo motivo de não
existir campo `id` num nó: duas listas podem se separar, uma entrada não.

### `objective` e `criteria`

O contrato é exigente aqui:

- **`objective`**: *"The one falsifiable outcome this task delivers. Two outcomes are two tasks."*
- **`criteria`**: *"each falsifiable on its own. 'Works correctly' is prose; 'a rejected order
  returns the stated domain error' is a criterion."*

"Falsificável" quer dizer: dá para escrever um teste que **falharia** se aquilo parasse de valer.
"Funciona bem" não é critério porque nenhum teste pode falhar por causa disso.

### Nenhum status, nenhuma estimativa, nenhuma ordem

Uma task **não tem** campo de status, prioridade, estimativa ou ordem de execução. Esses campos não
existem no contrato. A ordem se deriva das dependências (`depends_on`), e o estado da execução mora
no git.

---

## 9. O digest: qual versão a vinculação leu

### O problema que ele resolve

A task acima vinculou `definition/sales/order`. Quem implementar vai ler esse nó e escrever código
conforme ele. Ótimo.

Mas… **quando** a task foi vinculada? Esse nó mudou desde então? Se alguém acrescentou um atributo
obrigatório ao pedido depois que a task foi escrita, a task está desatualizada — e nada no arquivo
diria isso, porque o nome do nó (`definition/sales/order`) continua idêntico.

### A solução: identidade por conteúdo

Um **digest** é o SHA-256 dos **bytes** de um arquivo:

```bash
$ sha256sum knowledge/definition/sales/order.md
ea0d00a2b7e35cb1926eb5b81a699e2917318f4a4a867d3c986500bf23bcab02
```

Escrito no nó como `sha256:ea0d00a2…`. A definição no contrato:

> *"Content identity: the SHA-256 of the bytes of whatever artifact the field carrying it names. A
> pin records **which version** of that artifact a judgment read, so an artifact that moved
> afterwards is visible to the validator rather than assumed unchanged."*

### A divisão que é a chave

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │    O CAMINHO diz    ────►   QUAL coisa é                         │
  │                                                                  │
  │    O DIGEST diz     ────►   QUAL VERSÃO dela                     │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
```

O digest é sempre **do arquivo inteiro** — frontmatter e corpo. Isso é escolha: um digest só do
frontmatter perderia o que a seção `## Rules` aponta, e não seria recomputável com um comando só. E
um valor que só a ferramenta sabe verificar é uma alegação; o ponto de um digest é ser uma
verificação.

### Vendo funcionar

Base montada, índice derivado, task escrita com os digests que o índice lista, plano validado:

```bash
$ python3 bin/plan.py work/ knowledge/
derived work/plan.json: 3 node(s), 6 edge(s), contract siegard-plan/2
  1 inventory, 1 epic, 1 task; 1 unresolved gap citation(s) (1 unique); ...
```

**Primeiro teste — a base cresce com um nó que a task não vincula.** Acrescentando
`definition/sales/coupon`, um cupom de desconto sem relação nenhuma com como um pedido é gravado:

```bash
$ python3 bin/graph.py knowledge/
derived knowledge/graph.json: 7 node(s), 5 edge(s), contract siegard/1

$ python3 bin/plan.py work/ knowledge/
derived work/plan.json: 3 node(s), 6 edge(s), contract siegard-plan/2      ← segue válido
```

Nada aconteceu, e está certo: nada que governa a task mudou.

**Segundo teste — muda o nó que a task VINCULA.** Alterando `max_length` de 20 para 8 em
`definition/sales/order`:

```
task/checkout/record-order: definition/sales/order is pinned at sha256:ea0d00a2… and
stands at sha256:2ab1b82b…; the binding read this node before it moved — re-bind the
task against the node as it now reads, or restate the digest deliberately once the
change is known not to bear on it
```

Três coisas nessa mensagem, e cada uma é deliberada. Ela **nomeia o nó** que se moveu, não só a
task. Ela dá **os dois digests**, então dá para conferir à mão. E ela oferece **as duas saídas**,
porque a escolha entre elas é de julgamento.

### As duas saídas

| saída | quando | o que fazer |
|---|---|---|
| **re-vincular** | a mudança afeta esta task | refaz a vinculação contra o nó como ele lê hoje |
| **reafirmar o digest** | a mudança não afeta esta task | escreve o digest novo à mão |

A palavra "deliberately" na mensagem está lá porque a diferença entre as duas é **alguém ter olhado
ou não**.

### Os quatro pins do motor

```
  ┌─────────────┐  nodes[].digest:  um por nó vinculado
  │ task        │ ──────────────────────────────────► knowledge/<nó>.md
  └─────────────┘

  ┌─────────────┐  task:  pina o ARQUIVO da task
  │implementation│ ─────────────────────────────────► work/task/<ep>/<n>.md
  └─────────────┘

  ┌─────────────┐  implementation:  pina o record de implementação
  │ proof       │ ──────────────────────────────────► delivery/implementation/…
  └─────────────┘     (pega o caso: o código foi reescrito e os testes não)

  ┌─────────────┐  standardRef.pin:  pina a cópia do standard que leu
  │ review      │ ──────────────────────────────────► delivery/standards/<f>
  └─────────────┘
      └─ uma review NÃO pina a task: a totalidade de cobertura já a
         prende aos critérios como eles estão.
```

Nenhum nó da base carrega pin: a base é o topo da cadeia e não aponta para nada anterior.

### Por que hash, e não data nem número de versão

| mecanismo | por que não |
|---|---|
| timestamp | diz *quando* alguém leu, não *o quê*. Dois arquivos diferentes têm a mesma data; o mesmo arquivo pode ser tocado sem mudar. |
| número de versão | exige que alguém incremente. A hora em que esquecem é a hora em que importava. |
| **hash** | não precisa de ninguém. Recomputável por qualquer um, num comando. **Não pode concordar com um arquivo que mudou.** |

---

## 10. As totalidades: nada passa em silêncio

O motor tem várias verificações do tipo "isto tem de estar completo". Elas são o coração da coisa,
porque **o modo normal de errar é o silêncio**: não escrever nada sobre algo.

### Totalidade 1 — cobertura do épico

Um épico declara `covers`: os nós da base pelos quais ele responde. Então, para cada nó em `covers`,
**uma das duas** tem de valer:

```
   ┌────────────────────────────────────────────────────────────┐
   │  nó em covers                                              │
   │        │                                                   │
   │        ├──► uma task do épico o vincula          ✔        │
   │        │                                                   │
   │        └──► está em `uncovered`, com um porquê   ✔        │
   │                                                            │
   │        nenhuma das duas  ────────────────────►   ✗ RECUSA │
   └────────────────────────────────────────────────────────────┘
```

Recusa real:

```
epic/checkout: covers names definition/sales/order, which no task under it binds
and uncovered does not declare; a covered node reaches a task or a stated why,
never neither — bind it in a task under this epic, or declare it in `uncovered`
with a why
```

E vale nos dois sentidos: uma task que vincula algo **fora** do `covers` do seu épico também é
recusada — porque vinculação fora da declaração é escopo que o plano não declarou.

### Totalidade 2 — triagem de gaps

Se uma task vincula um nó que tem um **gap aberto**, a task tem de dizer algo sobre ele:

```
   ┌─────────────────────────────────────────────────────────────────┐
   │  gap aberto num nó vinculado                                    │
   │        │                                                        │
   │        ├──► `unresolved`  → "preciso disto, e a base não tem"   │
   │        │                     (bloqueia a entrega!)              │
   │        │                                                        │
   │        └──► `waived`      → "não afeta esta task, porque X"     │
   │                                                                 │
   │        silêncio  ─────────────────────────────────►   ✗ RECUSA │
   └─────────────────────────────────────────────────────────────────┘
```

A diferença entre os dois é enorme:

- **`unresolved`** = a task **não pode ser entregue**. O fato tem de ser produzido na base primeiro,
  via `/analyse-domain`, e a task re-vinculada. Escrever código por cima de um `unresolved` faz o
  que se escrever se ler exatamente como uma decisão do negócio, no único lugar onde ninguém vai
  procurar por uma decisão.
- **`waived`** = julgamento registrado de que aquele gap não importa aqui. É uma alegação que um
  revisor pode **rejeitar** — e é por isso que exige um porquê.

### Totalidade 3 — o record responde a tudo

Um record de implementação tem de responder a **cada critério** da task e a **cada nó vinculado**.
Silêncio sobre qualquer um é recusado:

```
implementation/checkout/record-order: the task binds definition/sales/order, and
this record does not say how the source answers to it; a bound node passed over in
silence is the base going unanswered in code — answer it in `nodes`, or re-bind the
task through /plan-work if it does not govern this work
```

---

## 11. A entrega

Três tipos de nó, e uma separação que é o ponto todo:

| tipo | o que registra | quem escreve |
|---|---|---|
| `implementation` | o que o código faz, critério por critério, nó por nó | um agente |
| `proof` | o que os testes provam, e o que **não** provam | **outro** agente, em contexto separado |
| `review` | o que quatro passes acharam | mais quatro agentes |

### Por que implementação e prova são agentes separados

Porque:

> *"uma implementação e seus testes escritos numa passada concordam por construção, **inclusive onde
> os dois estão errados**."*

Se o mesmo agente escreve o código e o teste, o teste testa o que o código faz — não o que o
critério pede. Separar os contextos é o que faz o teste ser uma verificação.

### Por que ninguém que julga também executa

`bin/run.py` roda os comandos do consumidor e grava o que imprimiram. Ele **não conta testes** —
parsear formato de reporter é conhecimento de stack, e o motor não tem nenhum.

E `/implement-task` **não roda nada**. A razão: quem escreve o código não pode testemunhar se
passou, ou itera até ficar verde e o que falhou não existe em lugar nenhum.

```
   ┌──────────────────┐         ┌──────────────────┐        ┌───────────────┐
   │ /implement-task  │         │    bin/run.py    │        │ /review-change│
   │                  │         │                  │        │               │
   │ escreve código   │         │ executa e grava  │        │ julga o que   │
   │ escreve testes   │         │ o que imprimiu   │        │ está gravado  │
   │                  │         │                  │        │               │
   │ NÃO EXECUTA      │         │ NÃO JULGA        │        │ NÃO EXECUTA   │
   └──────────────────┘         └──────────────────┘        └───────────────┘
```

### As quatro passes da review

| passe | pergunta |
|---|---|
| **coverage** | os testes realmente provam os critérios da task? |
| **base conformance** | o código afirma só o que a base sustenta? |
| **standard conformance** | segue o standard que o **projeto** definiu para si? |
| **failures** | por que a suite falhou? |

E a review produz **evidência, nunca veredito**:

> *"Um finding com o qual ninguém pode discordar é uma decisão vestida de finding. Quem decide é uma
> pessoa, lendo o que você escreveu."*

Não há severidade, nem nota, nem ranking, nem "isto bloqueia". Se a review calculasse veredito, a
revisora seria o portão — e foi exatamente disso que este desenho fugiu.

### O standard do projeto

O framework embarca o **contrato** de um standard (`schemas/standard.json`), o passe e as
verificações — e **nenhuma regra**. Porque as convenções de uma stack não são de um domínio, e um
framework que as embarcasse prescreveria TypeScript a um projeto em Go.

Um projeto pode ter **vários** registros — o contrato diz isso no campo `standard`: *"One project
may hold several — a backend's rules are not a frontend's — and each is named where it is used."* A
restrição é um registro **por invocação**.

Cada regra do standard se marca com `decided_by`:

- **`reading`** — dizer se vale exige entender o que o código significa. É do passe de standard, e um
  finding cita a regra pelo id.
- **`tool`** — um linter ou compilador decide exato e barato. **Não é trabalho de modelo:** roda como
  passo da suite do projeto, e o que achar chega pelo passe de falhas.

> *"Um modelo aplicando uma regra que o linter tem tem recall estritamente pior que o linter, e custa
> mais."*

E um projeto que não escreveu standard nenhum recebe uma review **honestamente estreita** — o passe
registra que não rodou e o que faltava — **nunca uma review limpa**.

---

## 12. Os quatro pontos de entrada

```
  material do cliente
  (documento, reunião, prosa)
         │
         ▼
  ┌─────────────────────┐
  │  /analyse-domain    │  vira nós de conhecimento, valida, deriva graph.json
  └──────────┬──────────┘
             │  handoff: a invocação de /plan-work pronta para colar
             ▼
  ┌─────────────────────┐
  │  /plan-work         │  vira inventário + épicos + tasks, valida CONTRA a base
  └──────────┬──────────┘
             │  handoff: a invocação de /implement-task, com a task como slot
             ▼
  ┌─────────────────────┐
  │  /implement-task    │  escreve código + testes, grava os dois records
  └──────────┬──────────┘     UMA invocação, UMA task
             │  handoff: a invocação de /review-change, com o file set já preenchido
             ▼
  ┌─────────────────────┐
  │  /review-change     │  captura a execução, roda quatro passes, grava findings
  └──────────┬──────────┘
             │
             ▼
       uma PESSOA lê
```

**Cada um para e devolve o controle.** Nenhum chama o próximo. O relatório termina com a invocação
seguinte pronta para colar e os espaços em branco — preencher e rodar é do humano.

E cada um termina do mesmo jeito:

> *"Then stop. `git diff` sobre a raiz é a revisão, e ela pertence a uma pessoa."*

Existem dois comandos auxiliares, que não são pontos de entrada:

```bash
python3 bin/terms.py             # todos os termos, lidos do contrato que os define
python3 bin/terms.py pin         # só um
python3 bin/run.py …             # executa os comandos do consumidor e grava a saída
```

---

## 13. A parada é a funcionalidade

Isto costuma ser o que mais estranha quem chega: o motor **recusa muito**. E recusar é o produto,
não a falha.

Existem 24 condições distintas de parada nas quatro skills. Todas antes de escrever qualquer coisa:

```
  ┌────────────────────────────────────────────────────────────────────┐
  │  ANTES de escrever qualquer arquivo, verifica:                      │
  │                                                                     │
  │  ✗ a raiz tem mudanças não commitadas?      → PARA                 │
  │      (porque `git diff` é a revisão, e ela só diz o que ESTA        │
  │       invocação fez se a raiz começar limpa)                        │
  │                                                                     │
  │  ✗ a base/plano não fecha?                  → PARA                 │
  │  ✗ falta um input que ninguém nomeou?       → PARA                 │
  │  ✗ a task tem entradas `unresolved`?        → PARA                 │
  │  ✗ a task tem nota `BLOCKING`?              → PARA                 │
  └────────────────────────────────────────────────────────────────────┘
```

E a parada é **uma só, junta**:

> *"Absent inputs stop once, together: one stop naming everything missing, so the human answers once
> — never a question at a time."*

### Três paradas que só uma pessoa resolve

| parada | por que é do humano |
|---|---|
| um **gap** | nomeia um fato que só quem conhece o domínio afirma, e um valor inventado se lê igual a um afirmado |
| **raiz suja** | é decisão de git — commitar, descartar, ignorar — e nenhuma das três é de uma skill |
| nota **`BLOCKING`** | é o escopo e a base se contradizendo, e as duas saídas passam por um ponto de entrada que alguém invoca |

Todo o resto é **forma**, e forma a própria invocação corrige. A regra que separa as duas:

> **"Fixing means form, never knowledge."** Um valor fora de vocabulário, uma lista onde cabia um
> mapa, um digest malformado — é da invocação corrigir. Um fato ausente é um gap.

---

## 14. Exemplo completo de ponta a ponta

Um requisito, do começo ao fim.

### O material

> *"Cliente monta um pedido com número e valor total. Não pode fechar pedido com total zerado ou
> negativo. Depois de fechado, não pode fechar de novo."*

### Passo 1 — `/analyse-domain` produz nós

```
knowledge/
├── context/sales.md
├── aggregate/sales/orders.md
│
├── definition/sales/order.md
│      ddd: aggregate-root
│      identity: [order_number]
│      attributes: [order_number, total]
│      gaps:
│        - field: attributes.[]
│          why: The material names the number and the total, and no complete list.
│                            ↑ o material NÃO listou todos os campos.
│                              declarado, não inventado. Caminho pontilhado,
│                              porque o campo ESTÁ declarado.
│
├── definition/sales/order-already-placed.md
│      ddd: domain-error
│      gaps:
│        - field: attributes
│          why: The material states the refusal and carries no payload for it.
│                            ↑ o erro que a rejeição do ciclo de vida nomeia.
│                              Tem de existir como nó: uma rejeição não pode
│                              apontar para um erro que a base não sustenta.
│
├── rule/sales/total-positive.md
│      statement: An order total MUST be greater than zero.
│      constrains: [definition/sales/order]
│
├── lifecycle/sales/order.md
│      states: [draft, placed]
│      transitions: draft --place--> placed
│      rejections: placed --place--> definition/sales/order-already-placed
│                            ↑ "não pode fechar de novo" — uma REJEIÇÃO,
│                              não uma transição
│
└── graph.json      ← gerado por graph.py
```

Saída real, desta base exata:

```bash
$ python3 bin/graph.py knowledge/
derived knowledge/graph.json: 6 node(s), 5 edge(s), contract siegard/1
  1 context, 1 aggregate, 2 definition, 1 rule, 1 lifecycle; 2 gap(s); 0 node(s) with rationale

$ python3 bin/graph.py --gaps knowledge/
definition/sales/order: attributes.[]
definition/sales/order-already-placed: attributes
```

### Interlúdio: dois erros que o validador pega na porta

Vale mais do que qualquer explicação. A base acima, montada pela primeira vez, foi recusada com
**dois problemas — os dois exatamente os que a [seção 16](#16-erros-comuns-e-o-que-significam)
cataloga**:

```
definition/sales/order-already-placed: frontmatter: 'attributes' is a required property
definition/sales/order: gaps[0]: `attributes` is declared by the node; a gap names an
absent fact. An absence inside `attributes` takes a dotted path
```

O primeiro: o nó do erro de domínio foi escrito sem `attributes`, e um `definition` exige o campo.
Não bastava omitir — a ausência tem de ser **declarada**, com um gap. O segundo: `attributes` foi
declarado com dois campos **e** gapeado com o nome nu. O validador não deixa as duas coisas
coexistirem, e a mensagem já traz o conserto (`attributes.[]`).

Nenhum dos dois erros é bobo, e nenhum dos dois seria pego por revisão humana com confiabilidade. É
isto que o motor compra: os erros de forma param na porta, e o que sobra para uma pessoa revisar é
**julgamento** — se o gap é legítimo, se a regra foi bem lida.

### Passo 2 — `/plan-work` produz o plano

```
work/
├── intake/scope.md                       ← o material, preservado como foi dado
├── inventory/order-service.md
├── epic/checkout.md
│      covers: [definition/sales/order, rule/sales/total-positive,
│               lifecycle/sales/order]
│
├── task/checkout/record-order.md
│      objective: A valid order is persisted and retrievable by its order_number.
│      criteria:
│        - Submitting a valid order returns its order_number.
│        - An order with a total of zero or less is refused.
│      nodes:
│        - node: definition/sales/order
│          digest: sha256:ea0d00a2…
│        - node: rule/sales/total-positive
│          digest: sha256:24a0256b…
│        - node: lifecycle/sales/order
│          digest: sha256:fc9f08af…
│      unresolved:
│        - gap: definition/sales/order#attributes.[]
│                    ↑ o gap da base bloqueia: a task PRECISA da lista de campos.
│                      A citação é <identificador-do-nó>#<campo-do-gap>.
│
└── plan.json
```

Saída real:

```bash
$ python3 bin/plan.py work/ knowledge/
derived work/plan.json: 3 node(s), 6 edge(s), contract siegard-plan/2
  1 inventory, 1 epic, 1 task; 1 unresolved gap citation(s) (1 unique); 0 open question(s); 0 waived

$ python3 bin/plan.py --unresolved work/ knowledge/
task/checkout/record-order:
  gap definition/sales/order#attributes.[]
```

Note que o plano **valida** com um `unresolved` aberto. Um plano com pendência é um plano legítimo —
o que ele não é, é entregável. É a próxima etapa que para.

### Passo 3 — `/implement-task` **PARA**

A skill começa perguntando ao próprio motor o que é entregável. Saída real:

```bash
$ python3 bin/deliver.py --outstanding delivery/ work/ knowledge/
task/checkout/record-order: no record; 1 unresolved entry(ies), which /analyse-domain settles
```

Duas coisas ali. "no record" — nada foi entregue ainda. E "1 unresolved entry(ies), **which
/analyse-domain settles**" — o próprio motor diz para onde ir. A skill então para:

```
PARADA: The task carries unresolved entries.
  definition/sales/order#attributes.[] — the material names the number and the
  total, and no complete list.

O fato é produzido na base, via /analyse-domain, e a task re-vinculada depois.
```

**É aqui que o motor ganha o salário.** Sem ele, o desenvolvedor teria inventado os campos que
faltavam, e a invenção teria virado "o que o sistema faz" para sempre.

### Passo 4 — o ciclo fecha

O cliente responde: *"tem também data de criação e o cliente que pediu"*. Roda-se `/analyse-domain`
de novo, o gap fecha com fatos **afirmados**, o digest daquele nó muda, a task é re-vinculada, o
`unresolved` sai — e só então `/implement-task` escreve código.

```
implementation/checkout/record-order.md
     criteria:
       - criterion: Submitting a valid order returns its order_number.
         met: true
         how: place() returns the persisted order_number unchanged
     nodes:
       - node: definition/sales/order
         encoded_at: [src/orders/place.ts]
         how: the order's identity and attributes are the shape place() persists
     task: sha256:…                      ← pina a redação da task

proof/checkout/record-order.md
     implementation: sha256:…            ← pina o record acima
     tests:
       - file: tests/place.spec.ts
         proves: Submitting a valid order returns its order_number.
         fails_when: place() answers with anything but the stored order_number
                        ↑ isto é o que faz o teste ser prova:
                          o que teria de quebrar para ele falhar
```

### Passo 5 — `/review-change`

Captura a execução, roda as quatro passes, grava findings com evidência. Uma pessoa lê e decide o
que significam.

---

## 15. Glossário

Consultável a qualquer momento com `python3 bin/terms.py`, que lê cada definição do contrato que a
enuncia — nunca de uma cópia.

| termo | em português simples |
|---|---|
| **nó** (node) | um arquivo markdown com frontmatter. A unidade de tudo. |
| **raiz** (root) | um dos três diretórios: conhecimento, trabalho, entrega. |
| **base** | a raiz de conhecimento e seus nós. Nomeia só isso. |
| **slug** | o nome do arquivo em kebab-case. |
| **gap** | uma ausência declarada: um fato que o material não disse. |
| **rationale** | marca um valor que a análise **decidiu** lendo o material, em vez de ler literalmente. Contestável. |
| **vincular** (bind) | uma task listar os nós da base que a governam, com o digest de cada um. |
| **vinculado** (bound) | dito de um nó que uma task listou. |
| **digest** | o SHA-256 dos bytes de um arquivo: qual versão dele um julgamento leu. |
| **pin** | o mesmo mecanismo, do lado da entrega: o digest do artefato que um record responde. |
| **covers** | os nós da base pelos quais um épico responde. |
| **uncovered** | os nós que o épico reivindicou e este plano deixa de fora, cada um com porquê. |
| **unresolved** | o que a task precisa e a base não tem. **Bloqueia a entrega.** |
| **waived** | um gap que não afeta esta task, com o porquê. Um revisor pode rejeitar. |
| **criterion** | uma condição falsificável por si só. |
| **record** | um nó de entrega: o que foi feito ou achado. |
| **proof** | o nó que registra o que os testes provam — e o que não provam. |
| **standard** | as regras que o **projeto** definiu para si. O framework não embarca nenhuma. |
| **stale** | o índice derivado não corresponde mais aos nós. Rodar o script de novo. |
| **intake** | onde o material lido fica preservado. Nunca validado como nó. |
| **closure** | um `closure.md` na raiz de trabalho marca o plano encerrado. Vira história. |

---

## 16. Erros comuns e o que significam

Todas as mensagens abaixo são reais. O formato é sempre:

```
<onde>: <o que está errado>; <por que importa — e o que fazer>
```

### "the path is the identity and this one computes to none"

Um arquivo num caminho que não vira identificador nenhum. Ex.: `notas.md` na raiz de conhecimento.
Material de leitura vai em `intake/` ou `run/`, que nunca são validados como nós.

### "gaps[0]: `attributes` is declared by the node; a gap names an absent fact"

O campo foi declarado **e** dito faltante. Escolha um. Se parte do campo falta, o gap usa caminho
pontilhado: `attributes.[]` ou `attributes.customer`.

### "…is pinned at … and stands at …"

O nó vinculado mudou depois da vinculação. Ou re-vincular a task, ou reafirmar o digest de propósito.
A mensagem nomeia o nó. Ver a [seção 9](#9-o-digest-qual-versão-a-vinculação-leu).

### "a covered node reaches a task or a stated why, never neither"

Um épico reivindicou um nó e nenhuma task dele o vincula, nem `uncovered` o declara. Ou criar a task,
ou declarar em `uncovered` com o porquê.

### "a bound node passed over in silence is the base going unanswered in code"

O record não disse como o código responde a um nó que a task vinculou. Ou responder em `nodes`, ou
re-vincular a task se aquele nó não governa este trabalho.

### "an unnamed refusal is a gap, never an invented domain error"

O nó diz que algo é rejeitado e não nomeia o erro. Se o material não disse qual erro, isso é um gap —
não um código de erro inventado.

### "an uncovered pairing is where behaviour gets invented later"

Um par (estado × gatilho) do ciclo de vida sem transição, sem rejeição e sem gap. Dizer alguma coisa
sobre ele, mesmo que seja "ninguém disse".

### "STALE: … is not what the nodes derive to"

O `.json` não corresponde aos markdown. Rodar o script sem `--check` para reescrever. **Não editar o
json** — todo fato nele mora num arquivo de nó.

### "a finding citing no rule is taste with a location attached"

Um finding do passe de standard sem citar a regra pelo id. Sem regra citada, é opinião com endereço.

---

## 17. Migrando de 1.x para 2.0.0

A 2.0.0 mudou como uma task pina a base, e a mudança **invalida todo nó de plano escrito na 1.x**.

**O que era:** uma task carregava um campo `base` — um SHA-256 único, do `graph.json` inteiro — e
`nodes` era uma lista de identificadores nus.

**Por que mudou:** o índice não carrega o conteúdo dos nós. Então reescrever os `attributes` de um
nó vinculado não movia o pin, e a task continuava válida sobre um fato que mudou debaixo dela; ao
mesmo tempo, mudar o `title` de qualquer nó movia o pin e staleava **todas** as tasks do plano,
inclusive as que vinculam outros nós. Calado no caso que importa, barulhento no que não importa.

**O que é agora:** cada entrada de `nodes` carrega `node` e `digest`, e o campo `base` não existe. A
task stalea quando um nó **que ela vincula** se move, e a recusa nomeia esse nó.

### O que um plano existente precisa

Um script de uso único faz a conversão. Ele **não é distribuído** — mora em `tools/`, fora de
`src/claude/`:

```bash
$ python3 tools/migrate_plan_pins.py <work-root> <knowledge-root> --dry-run
$ python3 tools/migrate_plan_pins.py <work-root> <knowledge-root>
```

Ele lê a vinculação que a task já tem, estampa em cada entrada o digest que o índice já lista, remove
o `base`, e não toca em mais nada. A reescrita é textual, e não um round-trip de YAML, para que o
`git diff` continue legível — que é justamente a revisão que a migração existe para passar.

Antes e depois, saída real:

```yaml
# antes
nodes:
  - definition/sales/order
  - definition/sales/coupon
base: sha256:2a879742…
```

```yaml
# depois
nodes:
  - node: definition/sales/order
    digest: sha256:602d0d27…
  - node: definition/sales/coupon
    digest: sha256:279fb43a…
```

```
task/checkout/record: 2 digest(s) stamped, base removed

migrated 1 task(s); 0 already migrated. Validate with plan.py, and read the diff.
```

Três propriedades que valem conhecer: ele é **idempotente** (rodar duas vezes reporta "already
migrated"); ele **recusa** uma vinculação que nomeia um nó que a base não tem, em vez de inventar um
digest que nenhum `sha256sum` reproduz; e quando qualquer task está no caminho, **não escreve nada** —
nem as que estavam boas.

Depois de migrar, validar e ler o diff:

```bash
$ python3 bin/plan.py <work-root> <knowledge-root>
```

---

## Em uma frase

> O Siegard força cada fato de domínio que o código codifica a apontar para um nó que o negócio
> decidiu; cada mudança a apontar para uma task; e cada task a apontar para a versão exata de cada
> nó que leu — e recusa, em vez de adivinhar, sempre que um desses elos não fecha.

O resto do motor é a mecânica que torna essa frase verificável em vez de aspiracional.
