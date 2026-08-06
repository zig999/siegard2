# Siegard explicado do zero

> Material didático sobre o motor deste repositório, em `.docs/`, escrito em português por
> decisão explícita do mantenedor.
>
> **Nota sobre idioma:** a seção Language de `/CLAUDE.md` exige que todo artefato do
> repositório seja em inglês (en-US), e nomeia `docs` entre eles. Este arquivo é a exceção
> deliberada, decidida com a regra sobre a mesa. Enquanto a regra não registrar a exceção,
> ele é o único artefato do repositório fora dela.
>
> Todos os exemplos de nó vieram dos `examples` dos próprios schemas, e todas as
> mensagens de erro citadas são saída real dos validadores, capturada rodando o motor.

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
9. [O pin](#9-o-pin)
10. [As totalidades: nada passa em silêncio](#10-as-totalidades-nada-passa-em-silêncio)
11. [A entrega](#11-a-entrega)
12. [Os quatro pontos de entrada](#12-os-quatro-pontos-de-entrada)
13. [A parada é a funcionalidade](#13-a-parada-é-a-funcionalidade)
14. [Exemplo completo de ponta a ponta](#14-exemplo-completo-de-ponta-a-ponta)
15. [Glossário](#15-glossário)
16. [Erros comuns e o que significam](#16-erros-comuns-e-o-que-significam)

---

## 1. Que problema isso resolve

Imagine um projeto de software normal. Alguém do negócio explica uma regra numa reunião.
Um desenvolvedor entende, escreve o código. Seis meses depois:

- A regra está no código, misturada com detalhes técnicos.
- Está também num Jira fechado, com a redação de quem abriu o ticket.
- Está num comentário `// pedido não pode ter total zero`, que ninguém atualizou.
- Está na cabeça de duas pessoas, uma das quais saiu.

E quando alguém pergunta *"por que o sistema recusa esse pedido?"*, a resposta honesta é
"vamos ler o código e descobrir". O código passou a ser a fonte da verdade sobre o que o
**negócio decidiu** — e isso é uma inversão. O código deveria ser uma *consequência* da
decisão, não o lugar onde ela mora.

Pior: quando o código é a única fonte, **não existe diferença visível entre uma decisão do
negócio e um chute de quem programou**. As duas coisas parecem exatamente iguais no
arquivo. Um `if total <= 0: reject()` pode ser uma regra que o cliente ditou ou uma
suposição de terça-feira à tarde.

### O que o Siegard faz

Ele separa isso em três camadas e obriga cada uma a apontar para a anterior:

```
   O que o negócio decidiu   →   O que vamos construir   →   O que foi construído
        (conhecimento)                  (plano)                    (entrega)
```

E acrescenta uma regra que muda tudo:

> **Um fato que ninguém disse não é inventado. É declarado como ausente.**

É essa regra que faz a diferença entre decisão e chute ficar visível. Se o material nunca
disse qual é o total mínimo de um pedido, o nó **não escreve zero**. Ele escreve: *este
fato está em falta, e só quem conhece o domínio pode preenchê-lo.*

---

## 2. A ideia central em uma página

Três diretórios. Cada um cheio de arquivos markdown. Cada um com um índice gerado por
script e um validador que **se recusa** a gerar o índice se as coisas não fecharem.

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
                               │  e "pina" a versão da base que leu
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RAIZ DE TRABALHO              "o que vamos construir"                      │
│  work/                                                                      │
│    inventory/order-service.md          ← o que já existe no código          │
│    epic/checkout.md                    ← um fatia de escopo                 │
│    task/checkout/record-order.md       ← uma unidade de trabalho            │
│    plan.json                           ← GERADO.                            │
│                                                                             │
│  validador: bin/plan.py   (valida o plano CONTRA a base)                    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  cada record responde a uma task
                               │  e "pina" a versão da task que respondeu
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

1. **Tudo é markdown.** Nada de banco de dados, nada de estado escondido. Você abre no
   editor e lê.
2. **Nenhum nó tem status.** Não existe campo "em andamento", "pronto", "aprovado". O
   estado da execução mora no git. Um plano que registrasse progresso seria um arquivo de
   estado de orquestrador, e o framework recusa ter um.
3. **Os `.json` são derivados.** Você nunca os edita. Você muda os markdown e roda o
   script. Se você editar o json à mão, o próximo `--check` acusa.

---

## 3. O nó: a unidade de tudo

Um **nó** é um arquivo markdown com duas partes: um cabeçalho de dados (o *frontmatter*,
entre `---`) e um corpo de prosa.

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

O validador **só valida o frontmatter**. O corpo é para você. Mas mesmo o corpo tem forma
obrigatória: exatamente dois cabeçalhos, na ordem. Num nó de conhecimento são
`## What it is` e `## Rules`. Numa task ou num record são `## What it is` e `## Notes`.
Uma seção sem nada a dizer carrega literalmente a linha `None.` — porque uma seção ausente
e uma seção vazia contam histórias diferentes, e o framework quer a diferença explícita.

> **Por que isso importa:** um fato que more só na prosa é um fato que duas pessoas leem de
> dois jeitos. Se é fato, vai no frontmatter, onde tem nome e o validador o alcança.

---

## 4. O caminho é a identidade

Esta é **a ideia mais importante do motor inteiro**. Se você entender só uma coisa, entenda
esta.

Num sistema normal, um registro tem um `id`:

```yaml
id: order-definition-001     # ← um campo
type: definition             # ← outro campo
context: sales               # ← outro campo
```

Três campos que podem **discordar** do lugar onde o arquivo está. Você move o arquivo e
esquece de atualizar o `context`. Agora existem duas respostas para "a que contexto isso
pertence", e nenhuma é autoridade.

No Siegard, o caminho **é** o identificador:

```
knowledge/definition/sales/order.md
          └────┬───┘ └─┬─┘ └─┬─┘
              tipo  contexto  nome
```

E por isso **não existe campo `id`, nem `type`, nem `context`**. Não podem discordar do
caminho porque não existem. O validador extrai o tipo e o contexto do caminho e pronto.

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

Olhe a entrega com atenção. Um record de implementação fica **no mesmo caminho da task que
responde**. Logo, `implementation/checkout/record-order.md` responde a
`task/checkout/record-order` — e **nenhum campo diz isso**. Não pode haver desacordo.

### O `<nome>` (o "slug")

É só o nome do arquivo, reduzido a minúsculas com hífens: `record-order`, `total-positive`.
A regra do contrato:

> *"A name reduced to kebab-case. A name that will not reduce is a refusal, not a
> transliteration."*

Ou seja: `Pedido Não Confirmado` vira `pedido-nao-confirmado`? **Não.** O contrato diz que
um nome que não reduz é uma **recusa**, não uma transliteração — o motor não vai chutar
como transformar acentos. Nomes vão para inglês em kebab-case.

---

## 5. O índice derivado

Cada raiz tem um `.json` ao lado dos markdown. Ele **não é editado nunca**. É gerado:

```bash
python3 bin/graph.py knowledge/          # gera knowledge/graph.json
```

Saída real:

```
derived knowledge/graph.json: 3 node(s), 1 edge(s), contract siegard/1
  1 context, 1 aggregate, 1 definition; 0 gap(s); 0 node(s) with rationale
```

### Por que existir um índice, se os arquivos já estão ali?

Porque ler 200 arquivos para responder "quem depende de quem" é caro. O índice tem os
**nós** (os arquivos) e as **arestas** (as referências que os frontmatters declaram), então
uma pergunta sobre estrutura se responde num arquivo só.

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

**Ponto crítico:** o mesmo script é o validador. Ele **se recusa** a gerar o índice sobre
uma base que não fecha. Não existe estado "índice gerado, mas com problemas".

### Os três códigos de saída

Todos os scripts do motor usam os mesmos três:

| código | significa |
|---|---|
| `0` | está tudo de pé |
| `1` | há problemas, ou o índice está desatualizado (*stale*) |
| `2` | não deu para rodar (falta argumento, dependência, arquivo ilegível) |

E a aresta só existe se o **frontmatter** declarar. Uma relação escrita só na prosa não é
aresta — porque duas leituras de um parágrafo produzem dois grafos.

---

## 6. O gap: o que o material não disse

Este é o conceito que mais diferencia o Siegard de qualquer outra coisa.

Você está analisando um documento do cliente sobre pedidos. Ele diz o que é um pedido, diz
que tem número e total. **Não diz** quais são todos os campos. O que você faz?

**Errado** (o que qualquer um faria):

```yaml
attributes:
  - name: order_number
    type: string
  - name: total
    type: decimal
  - name: created_at      # ← ninguém disse isso. você achou razoável.
    type: datetime
```

Esse `created_at` agora é indistinguível de um campo que o cliente ditou. Daqui a um ano
ninguém sabe qual dos três o negócio decidiu.

**Certo** — e aqui há uma sutileza que eu mesmo errei ao montar o exemplo da seção 14:

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

Se você usar o nome nu no caso B, o validador recusa — e a mensagem ensina o conserto:

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

Um **gap** é uma declaração formal de ausência. Ele diz: *"este campo está faltando, e a
razão é esta"*. E — aqui está o truque — **o validador aceita um gap no lugar de qualquer
campo obrigatório**. O nó vale, e a falta está registrada.

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

Esse terceiro caso é sutil e importante. `rationale` cobre uma **leitura** do material
declarado — onde cai uma fronteira, que tipo de coisa é algo que foi dito. **Nunca** cobre
um valor sobre o qual o material é silencioso. Um valor plausível é um gap.

### Como ver os gaps abertos

```bash
python3 bin/graph.py --gaps knowledge/
```

Imprime `<identificador>: <campo>, <campo>` direto dos nós — nunca lendo o `graph.json`.
Essa é uma regra de projeto: relatórios pontuais se pedem ao script, contexto em massa se
lê do índice, e os dois derivam do mesmo pipeline, então não podem discordar.

### A regra de ouro dos gaps

> **Nunca feche um gap com um chute.** Um gap nomeia um fato que só quem conhece o domínio
> pode resolver, e um valor inventado se lê exatamente como um que o negócio ditou.

---

## 7. Os sete tipos de nó, com exemplos reais

Todos os exemplos abaixo saíram dos `examples` do próprio `schemas/node.json` — são formas
válidas por construção.

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
*Caminho: `aggregate/sales/orders.md`. Note o `rationale`: essa fronteira foi uma leitura
da analista, não algo que o material disse com essas palavras. Marcado, e portanto
contestável por um revisor.*

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
*`statement` é a regra em prosa normativa. `expression` é a mesma coisa checável.
`constrains` diz o que ela governa — e é uma aresta.*

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

**Aqui entra uma verificação bonita do motor: a totalidade.** Para cada par
(estado × gatilho), o nó tem de dizer *alguma coisa* — uma transição, uma rejeição, ou um
gap. Se `placed` × `place` não estivesse coberto, o validador recusa:

```
definition/sales/order: state `placed` has no transition, no rejection and no gap
for trigger `place`; an uncovered pairing is where behaviour gets invented later
```

Leia a última parte de novo: *"um par não coberto é onde comportamento é inventado
depois"*. É exatamente o que acontece na vida real — o desenvolvedor chega nesse caso, não
acha resposta, e decide sozinho.

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
*Um gap na vida real: sabe-se que consome algo de fora, não se sabe qual contrato.
Registrado, não inventado.*

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

Agora a segunda camada. Você vai construir algo. O plano tem três tipos de nó:

| tipo | o que é |
|---|---|
| `inventory` | o que **já existe** no código: módulos, convenções observadas, pontos de reuso, riscos |
| `epic` | uma fatia de escopo, que **declara quais nós da base ela responde** |
| `task` | uma unidade de trabalho: um objetivo, critérios, e a **vinculação** |

### O que é "vincular" (bind)

Uma task **vincula** os nós da base que a governam. É uma lista de identificadores:

```yaml
title: Record order
summary: Persist a placed order.
objective: A valid order is persisted and retrievable by its order_number.
criteria:
  - Submitting a valid order returns its order_number.
nodes:                                    # ← ESTA é a vinculação
  - definition/sales/order
base: sha256:2c6ed1ba…72ba                # ← e este é o pin (próxima seção)
```

A definição no contrato:

> *"The base nodes that govern this task, by identifier. **This is the binding**: the
> executor reads exactly these."*

Repare em "**exatamente estes**". Quem for implementar a task lê esses nós e mais nenhum.
Isso é o que faz a task ser autocontida: não é "leia a base e se vire", é "estes quatro
fatos governam este trabalho".

```
  BASE                                    PLANO
  ┌────────────────────────┐              ┌──────────────────────────┐
  │ definition/sales/order │◄─── binds ───│ task/checkout/           │
  │ rule/sales/total-pos.  │◄─── binds ───│   record-order           │
  │ lifecycle/sales/order  │              │                          │
  │ definition/sales/coupon│              │ (não vincula os outros   │
  └────────────────────────┘              │  dois — não governam)    │
                                          └──────────────────────────┘
```

### `objective` e `criteria`

```yaml
objective: A valid order is persisted and retrievable by its order_number.
criteria:
  - Submitting a valid order returns its order_number.
```

O contrato é exigente aqui:

- **`objective`**: *"The one falsifiable outcome this task delivers. Two outcomes are two
  tasks."*
- **`criteria`**: *"each falsifiable on its own. 'Works correctly' is prose; 'a rejected
  order returns the stated domain error' is a criterion."*

"Falsificável" quer dizer: dá para escrever um teste que **falharia** se aquilo parasse de
valer. "Funciona bem" não é critério porque nenhum teste pode falhar por causa disso.

### Nenhum status, nenhuma estimativa, nenhuma ordem

Uma task **não tem** campo de status, prioridade, estimativa ou ordem de execução. Esses
campos não existem no contrato. A ordem se deriva das dependências (`depends_on`), e o
estado da execução mora no git.

---

## 9. O pin

Agora o conceito que você perguntou. Vou construir do zero.

### O problema que ele resolve

A task acima vinculou `definition/sales/order`. Quem implementar vai ler esse nó e escrever
código conforme ele. Ótimo.

Mas… **quando** a task foi vinculada? A base mudou desde então? Se alguém acrescentou um
atributo obrigatório ao pedido depois que a task foi escrita, a task está desatualizada — e
nada no arquivo diria isso, porque o nome do nó (`definition/sales/order`) continua
idêntico.

### A solução: identidade por conteúdo

Um **pin** é o SHA-256 dos **bytes** de um arquivo:

```bash
$ sha256sum knowledge/graph.json
2c6ed1ba35d4fa96aa1845dcfdd12c15c8f55996297ffa4151be3c85422072ba
```

Escrito no nó como `sha256:2c6ed1ba…`. A definição no contrato:

> *"Content identity: the SHA-256 of the bytes of whatever artifact the field carrying it
> names. A pin records **which version** of that artifact a judgment read, so an artifact
> that moved afterwards is visible to the validator rather than assumed unchanged."*

### A divisão que é a chave

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │    O CAMINHO diz    ────►   QUAL coisa é                         │
  │                                                                  │
  │    O PIN diz        ────►   QUAL VERSÃO dela                     │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
```

`implementation/checkout/record-order.md` já diz, pelo caminho, a que task responde. O pin
diz contra qual **redação** daquela task o código foi escrito.

### Vendo funcionar

Montei a base de verdade e rodei o motor. Base com 3 nós, pin calculado, task escrita com
ele, plano validado:

```
$ sha256sum knowledge/graph.json  →  sha256:2c6ed1ba…72ba
$ grep base: task/checkout/record-order.md
  base: sha256:2c6ed1ba…72ba

$ python3 bin/plan.py work/ knowledge/
derived work/plan.json: 3 node(s), 2 edge(s), contract siegard-plan/1     ✔
```

Agora acrescentei à base um nó **totalmente sem relação** — `definition/sales/coupon`, um
cupom de desconto que a task não vincula. **Não toquei em nada do plano.** Rederivei a
base:

```
$ python3 bin/graph.py knowledge/
derived knowledge/graph.json: 4 node(s)

$ sha256sum knowledge/graph.json  →  sha256:cfeb6d09…e179     ← mudou!
```

E o mesmo plano, intocado, passou a ser recusado:

```
task/checkout/record-order: base pin sha256:2c6ed1ba…72ba is not the base as it
stands (sha256:cfeb6d09…e179); the binding read a base that has since moved —
re-bind the task, or restate the pin deliberately
```

### A lição de granularidade

O pin da base é **grosso**: cobre o `graph.json` inteiro. Qualquer mudança em qualquer nó
stalea **toda** task do plano, inclusive as que não vinculam o nó mexido.

Isso é escolha, não bug. É conservador de propósito: o motor prefere te obrigar a olhar de
novo do que deixar passar uma vinculação feita contra uma base que se moveu.

Do lado da entrega é **fino**. Um record de implementação pina o **arquivo da task**, não o
`plan.json`. Provei os dois lados:

```
# acrescentei uma SEGUNDA task ao plano. o plan.json mudou (3 → 4 nós).
# o record continuou válido:
derived delivery/delivery.json: 1 implementation; 1 of 2 task(s) hold a record   ✔

# depois mexi na PRÓPRIA task que o record responde — só na prosa do summary,
# de "Persist a placed order." para "Persist a placed order, exactly once."
# nem objetivo, nem critérios, nem vinculação. o record caiu na hora:
implementation/checkout/record-order: task pin sha256:185bf47c…4073 is not
task/checkout/record-order as it stands (sha256:2d8c4331…d19d); the record
answers a task that has since changed — deliver it again against the task as it
now stands, or restate the pin deliberately
```

**Por que a assimetria é deliberada:** se um record pinasse o `plan.json`, cada task nova
adicionada ao plano invalidaria todos os records existentes — e nenhuma skill tem
autoridade para re-pinar records que ela não pode ler. Pinar o arquivo da task dá o alcance
exato.

### Os quatro pins do motor

```
  ┌─────────────┐  base:  pina graph.json da base
  │ task        │ ──────────────────────────────────► knowledge/graph.json
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

### As duas saídas, sempre oferecidas

Toda mensagem de pin divergente oferece duas, e a escolha é de julgamento:

| saída | quando | o que fazer |
|---|---|---|
| **re-vincular / re-entregar** | a mudança afeta esta task | refaz a vinculação contra o que a base diz hoje |
| **reafirmar o pin deliberadamente** | a mudança não afeta esta task | escreve o hash novo à mão |

A palavra "deliberately" na mensagem está lá porque a diferença entre as duas é **você ter
olhado ou não**.

### Por que hash, e não data nem número de versão

| mecanismo | por que não |
|---|---|
| timestamp | diz *quando* alguém leu, não *o quê*. Dois arquivos diferentes têm a mesma data; o mesmo arquivo pode ser tocado sem mudar. |
| número de versão | exige que alguém incremente. A hora em que esquecem é a hora em que importava. |
| **hash** | não precisa de ninguém. Recomputável por qualquer um, num comando. **Não pode concordar com um arquivo que mudou.** |

É por isso que o contrato diz "computable by hand with `sha256sum`": um pin que só a
ferramenta soubesse verificar seria uma alegação, e o ponto dele é ser uma verificação.

---

## 10. As totalidades: nada passa em silêncio

O motor tem várias verificações do tipo "isto tem de estar completo". Elas são o coração da
coisa, porque **o modo normal de errar é o silêncio**: não escrever nada sobre algo.

### Totalidade 1 — cobertura do épico

Um épico declara `covers`: os nós da base pelos quais ele responde. Então, para cada nó em
`covers`, **uma das duas** tem de valer:

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

Recusa real (esta apareceu de verdade quando eu esqueci de criar a task no meu teste):

```
epic/checkout: covers names definition/sales/order, which no task under it binds
and uncovered does not declare; a covered node reaches a task or a stated why,
never neither — bind it in a task under this epic, or declare it in `uncovered`
with a why
```

E vale nos dois sentidos: uma task que vincula algo **fora** do `covers` do seu épico
também é recusada — porque vinculação fora da declaração é escopo que o plano não declarou.

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

```
task/x: waived[0] triages a gap on definition/sales/invoice, which `nodes` does
not bind; triage covers the nodes the task cites — bind definition/sales/invoice
if it governs this task, or drop the entry
```

A diferença entre os dois é enorme:

- **`unresolved`** = a task **não pode ser entregue**. O fato tem de ser produzido na base
  primeiro, via `/analyse-domain`, e a task re-vinculada. Se você escrever código por cima
  de um `unresolved`, o que você escrever se lê exatamente como uma decisão do negócio, no
  único lugar onde ninguém vai procurar por uma decisão.
- **`waived`** = julgamento registrado de que aquele gap não importa aqui. É uma alegação
  que um revisor pode **rejeitar** — e é por isso que exige um porquê.

### Totalidade 3 — o record responde a tudo

Um record de implementação tem de responder a **cada critério** da task e a **cada nó
vinculado**. Silêncio sobre qualquer um é recusado:

```
implementation/checkout/record-order: the task binds definition/sales/order, and
this record does not say how the source answers to it; a bound node passed over
in silence is the base going unanswered in code — answer it in `nodes`, or
re-bind the task through /plan-work if it does not govern this work
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

> *"uma implementação e seus testes escritos numa passada concordam por construção,
> **inclusive onde os dois estão errados**."*

Se o mesmo agente escreve o código e o teste, o teste testa o que o código faz — não o que
o critério pede. Separar os contextos é o que faz o teste ser uma verificação.

### Por que ninguém que julga também executa

`bin/run.py` roda os comandos do consumidor e grava o que imprimiram. Ele **não conta
testes** — parsear formato de reporter é conhecimento de stack, e o motor não tem nenhum.

E `/implement-task` **não roda nada**. A razão:

> quem escreve o código não pode testemunhar se passou, ou itera até ficar verde e o que
> falhou não existe em lugar nenhum.

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

> *"Um finding com o qual ninguém pode discordar é uma decisão vestida de finding. Quem
> decide é uma pessoa, lendo o que você escreveu."*

Não há severidade, nem nota, nem ranking, nem "isto bloqueia". Se a review calculasse
veredito, a revisora seria o portão — e foi exatamente disso que este desenho fugiu.

### O standard do projeto

O framework embarca o **contrato** de um standard (`schemas/standard.json`), o passe e as
verificações — e **nenhuma regra**. Porque as convenções de uma stack não são de um
domínio, e um framework que as embarcasse prescreveria TypeScript a um projeto em Go.

Cada regra do standard se marca com `decided_by`:

- **`reading`** — dizer se vale exige entender o que o código significa. É do passe de
  standard, e um finding cita a regra pelo id.
- **`tool`** — um linter ou compilador decide exato e barato. **Não é trabalho de modelo:**
  roda como passo da suite do projeto, e o que achar chega pelo passe de falhas.

> *"Um modelo aplicando uma regra que o linter tem tem recall estritamente pior que o
> linter, e custa mais."*

E um projeto que não escreveu standard nenhum recebe uma review **honestamente estreita** —
o passe registra que não rodou e o que faltava — **nunca uma review limpa**.

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

**Cada um para e devolve o controle.** Nenhum chama o próximo. O relatório termina com a
invocação seguinte pronta para colar e os espaços em branco — preencher e rodar é seu.

E cada um termina do mesmo jeito:

> *"Then stop. `git diff` sobre a raiz é a revisão, e ela pertence a uma pessoa."*

Existe um quinto comando, que não é ponto de entrada:

```bash
python3 bin/terms.py             # todos os termos, lidos do contrato que os define
python3 bin/terms.py pin         # só um
```

---

## 13. A parada é a funcionalidade

Isto costuma ser o que mais estranha em quem chega: o motor **recusa muito**. E recusar é o
produto, não a falha.

Existem 24 condições distintas de parada nas quatro skills. Todas antes de escrever
qualquer coisa:

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

> *"Absent inputs stop once, together: one stop naming everything missing, so the human
> answers once — never a question at a time."*

### Três paradas que só uma pessoa resolve

| parada | por que é sua |
|---|---|
| um **gap** | nomeia um fato que só quem conhece o domínio afirma, e um valor inventado se lê igual a um afirmado |
| **raiz suja** | é decisão de git — commitar, descartar, ignorar — e nenhuma das três é de uma skill |
| nota **`BLOCKING`** | é o escopo e a base se contradizendo, e as duas saídas passam por um ponto de entrada que alguém invoca |

Todo o resto é **forma**, e forma a própria invocação corrige. A regra que separa as duas:

> **"Fixing means form, never knowledge."** Um valor fora de vocabulário, uma lista onde
> cabia um mapa, um pin malformado — é seu para corrigir. Um fato ausente é um gap.

---

## 14. Exemplo completo de ponta a ponta

Vamos seguir um requisito do começo ao fim.

### O material

> *"Cliente monta um pedido com número e valor total. Não pode fechar pedido com total
> zerado ou negativo. Depois de fechado, não pode fechar de novo."*

### Passo 1 — `/analyse-domain` produz nós

```
knowledge/
├── context/sales.md
│      title: Sales
│      summary: Ordering.
│      strategic: core
│
├── aggregate/sales/orders.md
│      title: Orders
│      summary: An order and its lines change together or not at all.
│
├── definition/sales/order.md
│      title: Order
│      ddd: aggregate-root
│      aggregate: orders
│      identity: [order_number]
│      attributes:
│        - {name: order_number, type: string, max_length: 20}
│        - {name: total, type: decimal, precision: 12, scale: 2}
│      gaps:
│        - field: attributes.[]
│          why: The material names the number and the total, and no complete list.
│                            ↑ o material NÃO listou todos os campos.
│                              declarado, não inventado. E com caminho
│                              pontilhado, porque o campo ESTÁ declarado.
│
├── definition/sales/order-already-placed.md
│      title: Order already placed
│      summary: The refusal when a placed order is placed again.
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
│      expression: order.total > 0
│      constrains: [definition/sales/order]
│
├── lifecycle/sales/order.md
│      subject: definition/sales/order
│      states: [draft, placed]
│      initial: draft
│      transitions:
│        - {from: draft, trigger: place, to: placed}
│      rejections:
│        - {from: placed, trigger: place, error: definition/sales/order-already-placed}
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

$ sha256sum knowledge/graph.json
sha256:e4bb7378…7e9d14b7        ← este é o pin que as tasks vão carregar
```

### Interlúdio: os dois erros que eu cometi montando isto

Vale mais do que qualquer explicação. Montei a base acima e rodei o validador. Ele recusou
com **dois problemas — os dois exatamente os que a seção 16 documenta**:

```
definition/sales/order-already-placed: frontmatter: 'attributes' is a required property
definition/sales/order: gaps[0]: `attributes` is declared by the node; a gap names an
absent fact. An absence inside `attributes` takes a dotted path
```

O primeiro: eu escrevi o nó do erro de domínio sem `attributes`, e um `definition` exige o
campo. Não bastava omitir — a ausência tem de ser **declarada**, com um gap. O segundo: eu
declarei `attributes` com dois campos **e** gapei `attributes` com o nome nu. O validador
não deixa as duas coisas coexistirem, e a mensagem já traz o conserto (`attributes.[]`).

Nenhum dos dois erros é bobo, e nenhum dos dois teria sido pego por revisão humana com
confiabilidade. É isto que o motor compra: os erros de forma param na porta, e o que sobra
para uma pessoa revisar é **julgamento** — se o gap é legítimo, se a regra foi bem lida.

### Passo 2 — `/plan-work` produz o plano

```
work/
├── intake/requisito-original.md          ← o material, preservado como foi dado
├── inventory/order-service.md
├── epic/checkout.md
│      covers: [definition/sales/order, rule/sales/total-positive,
│               lifecycle/sales/order]
│
├── task/checkout/record-order.md
│      objective: A valid order is persisted and retrievable by its order_number.
│      criteria:
│        - Submitting a valid order returns its order_number.
│        - An order with total zero or less is refused.
│        - Placing an order already placed is refused with the stated error.
│      nodes: [definition/sales/order, rule/sales/total-positive,
│              lifecycle/sales/order]
│      base: sha256:e4bb7378…7e9d14b7
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
derived work/plan.json: 3 node(s), 6 edge(s), contract siegard-plan/1
  1 inventory, 1 epic, 1 task; 1 unresolved gap citation(s) (1 unique); 0 open question(s); 0 waived

$ python3 bin/plan.py --unresolved work/ knowledge/
task/checkout/record-order:
  gap definition/sales/order#attributes.[]
```

Note que o plano **valida** com um `unresolved` aberto. Um plano com pendência é um plano
legítimo — o que ele não é, é entregável. É a próxima etapa que para.

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

**E é aqui que o motor ganha o seu salário.** Sem ele, o desenvolvedor teria inventado os
campos que faltavam, e a invenção teria virado "o que o sistema faz" para sempre.

### Passo 4 — você pergunta ao cliente, e o ciclo fecha

O cliente responde: *"tem também data de criação e o cliente que pediu"*. Você roda
`/analyse-domain` de novo, o gap fecha com fatos **afirmados**, o pin da base muda, a task
é re-vinculada, o `unresolved` sai — e só então `/implement-task` escreve código.

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
     task: sha256:185bf47c…4073          ← pina a redação da task

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

Captura a execução, roda as quatro passes, grava findings com evidência. Uma pessoa lê e
decide o que significam.

---

## 15. Glossário

Consultável a qualquer momento com `python3 bin/terms.py`.

| termo | em português simples |
|---|---|
| **nó** (node) | um arquivo markdown com frontmatter. A unidade de tudo. |
| **raiz** (root) | um dos três diretórios: conhecimento, trabalho, entrega. |
| **base** | a raiz de conhecimento e seus nós. *(Cuidado: `base:` numa task é o pin, não a raiz.)* |
| **slug** | o nome do arquivo em kebab-case. |
| **gap** | uma ausência declarada: um fato que o material não disse. |
| **rationale** | marca um valor que a análise **decidiu** lendo o material, em vez de ler literalmente. Contestável. |
| **vincular** (bind) | uma task listar os nós da base que a governam. |
| **vinculado** (bound) | dito de um nó que uma task listou. |
| **pin** | o SHA-256 dos bytes de um arquivo: qual versão dele um julgamento leu. |
| **covers** | os nós da base pelos quais um épico responde. |
| **uncovered** | os nós que o épico reivindicou e este plano deixa de fora, cada um com porquê. |
| **unresolved** | o que a task precisa e a base não tem. **Bloqueia a entrega.** |
| **waived** | um gap que não afeta esta task, com o porquê. Um revisor pode rejeitar. |
| **criterion** | uma condição falsificável por si só. |
| **record** | um nó de entrega: o que foi feito ou achado. |
| **proof** | o nó que registra o que os testes provam — e o que não provam. |
| **standard** | as regras que o **projeto** definiu para si. O framework não embarca nenhuma. |
| **stale** | o índice derivado não corresponde mais aos nós. Rode o script de novo. |
| **intake** | onde o material lido fica preservado. Nunca validado como nó. |
| **closure** | um `closure.md` na raiz de trabalho marca o plano encerrado. Vira história. |

---

## 16. Erros comuns e o que significam

Todas as mensagens abaixo são reais. O formato é sempre:

```
<onde>: <o que está errado>; <por que importa — e o que fazer>
```

### "the path is the identity and this one computes to none"

Você pôs um arquivo num caminho que não vira identificador nenhum. Ex.: `notas.md` na raiz
de conhecimento. Material de leitura vai em `intake/` ou `run/`, que nunca são validados
como nós.

### "gaps[0]: `attributes` is declared by the node; a gap names an absent fact"

Você declarou o campo **e** disse que ele falta. Escolha um. Se parte do campo falta, o gap
usa caminho pontilhado: `attributes.customer`.

### "base pin … is not the base as it stands"

A base mudou depois da vinculação. Ou re-vincule a task, ou reafirme o pin de propósito.
Veja a [seção 9](#9-o-pin).

### "a covered node reaches a task or a stated why, never neither"

Um épico reivindicou um nó e nenhuma task dele o vincula, nem `uncovered` o declara. Ou
crie a task, ou declare em `uncovered` com o porquê.

### "a bound node passed over in silence is the base going unanswered in code"

O record não disse como o código responde a um nó que a task vinculou. Ou responda em
`nodes`, ou re-vincule a task se aquele nó não governa este trabalho.

### "an unnamed refusal is a gap, never an invented domain error"

O nó diz que algo é rejeitado e não nomeia o erro. Se o material não disse qual erro, isso
é um gap — não um código de erro inventado.

### "an uncovered pairing is where behaviour gets invented later"

Um par (estado × gatilho) do ciclo de vida sem transição, sem rejeição e sem gap. Diga
alguma coisa sobre ele, mesmo que seja "ninguém disse".

### "STALE: … is not what the nodes derive to"

O `.json` não corresponde aos markdown. Rode o script sem `--check` para reescrever. **Não
edite o json** — todo fato nele mora num arquivo de nó.

### "a finding citing no rule is taste with a location attached"

Um finding do passe de standard sem citar a regra pelo id. Sem regra citada, é opinião com
endereço.

---

## Em uma frase

> O Siegard força cada fato de domínio que o código codifica a apontar para um nó que o
> negócio decidiu; cada mudança a apontar para uma task; e cada task a apontar para a
> versão exata da base que leu — e recusa, em vez de adivinhar, sempre que um desses elos
> não fecha.

O resto do motor é a mecânica que torna essa frase verificável em vez de aspiracional.
