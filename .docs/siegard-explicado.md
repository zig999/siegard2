# Siegard explicado do zero

> **Sobre este manual.** Ele descreve o motor deste repositório a partir do zero, sem supor
> conhecimento prévio. Cobre a versão **3.5.0** — o redesign que fecha a especificação em cinco
> classes normativas (Domain Model, Rule, Scenario, Contract, Architecture Constraint), substitui
> gaps-como-ignorância por decide-and-disclose, e introduz o trace como o vínculo que sobrevive ao
> plano. Substitui a edição da versão 3.1.0, que descrevia o modelo anterior — sete tipos de nó,
> gaps abertos, binding por digest — inteiramente retirado deste repositório.
>
> **Sobre o idioma.** A seção Language de `/CLAUDE.md` exige que todo artefato do repositório seja
> em inglês (en-US), e nomeia `docs` entre eles. Este arquivo é a exceção deliberada, decidida pelo
> mantenedor com a regra sobre a mesa, e é o único artefato do repositório fora dela.
>
> **Sobre os exemplos.** Todo nó citado vem do fixture `tests/fixtures/spec-model/`, e toda saída
> de validador citada é real, capturada rodando `spec.py` sobre ele.

---

## Índice

1. [Que problema isso resolve](#1-que-problema-isso-resolve)
2. [A ideia central em uma página](#2-a-ideia-central-em-uma-página)
3. [O nó: a unidade de tudo](#3-o-nó-a-unidade-de-tudo)
4. [O caminho é a identidade](#4-o-caminho-é-a-identidade)
5. [Por que não há índice derivado](#5-por-que-não-há-índice-derivado)
6. [Decide-and-disclose: o log de decisões](#6-decide-and-disclose-o-log-de-decisões)
7. [As cinco classes, com exemplos reais](#7-as-cinco-classes-com-exemplos-reais)
8. [Do domínio ao plano: implementar contra](#8-do-domínio-ao-plano-implementar-contra)
9. [O trace: o vínculo que sobrevive ao plano](#9-o-trace-o-vínculo-que-sobrevive-ao-plano)
10. [As totalidades: nada passa em silêncio](#10-as-totalidades-nada-passa-em-silêncio)
11. [A entrega](#11-a-entrega)
12. [O standard: as regras que o projeto define para si](#12-o-standard-as-regras-que-o-projeto-define-para-si)
13. [Os quatro pontos de entrada](#13-os-quatro-pontos-de-entrada)
14. [A parada é a funcionalidade](#14-a-parada-é-a-funcionalidade)
15. [Exemplo completo de ponta a ponta](#15-exemplo-completo-de-ponta-a-ponta)
16. [Glossário](#16-glossário)
17. [Erros comuns e o que significam](#17-erros-comuns-e-o-que-significam)
18. [De onde isto veio](#18-de-onde-isto-veio)

---

## 1. Que problema isso resolve

### O que o Siegard faz

Um projeto de software carrega dois tipos de conhecimento: o que o negócio decidiu (um pedido
tem um total, um caso muda de estado ao ser investigado, uma cobrança é recusada sem uma
investigação concluída) e como o código está organizado (camadas, injeção de dependência, onde um
teste mora). O primeiro é domínio; o segundo é arquitetura. Historicamente os dois se misturam no
código-fonte, em comentários, e na cabeça de quem escreveu — e divergem silenciosamente do que o
negócio realmente decidiu, porque nada os mantém amarrados um ao outro.

O Siegard separa os dois numa **especificação** — arquivos markdown com frontmatter estruturado,
válidos ou não contra um contrato explícito — e mantém um **vínculo de conteúdo** entre essa
especificação e o código que a implementa. Quando os dois divergem, é possível saber: um nó da
especificação mudou depois que o código foi escrito, ou o código mudou sem que ninguém atualizasse
o vínculo. Nenhuma das duas coisas é descoberta por acidente meses depois.

O motor não decide nada sozinho. Toda decisão de negócio — o que uma entidade é, o que uma regra
exige, o que uma tarefa implementa — é de um agente ou de uma pessoa. O motor garante que a
decisão, uma vez tomada, fique registrada num lugar verificável, e recusa o que contradiz o que já
foi registrado.

## 2. A ideia central em uma página

Tudo que este motor valida é um **nó**: um arquivo markdown cujo *caminho* é sua identidade e cujo
frontmatter é validado contra um schema JSON. Não existe um campo `id`, `type` ou `class` dentro
do arquivo — o caminho já diz tudo isso, então nada no conteúdo pode discordar de onde o arquivo
está.

A especificação de um sistema tem exatamente **cinco classes** de nó, fechadas por design:

| classe | responde | verificada por |
|---|---|---|
| Domain Model | o que existe e como se estrutura | resolução de referência, alcançabilidade |
| Rule | o que sempre deve valer (universal) | uma condição falsificável |
| Scenario | o que acontece num caso concreto (exemplo) | executável como um teste de aceitação |
| Contract | o que é prometido através de uma fronteira | compatibilidade ao longo do tempo |
| Architecture Constraint | o que limita o espaço de solução | uma função de fitness sobre a implementação |

Um fato que o material não declara **é decidido agora, pela análise, e a decisão vai para um log
append-only** — nunca fica marcado como pendência dentro do nó. Essa é a reversão central deste
redesign: a versão anterior tratava um fato não declarado como um "gap" a ser preenchido depois,
por alguém que soubesse o domínio; esta versão trata a análise como quem decide, imediatamente,
disclosing a decisão para que um humano possa revisar e discordar depois — nunca como um bloqueio
antes da entrega.

Desenvolvimento é planejado (`/plan-work`), implementado (`/implement-task`) e revisado
(`/review-change`) contra essa especificação — sem nunca precisar reabri-la enquanto o plano está
vivo, porque a convenção é que a especificação não muda durante a execução de um plano. O único
vínculo que precisa sobreviver ao plano depois que o código está escrito é o **trace**: qual nó da
especificação um arquivo de código implementa, e com qual conteúdo cada lado tinha no momento do
vínculo.

## 3. O nó: a unidade de tudo

Um nó carrega frontmatter (a parte estruturada, o que um validador lê) e um corpo (a parte em
prosa, o que um leitor lê). Nenhum campo aparece nos dois — a mesma afirmação nunca vive em dois
lugares ao mesmo tempo.

O corpo tem um conjunto fechado de headings, que varia por classe:

```
## Description

Um contexto ou um elemento de Domain Model.

## Responsibility

Por que este conceito existe.
```

Uma Rule, uma Scenario, um Contract ou uma Architecture Constraint carregam só `## Description` —
não têm uma "responsabilidade" própria além do que já declaram estruturadamente. Um heading sem
nada a dizer carrega a linha literal `None.`, nunca é omitido: a ausência de conteúdo é ela mesma
uma informação (nada a acrescentar), diferente da ausência do heading (o arquivo está incompleto).

### As duas metades, e por que são separadas

O frontmatter é o que um validador pode segurar mecanicamente — um tipo fora do vocabulário
fechado, uma referência que não resolve, um campo obrigatório ausente. O corpo é prosa que
explica, nunca uma segunda casa para uma obrigação: uma frase que restringe o domínio e vive só no
corpo é uma frase que nenhum validador jamais vai poder segurar (SPEC-001 R7). Se você se pegar
escrevendo "o sistema deve..." dentro de `## Description`, isso é o sinal de que falta um campo,
uma Rule, ou uma Scenario — nunca uma desculpa para deixar a frase lá.

## 4. O caminho é a identidade

```text
<especificação>/
├── domain/<contexto>/_context.md          — o descritor do contexto
├── domain/<contexto>/<slug>.md            — um elemento de Domain Model
├── rules/<contexto>/<slug>.md             — uma Rule
├── scenarios/<contexto>/<slug>.md         — uma Scenario
├── contracts/system/<slug>.md             — uma capability (a promessa do sistema)
├── contracts/<contexto>/<slug>.md         — os demais Contracts
├── constraints/<slug>.md                  — uma Architecture Constraint
└── decision-log.md                        — o log, obrigatório, não-normativo
```

A identidade de um nó é seu caminho a partir da raiz da especificação, sem `.md` —
`domain/troubleshooting/case`, `rules/troubleshooting/case-transitions`. Não existe id, name ou
class dentro do arquivo: reclassificar um elemento (de `entity` para `aggregate-root`) muda uma
linha de frontmatter e não quebra referência nenhuma, porque nada referencia pelo tipo.

### Referência: nua ou completa, e por quê

Uma referência é um slug nu dentro do mesmo diretório, e a identidade completa em todo o resto
(SPEC-003 R2). Na prática: um atributo ou relacionamento de um elemento pode nomear outro elemento
nu quando ambos estão no mesmo contexto, porque os dois vivem sob `domain/<contexto>/`. Uma Rule,
uma Scenario ou um Contract nunca ficam dentro de `domain/` — então o que eles referenciam ali é
sempre a identidade completa, `domain/<contexto>/<slug>`, sem forma nua.

### O slug

Kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) do termo da linguagem ubíqua. O nome de exibição é
derivado, nunca guardado: `case-status` → `CaseStatus` (PascalCase). A única exceção é uma sigla
que a derivação erraria — `display: ISBNCode` — e mesmo essa precisa reduzir de volta ao slug.

## 5. Por que não há índice derivado

O modelo anterior mantinha um `graph.json` derivado — um índice barato de identificadores, títulos
e resumos, para não abrir cada arquivo em toda leitura. Esta especificação não tem título nem
resumo por nó: só `type`, os campos que a classe declara, e o corpo sob `## Description`. Um
índice desse formato não teria o que resumir.

`bin/spec.py` valida direto dos arquivos, toda vez — não há nada persistido entre execuções que
possa ficar desatualizado. O que existe em troca:

```
$ python3 -B bin/spec.py --digest specs/
specification sound: 10 element(s), 3 rule(s), 2 scenario(s), 4 contract(s), 1 constraint(s)
across 2 context(s); 2 decision(s) disclosed
constraints/asynchronous-events  sha256:4ee34debeb63243b8f0dc060d155eb539c429b1e2dd86a180b3282b66b5bc693
contracts/monitoring/alert-raised  sha256:51a98821777a193d03d0100de96eee74fc686e74c19c7414cd1e59f45c295573
...
```

Um manifesto de identidades — barato — sem nada sobre o que cada nó diz. Para localizar nós que um
material fala sobre, quem analisa faz *grep* pelo vocabulário do material na especificação inteira
em vez de ler um resumo pré-computado. Mais pesado que o índice antigo nos casos grandes, mais
honesto sobre o que este modelo realmente oferece.

`--project` deriva diagramas (nunca editados à mão); `--digest` computa a identidade de conteúdo
de cada nó, usada pelo trace (seção 9), nunca pela especificação em si.

## 6. Decide-and-disclose: o log de decisões

Um fato que o material não declara **é decidido pela análise, agora, e a decisão vai para
`decision-log.md`** — nunca fica marcado dentro do nó como um `gap`, um `unknown` ou um
placeholder. Um campo obrigatório deixado sem decisão não é uma ausência honesta: é uma violação
do piso (SPEC-001 R4), porque fechá-lo é exatamente o trabalho deste passo.

```yaml
# decision-log.md
entries:
  - location: domain/troubleshooting/evidence.md
    field: attributes.value.type
    unstated: The material does not say what shape an evidence value takes.
    decided: string
    why: Every evidence sample in the material is shown as free text.
  - location: rules/troubleshooting/case-transitions.md
    field: rejections
    unstated: The material never says what resolving an open case does.
    decided: The trigger is rejected in the open state.
    why: Resolution without an investigation contradicts the stated flow.
```

Cada entrada nomeia onde a decisão caiu (arquivo e campo, ambos resolvíveis — o validador recusa
uma entrada cujo local não existe), o que o material deixou por dizer, o que foi decidido, e por
quê. O log é **disclosure, nunca um portão**: a análise decide e segue adiante, e nenhuma entrada
bloqueia entrega nenhuma. Uma pessoa revisa o log depois, e discordar é uma mudança comum ao
artefato — nunca um protocolo de ratificação.

O validador segura a metade mecanicamente decidível: os campos obrigatórios do piso, a
alcançabilidade, a ausência de campos de proveniência (`gaps`, `sources`, `rationale`,
`proposal` — todos recusados por nome, sempre), e que toda entrada do log resolve para um arquivo
e campo reais:

```
$ python3 -B bin/spec.py specs/     # (com decision-log.md apagado)
decision-log.md is missing; the log is mandatory and non-normative (SPEC-003 R5)

1 problem(s) over 22 file(s); the specification is not sound while these stand.
```

O que fica com o julgamento de quem analisa — nunca do validador — é se um termo recorrente virou
mesmo um elemento, se uma classe condicional se justifica, e se um artefato responde a alguma
pergunta de compreensão real.

## 7. As cinco classes, com exemplos reais

### Domain Model — o que existe e como se estrutura

Cinco subtipos: `aggregate-root`, `entity`, `value-object`, `domain-service`, `enumeration`.

```yaml
# domain/troubleshooting/case.md
---
type: aggregate-root
attributes:
  - name: id
    type: case-id
    required: true
  - name: status
    type: case-status
    required: true
  - name: opened_at
    type: datetime
    required: true
  - name: resolved_at
    type: datetime
relationships:
  - target: investigation
    type: composition
    cardinality: "1"
  - target: resolution
    type: composition
    cardinality: "0..1"
operations:
  - open
  - start-investigation
  - resolve
  - cancel
---

## Description

A customer problem submitted to the troubleshooting process.

## Responsibility

Control the investigation from opening to resolution or cancellation.
```

Um link para um primitivo, um value object ou uma enumeration é um **atributo**; um link para uma
entity ou um aggregate root é um **relacionamento** — nunca os dois para o mesmo fato (SPEC-002
R8). `composition` nunca cruza um agregado; `reference` é como um elemento aponta para outro
agregado, sempre por identidade.

Cada contexto carrega seu descritor, fora do espaço de slugs dos elementos pelo underscore:

```yaml
# domain/troubleshooting/_context.md
---
strategic: core
---

## Description

Diagnosing customer problems from submission to resolution.

## Responsibility

Own the language of cases, investigations and evidence.
```

### Rule — o que sempre deve valer

Três subtipos: `invariant` (dentro de um agregado, vale imediatamente), `policy` (pode cruzar
agregado ou contexto, e então `consistency: eventual` é obrigatório — exigir `immediate` através
de uma fronteira é a fronteira redesenhada, não uma regra), `state-machine`:

```yaml
# rules/troubleshooting/case-transitions.md
---
type: state-machine
statement: A case moves only along the declared transitions.
subject: domain/troubleshooting/case
status: domain/troubleshooting/case-status
initial: open
terminal: [resolved, cancelled]
transitions:
  - {from: open, trigger: start-investigation, to: investigating}
  - {from: investigating, trigger: resolve, to: resolved}
  - {from: open, trigger: cancel, to: cancelled}
  - {from: investigating, trigger: cancel, to: cancelled}
rejections:
  - {from: open, trigger: resolve}
  - {from: investigating, trigger: start-investigation}
---

## Description

The lifecycle of a case, total over its states and triggers.
```

O validador checa a totalidade: todo par (estado não-terminal, gatilho mencionado) precisa ser uma
transição ou uma rejeição — nunca deixado em silêncio. O diagrama de estado deriva direto disso:

```
$ python3 -B bin/spec.py --project specs/
$ cat specs/projections/state-troubleshooting-case.mmd
stateDiagram-v2
    [*] --> open
    open --> investigating : startInvestigation
    investigating --> resolved : resolve
    open --> cancelled : cancel
    investigating --> cancelled : cancel
    resolved --> [*]
    cancelled --> [*]
    %% rejected: resolve in open
    %% rejected: startInvestigation in investigating
```

### Scenario — um caso concreto

Sem subtipos — o sujeito já distingue um exemplo de invariante de um caso de aceitação ponta a
ponta. Âncora em exatamente um elemento de Domain Model, uma Rule ou um Contract:

```yaml
# scenarios/troubleshooting/refuse-resolution-without-evidence.md
---
subject: rules/troubleshooting/hypothesis-requires-evidence
given:
  - a case under investigation holds one hypothesis with no evidence
when:
  - the operator resolves the case
then:
  - the resolution is refused
  - the case stays investigating
---

## Description

The invariant refusing an unsupported resolution.
```

### Contract — o que atravessa uma fronteira

Quatro subtipos: `domain-event` (nomeado no passado), `command` (pode ser recusado — `refusal`
nomeia o value object que a recusa devolve), `api`, `capability` (a promessa do próprio sistema,
só existe sob `contracts/system/`). `direction` (`published` | `consumed`) é obrigatório nos três
primeiros; um contrato consumido nomeia o publicado do qual depende:

```yaml
# contracts/troubleshooting/alert-raised.md
---
type: domain-event
direction: consumed
upstream: contracts/monitoring/alert-raised
payload: domain/monitoring/alert
---

## Description

Troubleshooting depends on monitoring's published alert event.
```

Um sistema de terceiros é um contrato upstream nomeado pela capability que ele fornece — nunca o
nome do fornecedor, que é conhecimento de implementação e não entra na especificação.

### Architecture Constraint — o que limita a solução

Sem subtipos. Uma estratégia de integração, uma escolha de armazenamento, um anti-corruption
layer: `scope` (`system` ou um contexto) e, onde existe, `fitness` — a checagem mecânica que
verifica.

## 8. Do domínio ao plano: implementar contra

Uma tarefa de desenvolvimento nomeia os nós da especificação que implementa, por identidade — sem
nenhum pin:

```yaml
# task/checkout/record-order.md (frontmatter)
implements:
  - domain/sales/order
  - rules/sales/order-total-positive
```

Nada aqui compara um valor computado contra um valor guardado. A garantia é procedimental: **a
especificação não muda enquanto um plano está vivo**, por convenção, não por um digest que o
validador confere a cada execução. Isso substitui inteiramente o mecanismo anterior — cada nó
vinculado carregando o digest que a vinculação leu, e o plano recusado quando o nó se movia. Uma
tarefa hoje não carrega mais nada disso: nem um campo `nodes`, nem um `digest`, nem `unresolved`,
nem `waived`.

Quem decide o que uma tarefa implementa é um agente isolado (`execution-contract-binder`), num
contexto que nunca viu como a tarefa foi cortada — a especificação é lida pelo que ela diz hoje,
nunca para caber na tarefa. Ele ainda classifica cada divergência entre a tarefa e a especificação
em quatro classes, exatamente como antes:

- **`blocking`** — nenhum construto que a especificação admite demonstra o objetivo ou um
  critério como escrito, **incluindo um fato que a especificação simplesmente não declara**. É a
  única classe que impede a tarefa de ser escrita.
- **`underdetermined`** — existe uma implementação que satisfaz todo critério como escrito e que a
  especificação recusa; o binder a nomeia.
- **`remainder`** — uma cláusula de uma Rule vinculada não alcança nenhum critério desta tarefa
  porque pertence a outra tarefa ou a outro ato.
- **`advisory`** — o resto: uma costura, um vizinho não implementado, uma condição.

Uma nota `blocking` que vem do próprio escopo é o único caso que só uma pessoa resolve — através
do escopo, ou através da análise que estende a especificação. Não existe mais uma "pergunta que a
base não responde" como um retorno separado: isso agora é exatamente um caso de `blocking`.

## 9. O trace: o vínculo que sobrevive ao plano

Planejamento e entrega são descartáveis por design. Um plano e sua raiz de entrega existem para
fazer código ser escrito; uma vez que uma tarefa valida, nada exige que nenhum dos dois
sobreviva — um plano fechado pode ser apagado junto com sua entrega, e nenhuma outra raiz depende
dele continuar ali.

O que precisa sobreviver é o vínculo entre um nó da especificação e o arquivo que o implementa.
`siegard-trace.json`, ao lado de `siegard.json` no toplevel git da raiz de código-alvo, é esse
vínculo:

```json
{
  "specification": "specs",
  "bindings": [
    {
      "node": "domain/sales/order",
      "digest": "sha256:9e85d9145db8f5f67feee52781d20091759321ef039946f126559aa29d5e93ad",
      "files": [
        {"path": "backend/src/orders/place.ts",
         "digest": "sha256:f72cfadc058508a0eee4c51b041c39cc3150616fc1219afe14eb0955e4eb47c4"}
      ]
    }
  ]
}
```

`bin/trace.py` é o único escritor — `/implement-task` chama `--bind` uma vez que uma entrega
valida, para cada nó que o registro de implementação nomeia com `encoded_at` — e o único leitor:

```
$ python3 -B bin/trace.py --check backend/
no drift: 1 binding(s) match the specification and the code as both stand now
```

`--check` recomputa os dois digests a partir do que está em disco agora e reporta o que
divergiu — um nó que se moveu na especificação desde o vínculo, ou um arquivo que se moveu no
código sem um novo vínculo:

```
$ python3 -B bin/trace.py --check backend/
domain/sales/order: bound at sha256:9e85..., now sha256:e233...; the specification moved since
this bind
```

Isso é o que permite que uma invocação futura de `/plan-work` ou `/analyse`, sem abrir nenhum
histórico de plano, pergunte se código e especificação ainda concordam.

## 10. As totalidades: nada passa em silêncio

Um resumo por totalidade que o validador segura:

| totalidade | onde | o que ela impede |
|---|---|---|
| toda referência resolve | `spec.py` | um slug apontando para o vazio |
| todo value object e enumeration é alcançável | `spec.py` | um elemento que nenhuma pergunta de compreensão alcança |
| toda entrada do decision-log resolve | `spec.py` | uma decisão apontando para um arquivo ou campo que não existe |
| todo par (estado, gatilho) é decidido | `spec.py` | uma transição silenciosamente esquecida |
| todo nó coberto por um epic é implementado ou declarado `uncovered` | `plan.py` | um pedaço da especificação que o plano ignorou sem dizer |
| todo critério é respondido, e só uma vez | `deliver.py` | uma entrega que responde só o que é fácil |
| todo nó que a tarefa implementa é respondido | `deliver.py` | uma implementação que ignora parte do que assumiu governar |

## 11. A entrega

Três tipos de nó sob uma raiz de entrega — `implementation`, `proof`, `review` — mesmo esquema de
antes. O que muda: um registro responde por todo nó que a tarefa implementa (não mais "todo nó
vinculado"), e não existe mais `unresolved` — se algo faltava, a tarefa nunca teria sido escrita
com uma nota `BLOCKING` ainda de pé.

Depois que a entrega valida, `/implement-task` faz o bind (seção 9) — o único passo que toca um
arquivo fora das três raízes (entrega, trabalho, código-alvo): `siegard-trace.json`, no toplevel
do código.

## 12. O standard: as regras que o projeto define para si

Inalterado mecanicamente. `siegard.json` declara o registro uma vez; `schemas/standard.json` é o
contrato; `bin/deliver.py --standard <arquivo>` valida. Duas linhas seguem limitando o escopo:
nenhuma regra diz o que o sistema responde (isso é da especificação), e uma regra que uma
ferramenta decide não é de uma leitura reler.

## 13. Os quatro pontos de entrada

- **`/analyse`** — transforma material em nós da especificação, valida, deriva projeções, e para.
- **`/plan-work`** — transforma um escopo mais a especificação validada num plano de
  desenvolvimento.
- **`/implement-task`** — escreve o código de uma tarefa planejada e os testes que o provam,
  instala e roda o que o standard declara, faz o bind no trace, e para.
- **`/review-change`** — revisa uma mudança entregue por quatro ângulos independentes — cobertura,
  conformidade com a especificação, conformidade com o standard, e por que uma suíte falhou —
  produz evidência, nunca um veredito.

## 14. A parada é a funcionalidade

Uma parada é este framework funcionando, não falhando. Toda entrada recusa antes de escrever, em
vez de escrever o que um revisor teria de pegar depois. Só duas coisas exigem mesmo uma pessoa:
uma mudança não commitada (decisão de git) e uma nota `BLOCKING` (o escopo e a especificação se
contradizendo). O resto é forma, e forma é da própria invocação corrigir.

## 15. Exemplo completo de ponta a ponta

O fixture `tests/fixtures/spec-model/` é uma especificação sã inteira — dois contextos
(`monitoring`, `troubleshooting`), 10 elementos, 3 rules, 2 scenarios, 4 contracts, 1 constraint,
2 decisões disclosed. Rodando a validação completa:

```
$ python3 -B bin/spec.py tests/fixtures/spec-model/
specification sound: 10 element(s), 3 rule(s), 2 scenario(s), 4 contract(s), 1 constraint(s)
across 2 context(s); 2 decision(s) disclosed
```

O mapa de contexto que deriva disso mostra exatamente uma aresta — o único par de contextos com um
contrato entre si:

```
$ cat tests/fixtures/spec-model/projections/context-map.mmd
flowchart LR
    monitoring["Monitoring (supporting)"]
    troubleshooting["Troubleshooting (core)"]
    monitoring -->|alert-raised| troubleshooting
```

Um contrato removido vira "separate ways" no mapa, não uma aresta que desaparece em silêncio —
`test_every_projected_fact_traces_to_a_file` em `tests/test_spec_model.py` prova exatamente isso.

## 16. Glossário

Não reproduzido aqui: `bin/terms.py` imprime cada termo direto do contrato que o define, e
reproduzir o texto aqui seria a segunda cópia que ele existe para evitar.

```
$ python3 -B bin/terms.py implements
implements  [plan-node.json/properties/implements/description]
    The specification nodes this task implements, by identity: the executor reads exactly
    these, current, from the specification itself — the specification does not change during
    a plan's execution, by convention, so there is nothing to pin. ...
```

## 17. Erros comuns e o que significam

| Mensagem | O que aconteceu |
|---|---|
| `the path computes to no identity; see the layout in SPEC-003` | Um arquivo `.md` sob a raiz não bate com nenhum dos seis formatos de caminho — provavelmente uma pasta a mais, ou um arquivo fora de `domain/`, `rules/`, `scenarios/`, `contracts/`, `constraints/` ou a raiz. |
| `carries a provenance meta-field` | O arquivo tem `gaps`, `sources`, `rationale` ou `proposal` — nenhum existe mais neste modelo; a decisão vai para `decision-log.md`. |
| `answering no comprehension question does not exist` | Um value object ou enumeration que nada referencia. Um aggregate-root e um domain-service se justificam sozinhos; os outros três precisam de alguém que os alcance. |
| `an invariant constrains inside one aggregate` | Uma invariant cujo `constrains` atravessa um agregado — precisa virar uma policy com `consistency`. |
| `a boundary redrawn, not a rule` | Uma policy pedindo `consistency: immediate` através de uma fronteira — a fronteira é que está errada, não a regra. |
| `an undecided pairing is a decision to make and log, never silence` | Uma state-machine com um par (estado, gatilho) sem transição nem rejeição. |
| `the specification moved since this bind` | `trace.py --check` achou um nó cujo digest hoje difere do que o trace registrou. |

## 18. De onde isto veio

Este redesign substitui o modelo em sete tipos de nó (`context`, `aggregate`, `definition`,
`rule`, `lifecycle`, `interface`, `process`), a disciplina de gaps (um fato ausente marcado como
pendência, com rodadas de ratificação para fechá-lo), e o binding por digest (uma tarefa fixando a
versão exata de cada nó que lia). Os três existiam por uma razão real — nenhum deles foi trocado
por capricho — mas o redesign encontrou uma forma menor de entregar a mesma garantia: cinco
classes fecham o vocabulário do domínio sem precisar de sete; decidir e revelar entrega a mesma
honestidade que gaps entregava, sem o protocolo de ratificação por cima; e o trace entrega uma
garantia de sincronia mais forte que o binding por digest — sobrevivendo ao próprio plano, em vez
de expirar com ele.

Não existe migração automática. Uma especificação no modelo antigo é material para uma nova
invocação de `/analyse` — o material é lido de novo, e a nova especificação é escrita do zero
contra o formato atual.
