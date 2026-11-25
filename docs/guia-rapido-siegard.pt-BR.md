# Guia rápido do Siegard (for dummies)

> Este guia **explica**, não **governa**. Se ele discordar de uma especificação, de um schema ou do
> `SKILL.md` de uma skill, quem vale é a fonte. Os nomes de skills, flags, campos e arquivos ficam
> sempre em inglês, escritos exatamente como o Siegard escreve.
>
> Escrito para a versão 5.124.1 do plugin (a que consta em `plugin.json`), em 2026-11-17. Em caso
> de divergência, o `SKILL.md` de cada skill governa.
>
> **Para ir além:** o glossário em pt-BR (`docs/siegard-glossary.pt-BR.md`, capítulos em
> `docs/siegard-glossary.pt-BR/`) explica o vocabulário inteiro. O `README.md` resume um caso
> (a correção feita à mão durante um incidente), e o capítulo 15 do glossário o percorre passo a
> passo.

---

## 0. Pré-requisitos

- **Claude Code** com o plugin do Siegard instalado.
- **`python3` com PyYAML e jsonschema** (os scripts do framework precisam deles).
- O projeto num **repositório git**: sem git não há revisão (o `git diff` é a revisão de tudo), e
  as skills param.
- Um **`siegard.json`** na raiz git do projeto (o toplevel do repositório): é ele que "liga" o
  Siegard. As regras do framework só entram nas sessões, e nos agentes, de um repositório cujo
  toplevel tem esse arquivo (o cenário 0 cria o arquivo).
- O Siegard **não constrói aplicação própria**: quem constrói e testa é o seu projeto, pelos
  steps que o seu registry (o standard) declara.

---

## 1. O que é o Siegard, em um minuto

Imagine que o seu projeto tem uma **caderneta de decisões**: "um pedido só pode ter uma fatura",
"cupom expira em 30 dias". O Siegard faz o código **responder a essa caderneta**.

- A caderneta é a **specification**: arquivos markdown, chamados de **nós**, que um script valida.
- O trabalho é **planejado** contra a caderneta (`/plan-work`), **entregue** com código e testes
  (`/implement-task`) e **revisado** por alguém que não escreveu o código (`/review-change`).
- Um arquivo chamado **trace** (`siegard-trace.json`) anota qual arquivo de código guarda qual
  decisão. Se alguém mexer no código por fora, o trace percebe (isso se chama **drift**).

```
/analyse ──► SPECIFICATION ──► /plan-work ──► /implement-task ──► CÓDIGO + TESTES
                  ▲                                                     │
                  └────────── /review-change · /reconcile ◄── trace ◄───┘
```

**Como chamar uma skill:** o nome canônico vem com o prefixo do plugin: `/siegard:plan-work`,
`/siegard:deliver-scope` e assim por diante. A forma curta (`/plan-work`) funciona enquanto nenhum
outro plugin usar o mesmo nome. Neste guia escrevo a forma curta, para ficar curto.

---

## 2. Vocabulário mínimo (só o que você precisa)

| Palavra | Quer dizer |
|---|---|
| **project root** | A pasta onde mora o `siegard.json`. Se você não disser, o Siegard usa a raiz do git da pasta onde você abriu a sessão (desde que tenha `siegard.json`). |
| **target** | Uma base de código declarada no `siegard.json` (ex.: `backend`, `web`). Se o projeto só tem um, o Siegard usa esse e avisa. |
| **slug** | O nome de uma iniciativa (ex.: `cupom-desconto`). Cada slug tem um plano e uma pasta de entregas. |
| **plan / epic / task** | O plano é cortado em épicos, e cada épico em tarefas (`task/<epic>/<name>`). |
| **stop** | A skill parou porque falta algo que só uma pessoa decide. Ela diz o porquê. |
| **refusal** | Um script recusou algo e disse exatamente o quê. Nunca se contorna. |
| **door** (porta) | Uma "próxima invocação" já preenchida que o relatório te entrega para você colar. |
| **state A / state B** | Fim de um `goal`. A = tudo entregue, provado, revisado, medido e commitado. B = a execução parou num ponto que só uma pessoa resolve (uma linha de stop no log, um commit de fora da rota, um commit que tocou o `siegard.json` ou o standard, a versão do plugin mudou desde que o goal começou, ou um critério registrado como não atendido). |
| **drift** | Um arquivo mudou sem passar pelo fluxo, e o trace discorda. |

**Três regras de ouro para um operador novo:**

1. **O Siegard não chuta entradas.** Faltou uma entrada obrigatória? Ele para **uma vez**, listando
   tudo o que falta, e você responde de uma vez. Já um **fato** que a specification não diz é
   **decidido** no planejamento e registrado no decision log do nó, para você revisar depois.
2. **Tudo é recalculado do disco.** Pergunte "como estamos?" a `/siegard-status`, nunca à memória
   da conversa.
3. **Skill "fechada ao modelo" só você digita.** `/siegard-goal`, `/siegard-grant`, `/siegard-config`,
   `/siegard-standard`, `/siegard-archive` e `/clarify-request` não podem ser disparadas pelo Claude
   por conta própria: os argumentos são as **suas** palavras. No `/siegard-goal` e no
   `/siegard-grant`, essas palavras são a própria autorização.

---

## 3. Mapa das skills

| Fase | Skill | Em uma frase |
|---|---|---|
| Preparar | `/siegard-config` | Cria/atualiza o `siegard.json` |
| Preparar | `/siegard-standard` | Escreve o "standard" (regras do próprio projeto) |
| Especificar | `/analyse` | Transforma material em nós da specification |
| Planejar | `/plan-work` | Corta um escopo em épicos e tarefas |
| Entregar | `/implement-task` | Escreve código + testes de **uma** tarefa |
| Revisar | `/review-change` | Julga o que foi entregue (nunca "aprova") |
| Ponta a ponta | `/deliver-scope` | Planeja + entrega + revisa um escopo inteiro |
| Autônomo | `/siegard-goal` | Roda o escopo todo sem perguntar nada, até acabar |
| Autônomo | `/siegard-grant` | Autoriza o Siegard a tomar as decisões dos stops |
| Código por fora | `/reconcile` | Alinha código mudado "na mão" com a specification |
| Código por fora | `/check-source` | Lê arquivos mudados sem tarefa contra o standard |
| Código antigo | `/survey` | Lê código existente e escreve o "material" |
| Código antigo | `/adopt-scope` | survey → analyse → reconcile, de ponta a ponta |
| Acompanhar | `/siegard-status` | Onde o projeto está, agora |
| Acompanhar | `/siegard-progress` | Tabela de tarefas de **uma** iniciativa |
| Acompanhar | `/siegard-telemetry` | Relatório de custo e fricção de uma janela de tempo |
| Limpar | `/siegard-archive` | Remove iniciativas fechadas da árvore (a história fica no git) |
| Ajudar | `/clarify-request` | Reescreve seu pedido vago como uma instrução precisa |

---

## 4. Cada skill, em detalhe

> Convenção das tabelas de parâmetros: **obrigatório** = sem isso a skill para; **opcional** = há
> um padrão. Onde o `project root` ou o `target` têm padrão, ele é "decidido e avisado no relatório".

### 4.1 `/siegard-config` — "declarar o projeto" (fechada ao modelo)

**Para que serve:** escreve o `siegard.json`, o arquivo onde o projeto diz onde ficam as coisas. É
o primeiro passo de qualquer projeto. Só mexe nos campos que você nomeia.

**Parâmetros (em prosa, você diz o que quer declarar):**

| O que declarar | Para quê |
|---|---|
| `specification_root` | Pasta dos nós da specification |
| `targets` (nome em kebab-case + caminho relativo ao `siegard.json`, quantos quiser) | Bases de código. A pasta pode ainda não existir |
| `work_root` | Onde ficam os planos (um subdiretório por slug) |
| `delivery_root` | Onde ficam os registros de entrega e revisão |
| `standard` (por target: caminho ou `null`) | Qual registry de regras vale para cada target |
| `telemetry_root` | Onde o `/siegard-telemetry` grava relatórios |
| `edits_freely` (lista de targets) | Targets cujo código você edita sem tarefa |
| `tests` (por target, uma lista de escopos: `under` e `suffix` obrigatórios, `nested` opcional, falso se ausente; nunca glob) | Onde moram os testes |
| status line (ligar/desligar) | Mostra a linha de progresso no rodapé do Claude Code. Fica em `.claude/settings.local.json` (não se commita: o caminho é desta máquina). Aparece na próxima sessão. Depois de atualizar o plugin, rode de novo |

**Combinações e pegadinhas:**
- **Nunca edite o `siegard.json` à mão**: só o `/siegard-config` o escreve. Ele não remove campo:
  para tirar um, peça uma declaração nova do arquivo inteiro.
- Precisa de **pelo menos um campo** (ou só a status line, que exige `siegard.json` já existente).
- Para **criar** o arquivo você precisa **nomear a raiz**; não vale a raiz "inferida".
- `standard` com dois ou mais targets só vale como objeto por target. Um caminho solto só serve em
  projeto de um target.
- `edits_freely` **substitui** a lista inteira (não soma). Ele faz o `trace.py --check` contar o
  drift em vez de listar arquivo por arquivo: use sabendo disso.
- `git status` de `siegard.json` precisa estar limpo antes (o diff é a sua revisão).
- Quando qualquer outra skill diz "campo ausente", ela te entrega **a invocação do
  `/siegard-config` pronta para colar**.

**Exemplo** (a forma multilinha é a que o próprio framework entrega pronta):
```
/siegard:siegard-config
  Project root: .
  specification_root: specs
  targets: backend = services/api
  work_root: plans
  delivery_root: deliveries
  telemetry_root: telemetry
```

---

### 4.2 `/siegard-standard` — "as regras da casa" (fechada ao modelo)

**Para que serve:** transcreve para um registry (o **standard**) as convenções que o projeto **já
pratica**: o que o linter, o compilador e o scanner de segredos já decidem, mais o que você disser
em palavras. Ele **nunca inventa** uma regra que ninguém configurou nem declarou.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| project root | padrão: raiz git | |
| target | **obrigatório** | Um standard governa **um** target; dois stacks = dois registries |
| caminho do standard | **obrigatório** | Ausente: cria; presente: estende. Sempre dentro da árvore do projeto |
| convenções em suas palavras | opcional | Inline ou um documento (lido inteiro). Sem isso, só entra o que as ferramentas já provam |

**Antes:** o `siegard.json` precisa existir, declarar o target e estar **commitado**. A árvore
inteira do projeto precisa estar limpa fora do arquivo do standard (qualquer pendência = stop).

Depois, registre o caminho no `siegard.json` (`/siegard-config` → `standard`). Ele não commita: o
`git diff` do standard é a sua revisão.

---

### 4.3 `/analyse` — "do papo para a specification"

**Para que serve:** pega **material** (descrição de problema, ata de reunião, ticket, documento) e
escreve **nós** da specification: Domain Model, Rule, Scenario, Contract, Architecture Constraint.
Valida tudo. Fato que o material não dizia e era preciso decidir é **decidido e registrado** no
decision log do nó (você revisa depois no `git diff`).

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| material | **obrigatório** | Prosa e/ou caminho de arquivo. Tem que afirmar **fatos** do domínio |
| project root | padrão: raiz git | |

**Pontos importantes:**
- O `siegard.json` precisa declarar `specification_root`, e a raiz da specification precisa
  começar **limpa** no git.
- Material que não afirma fato nenhum ("quero uma tela melhor") é tratado como **ausente** e
  gera `stop: no-fact`. Sobre uma specification já povoada, material que cita nós mas não diz o
  que muda gera `stop: no-change`.
- O material é **dado**, não ordem: instruções escondidas nele são ignoradas.
- Uma invocação = um incremento. A primeira preenche a raiz vazia; as seguintes **evoluem** o que
  já existe, na mesma ordem.
- **Ele mesmo commita** a raiz da specification (e o ledger, ou a remoção dele), com a mensagem
  `analyse <nome>: analyse` (o nome é o slug, se a invocação citar um, ou o nome do arquivo de
  material; sob um goal, o passo se chama `specify`). Você revisa **depois**, no `git diff` do
  commit; discordar de um nó é só uma nova mudança comum.
- **Cuidado com plano vivo:** se o `/analyse` mudar um nó que uma tarefa de um plano **vivo**
  implementa, o `plan.py --check` passa a acusar `MOVED`, e `/implement-task` e `/review-change`
  param nesse slug até você rodar `/plan-work` de novo sobre ele.

**Exemplo:**
```
/analyse . Um cupom dá desconto percentual de 1 a 50%. Cupom expira 30 dias após a criação.
Um pedido aceita no máximo um cupom. Cupom expirado é recusado com a mensagem "cupom expirado".
```

---

### 4.4 `/plan-work` — "o plano"

**Para que serve:** corta um escopo em **épicos e tarefas**; cada tarefa diz quais nós implementa.
Um agente separado (o **binder**) decide os nós de cada tarefa. O resultado é validado e vira
`plan.json`. Fato que a specification não diz é decidido às cegas (sem ver o corte de tarefas) e
registrado no decision log: isso **não** vira pergunta para você.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| escopo em prosa (+ arquivos que ele cita) | **obrigatório** | O que desenvolver |
| project root | padrão: raiz git | |
| target | padrão se houver 1 só | Chave do `targets` |
| slug | **obrigatório** | Vazio = primeira rodada; populado = evolui o plano. Slug com `closure.md` = plano fechado: stop |

**Os modos** (você **nomeia** o modo; ele nunca é inferido):

| Modo | Quando usar | O que precisa além do básico |
|---|---|---|
| *(ordinário)* | Feature nova ou incremento | — |
| **Corrective increment** | **Um** comportamento errado em código já entregue, que nenhum critério de tarefa cobre | O comportamento errado **e o arquivo** onde ele mora (a reprodução, se você der, vai junto). O arquivo precisa estar no trace (ligado por alguma entrega); se não estiver, é stop. Se o conserto é mais de uma tarefa, é um escopo: use o modo ordinário |
| **Decided-fact increment** | Um `/implement-task` parou por silêncio da specification e você quer que o fato seja decidido | O fato como o stop citou e a task daquela entrega |
| **Proof increment** | Fatos que um teste decide, hoje só "decididos por leitura" | Por fato: o nó, a asserção literal, o registro (`siegard-reconcile/...`) e os arquivos. `trace.py --owed` lista isso |
| **Closing** | Declarar a iniciativa encerrada | O pedido com o motivo, o root e o slug. Escreve `closure.md` |

**Exemplos:**
```
/plan-work . target backend slug cupom — Permitir cupom de desconto no checkout (criar, validar, aplicar)
/plan-work . target backend slug cupom — corrective: o cupom expirado ainda é aceito; arquivo src/coupon/apply.ts
/plan-work . slug cupom — closing: iniciativa concluída, tudo entregue e revisado
```

**Dica:** o relatório termina entregando as *doors* já preenchidas para a próxima etapa.

**Commit:** ao final ele commita as raízes que rodou, em um commit só (`plan-work <slug>: <modo>`),
e para se alguma raiz já tinha mudança que não era dele. Ver a seção 6.

---

### 4.5 `/implement-task` — "escrever uma tarefa"

**Para que serve:** entrega **uma** tarefa do plano. Dois agentes escrevem (`task-implementer` o
código, `test-author` os testes). Os passos de install, build e testes do **seu** registry rodam
por `bin/run.py` (tudo fica capturado). Grava os registros de implementação e de prova, faz o
**bind** no trace e entrega a porta para o `/review-change`.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| task | opcional **se** só houver uma entregável | Identificador `task/<epic>/<name>`. Duas ou mais = stop perguntando qual |
| project root | padrão: raiz git | |
| target | padrão se houver 1 só | |
| slug | padrão se houver 1 iniciativa viva | |

**Pontos importantes:**
- **Uma invocação, uma tarefa.** Para várias, rode de novo (ou use `/deliver-scope`).
- Se o implementador encontra um fato que nenhum nó afirma, ele **para** e entrega duas portas:
  `/analyse` (você escreve o fato) ou `/plan-work` no modo *decided-fact* (o framework decide).
  **Contradição** entre escopo e specification é sempre sua.
- Plano fechado (`closure.md`) = não escreve mais código nele.
- Os roots que escreve precisam começar **limpos**: o commit final
  (`implement-task <slug>: deliver <task>`) leva só o que a invocação escreveu (ver seção 6). Um
  stop não commita nada.
- **Re-delivery:** rodar de novo sobre uma tarefa já entregue reescreve os dois registros. A
  re-delivery "só da prova" (o código fica, só o teste muda) só acontece se você a nomear. Se o
  teste novo falhar e o diagnóstico apontar o código, ela vira re-delivery completa na mesma
  invocação, presa aos testes que já existem (`deliver.py --red-guard`).

**Exemplos:**
```
/implement-task
/implement-task . slug cupom task/validacao/rejeitar-expirado
```

---

### 4.6 `/review-change` — "o segundo par de olhos"

**Para que serve:** quatro julgamentos independentes sobre o que foi entregue: (1) os testes
provam os critérios? (2) o código afirma só o que a specification contém? (3) o código segue o
standard? (4) por que uma execução falhou? (Há ainda um passe de certificação, quando o registro
de prova de uma tarefa oferece um teste como prova de um nó, ou quando você mesmo oferece um.) **Não aprova nada**: produz evidência (*findings*) e
**você** decide o que ela significa.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| tasks revisadas | **obrigatório** | Cada uma já com registro de implementação |
| file set | **obrigatório** | Normalmente vem dos registros; **nunca é descoberto** pela revisão. Revisar menos que os registros dizem é recusado |
| project root / target | padrões como acima | |
| slug | padrão se o `work_root` tiver exatamente uma iniciativa (viva ou fechada) | Revisar um plano fechado é permitido |
| nome da revisão | padrão = o slug | Nome já usado (`review/`, `run`, `siegard-reconcile/`) = stop. A 2ª revisão da mesma iniciativa **precisa de nome novo** |
| steps do standard / run já capturada | opcional | Decidem se roda o passe do standard e o de falhas |

**Exemplo:**
```
/review-change . slug cupom tasks task/validacao/rejeitar-expirado task/validacao/limite-um-cupom  revisão: cupom-r1
```

**Onde mora o conserto de cada finding** (o relatório diz):
- código errado, ou critério registrado como não atendido → `/implement-task` sobre a **mesma
  tarefa** (re-delivery);
- fato que o código afirma e nenhum nó tem → `/analyse`, e depois `/plan-work`;
- regra do standard que parece errada → quem é dono do registry a muda.

**Commit:** `review-change <slug>: review <nome-da-revisão>`, levando o delivery root, o trace e
`siegard-reconcile/<nome-da-revisão>.*`.

---

### 4.7 `/deliver-scope` — "do plano à revisão, sem eu apertar cada botão"

**Para que serve:** carrega **um escopo** pela rota inteira — `/plan-work` → `/implement-task` (por
tarefa) → `/review-change` → prova do que a revisão deixou testável → medição — fazendo um
**commit por etapa** (com pathspec: cada skill chamada commita o que escreveu, e ele commita o log
e a medição) e um log (`orchestration.md`). Ele não julga nada: toda
decisão é da skill chamada. Para onde só pessoa decide, **para**.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| **o pedido (ask)** | **obrigatório** | Suas **próprias palavras** dizendo que esse escopo deve ser levado de ponta a ponta, citadas literalmente. Não se infere de pedido menor |
| project root | padrão: raiz git | |
| target | padrão se houver 1 só | |
| slug | do pedido, ou derivado e avisado | Slug de plano vivo = **retomada**. Slug com `closure.md` = stop |
| alcance (reach) | padrão: o plano todo | `epic/<name>` ou `task/<epic>/<name>`; leva junto as dependências. Id que o plano não tem = stop. Alcance em slug sem plano vivo = stop |

**Antes de qualquer coisa ele exige:** specification válida e **commitada** (`spec.py` limpo),
árvore limpa nas raízes de trabalho/entrega/código/spec, no `siegard-trace.json` e em
`siegard-reconcile/`. Qualquer sujeira = stop (é trabalho de alguém em andamento).

**Portas que ele mesmo toma:** o seu pedido é o "siga". Durante a execução, ele toma sozinho uma
porta *derived* para `/plan-work`, `/implement-task`, `/review-change` ou `/reconcile` que o
`door.py --check` aceite (uma vez por tarefa), registrando uma linha `decided:` no log, com ou sem
goal. Um silêncio da specification vai primeiro pela rota *decided-fact* do `/plan-work`, que
decide e registra. Com um grant armado, ele consulta o `grant.py --decide` antes de parar.

**O que ele NUNCA faz:** `/analyse` (exceto uma vez, antes do plano, sob um goal que pede
"specify"), criar branch, `push`, `stash`, reescrever histórico, commitar sem pathspec, consertar
achados (conserto é um pedido novo seu) ou tentar de novo uma tarefa cuja entrega desistiu.

**Commits:** um por etapa, por pathspec (o da etapa é da skill chamada; o log, `deliver-scope
<slug>: log`, e a medição são dele). Uma execução cujo log fecha numa linha de stop **não
commita mais nada depois dela além da medição**, que leva a raiz de telemetria, o log com a linha
de stop e as execuções capturadas que terminaram `passed`.

**Achados não param a execução:** os findings da revisão vêm inteiros no relatório, e o valor de
cada um é decisão sua (sob um goal com `--correct contradicts`, os `contradicts` são corrigidos uma
vez).

**Quando para:** contradição entre escopo e specification; um segundo silêncio sobre uma tarefa que
a rota *decided-fact* já respondeu nesta execução; uma nota `BLOCKING` que fica sobre todas as
tarefas que restam; árvore com mudança que não
é dele; campo ausente no `siegard.json`; specification que não passa no `spec.py`; um build
vermelho que nenhuma mudança nos arquivos da própria tarefa resolve (`outside-task`); entre
outros. (Um vermelho que só um teste declarado resolve **não** para: o test-author o corrige.) Em
cada stop ele entrega as portas do relatório que parou, com a recomendada quando esse relatório fez
uma: *derived*, onde um fato do disco decide, ou *judged*, uma decisão de custo ou de leitura do
pedido. Contradição, duas leituras da mesma evidência e o valor de um achado **não** têm
recomendação: são suas.

**Exemplo:**
```
/deliver-scope Leve de ponta a ponta o escopo: "permitir cupom de desconto no checkout".
Projeto ., target backend, slug cupom.
```
Só um épico: `... slug cupom epic/validacao`. Só uma tarefa e suas dependências:
`... slug cupom task/validacao/rejeitar-expirado`.

---

### 4.8 `/siegard-goal` — "faça tudo e só me chame no fim" (fechada ao modelo)

**Para que serve:** transforma **um escopo** em um **goal**: o Siegard leva o escopo até o fim,
sem perguntar nada, e **sempre termina**, porque um script lê do disco se acabou (`goal.py
--state`): `state A` (entregue, provado, revisado, medido) ou `state B` (parou onde só você mexe).
Antes do primeiro passo ele já confere tudo o que o `/deliver-scope` recusaria.

**Forma geral:**
```
/siegard-goal [--arm] [<project-root>] (epic/<n> | task/<epic>/<n> ... | <objetivo em prosa> | --objective-file <caminho>) [--slug <slug>] [--target <chave>] [--correct contradicts] [--no-specify]
```

| Parâmetro | O que faz | Se ausente |
|---|---|---|
| `--arm` (**só como 1º argumento**) | Arma o goal agora | Só **compõe**: grava o objetivo e te dá a linha para colar |
| `<project-root>` | Raiz do projeto | Raiz git da sessão, avisada |
| **Escopo** (exatamente um) | Ids `epic/<n>` / `task/<epic>/<n>` de um plano vivo, **ou** objetivo em prosa, **ou** `--objective-file <caminho>` | Sem escopo = stop. Dois escopos juntos = stop |
| `--slug` | Nome da iniciativa | Ids: o único plano vivo que contém todos; prosa: slug novo (até 5 palavras) |
| `--target` | Chave do target | O único declarado; mais de um = stop |
| `--correct contradicts` | Política de achados: **uma vez**, corrige achados do tipo `contradicts` | Nenhum achado é corrigido: todos são só relatados |
| `--no-specify` | Só com objetivo em prosa ou `--objective-file`: **não** roda `/analyse` antes | O padrão é rodar `/analyse` uma vez sobre o objetivo antes do plano |
| `--specify` | Diz em voz alta o padrão. Como o `--no-specify`, só vale com objetivo em prosa ou `--objective-file`: sobre ids, os dois são recusados (e os dois juntos também) | — |

**Combinações que importam:**

| Você escreve | Resultado |
|---|---|
| `/siegard-goal . "…prosa…"` | **Compõe** (não arma). Entrega a linha `--arm` completa para você colar |
| `/siegard-goal --arm . "…prosa…"` | **Arma e começa já**; `/analyse` roda uma vez antes do plano |
| `/siegard-goal --arm . "…prosa…" --no-specify` | Arma **sem** especificar; para no primeiro fato que a specification não tem |
| `/siegard-goal --arm . epic/validacao` | Arma sobre um épico de plano vivo (slug deduzido) |
| `/siegard-goal --arm . task/validacao/a task/validacao/b --slug cupom` | Duas tarefas e suas dependências |
| `/siegard-goal --arm . --objective-file docs/pedido.md` | Objetivo longo vindo de arquivo |
| `... --correct contradicts` | Achados `contradicts` da revisão são corrigidos uma vez, sem te perguntar |
| `/siegard-goal --arm . "o texto acima"` (**citação**) | **Não arma**: compõe. Você lê o arquivo do objetivo (o texto citado, copiado literalmente) e depois arma por `--objective-file` |

**Regras que pegam novato:**
- A palavra `--arm` só vale como **1º argumento**. "Arma aí" numa mensagem seguinte **não arma**.
- Seu objetivo é passado **literal**; ninguém resume, traduz ou "corrige".
- Com `--no-specify`, um objetivo que muda um fato do negócio (um status, uma recusa, o que o
  sistema diz, quem vê o quê) **para no primeiro fato que a specification não tem**; o relatório
  avisa isso na hora de armar.
- Edição do `siegard.json` ou do standard não cabe num goal: é sua.
- Para **acompanhar**: `/siegard-progress <root> <slug>`. Para **abortar à mão**:
  `! python3 -B <plugin>/bin/goal.py --disarm <root>`.
- Só **um** goal armado por projeto.
- Dentro do goal: uma *door* **derived** (decidida por fato) é tomada pelo próprio
  `/deliver-scope`; uma *judged* (custo ou leitura do pedido) só se você armou um `/siegard-grant`
  com `--budget`. Contradição, duas leituras da mesma evidência e o valor de um achado continuam
  **seus**.
- Quatro respostas `not yet` idênticas seguidas = o goal pausa.
- Quem decide o fim é o script: `goal.py --state` imprime `state A`, `state B` ou `not yet` na
  primeira linha, e o hook `Stop` do plugin age sobre essa linha (nunca sobre uma leitura do modelo).
- Se o goal parou numa linha de stop, o resto da execução **não commita mais nada além da
  medição** (raiz de telemetria, o log com a linha de stop e as execuções que terminaram `passed`).
- Com `--specify` (padrão), o `/analyse` commita a specification **à parte**, para você revisar
  depois do goal.

---

### 4.9 `/siegard-grant` — "pode decidir por mim nos stops" (fechada ao modelo)

**Para que serve:** autoriza o Siegard a tomar as decisões que os stops devolveriam. O grant vale
**até você limpar**, até o plugin mudar de versão ou (com `--slug`) até a iniciativa ser fechada.
Sem grant, uma decisão *judged* sempre volta para você.

```
/siegard-grant [<project-root>] [--clear | [--slug <slug>] [--target <key>] [--doors <skill>,...|none] [--budget <n>] [--commits] [--close] [--routes] [<uma frase sua>]]
```

| Parâmetro | Significado | Padrão |
|---|---|---|
| *(nenhum argumento)* | **Não arma nada**: só mostra o grant armado | — |
| `<project-root>` | Raiz do projeto | Raiz git da sessão (a linha `project_root:` do `project.py --here`), avisada |
| `--clear` (sozinho, ao lado do root) | Desarma | — |
| `--slug` | Vale só para uma iniciativa viva | Todas as iniciativas vivas |
| `--target` | Target | O primeiro declarado, avisado |
| `--doors a,b` | Portas que podem ser tomadas: `plan-work`, `implement-task`, `review-change`, `reconcile`, `deliver-scope`, `analyse` — ou `none` | As seis |
| `--budget <n>` | Quantas decisões **judged** por iniciativa | **0** (sem orçamento, decisão de custo para) |
| `--commits` | Autoriza os commits do que a rota escreveu | Nenhum |
| `--close` | Autoriza **fechar** a iniciativa quando tudo estiver entregue, provado e revisado (suas palavras são o motivo do fechamento) | Nenhum |
| `--routes` | Deixa o Siegard escolher a **rota** de um pedido que não nomeia nenhuma: `/analyse` ou `/plan-work` numa iniciativa nova, do mesmo jeito que responde as portas de uma parada (orçamento de rotas *judged* contado à parte). Nunca com `--slug`, e só se `--doors` tiver `analyse` ou `plan-work` | Nenhum: a rota é sua |
| frase | Qualquer texto seu | Opcional: as flags já são o grant |

**Só um grant armado por projeto:** para mudar orçamento ou portas, arme de novo. O arming
substitui o grant em pé, que fica registrado como `replaced` (a linha `ended:` diz o que ele
cobria); não precisa de `--clear` antes.

**O grant nunca toma:** escolha que só você faz, `push`, branch, edição fora de skill,
`siegard.json`, standard, `CLAUDE.md`, nem nada fora do projeto. Com `--routes`, continuam suas a
rota de um achado, uma rota de ponta a ponta (`/deliver-scope`, `/adopt-scope`) e o incremento
corretivo. Se `--budget` for dado,
`--doors` não pode ser vazio.

**Exemplos:**
```
/siegard-grant . --budget 5 --commits --close "pode seguir, eu reviso depois"
/siegard-grant . --slug cupom --doors implement-task,review-change --commits
/siegard-grant . --routes --budget 3 --commits
/siegard-grant . --clear
/siegard-grant
```
(o último só mostra o que está armado.)

**Combinando com goal:** o `/deliver-scope` (com ou sem goal) toma sozinho as *doors* **derived**.
O grant também toma as derived da lista `--doors`, em qualquer sessão que receba o stop, e só o
`--budget N` dele libera as **judged**. Goal e grant são independentes. O grant é consultado **no
momento de cada stop**, então precisa estar armado antes de o goal chegar nele; armá-lo antes do
goal é a ordem mais simples.

---

### 4.10 `/reconcile` — "alguém mexeu no código por fora"

**Para que serve:** quando um arquivo mudou **sem** passar por uma tarefa (hotfix, merge resolvido
na mão, reescrita que atropelou outro binding), o trace fica **desatualizado**. O `/reconcile`
lê os arquivos contra os nós ligados a eles (um juiz por arquivo), registra a resposta por nó e
**só refaz o bind do que o juízo liberou**. Para um nó não liberado, entrega as duas portas **sem
escolher entre elas** (é decisão sua):
(a) o código está certo, a specification está atrasada → `/analyse` com o achado como material;
(b) a specification está certa, o código está errado → `/plan-work` corretivo.
Quando o achado é só comentário/prosa no arquivo, ele **recomenda** remover os comentários e rodar
o `/reconcile` de novo. Para o que ficou testável, entrega também a rota do *proof increment*.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| file set | **obrigatório** | Lista explícita, relativa ao target. **Nunca é descoberto**. Em adoção sobre ledger, vem das áreas do material (você pode nomear um subconjunto) |
| project root / target | padrões | |
| slug | **obrigatório** | Nome desta reconciliação (grava `siegard-reconcile/<slug>.md`). Slug usado = stop |
| `certifications` | opcional | Por nó, o(s) teste(s) que o provam + o step do registry que os roda |
| `rewrite` | opcional | **Sua afirmação** de que os arquivos mudaram por **uma** reescrita mecânica, + os steps do registry que mostram que a árvore reescrita compila e passa. A skill só **transcreve** o que você declarou num pequeno YAML (`pattern` e `replacement`, como o `re.sub` do Python os lê, mais os `steps`); ela nunca deduz a reescrita de um diff |
| `adoption` | opcional | Para código **nunca entregue**. Normalmente você não monta isso: o relatório do `/analyse` sobre material de survey entrega a invocação do `/reconcile` pronta, em modo adoção sobre o **ledger** (que dá o file set e os candidatos de cada arquivo); você preenche o slug e, se quiser, os arquivos `outside` do julgamento. Sem ledger, você nomeia os **candidatos** (nós que o `/analyse` escreveu) explicitamente |
| auditoria | opcional | Pedir "auditoria" re-julga bindings que **não** derivaram (nada omitido). Candidatos: `trace.py --encodes --rank <raiz-do-target>`. Só quando você pede. Não combina com `rewrite`, com `certifications` nem com adoção |

**Antes de rodar:** os arquivos nomeados, as provas e **toda a raiz da specification**
commitados; `siegard-trace.json` limpo; target sob git; specification validando limpa
(`spec.py`). Sem `siegard-trace.json` = stop, exceto em adoção.

**Commit:** ao final ele commita como `reconcile <slug>` (o registro em `siegard-reconcile/` e o
rebind no trace).

**Exemplos:**
```
/reconcile  file set: src/billing/raise.ts   project root: .   slug: hotfix-fatura
/reconcile  file set: src/orders/a.ts, src/orders/b.ts  slug: renomeia-x  rewrite: troquei X por Y nestes arquivos, só isso; steps: build, test
/reconcile  file set: src/orders/a.ts, src/orders/b.ts  slug: adocao-orders  adoption  candidatos: rules/orders/pedido, rules/orders/cancelamento
```

(O file set é sempre uma **lista de caminhos explícitos**, nunca um padrão com `*`. O terceiro
exemplo é a forma **sem ledger**.)

**Como saber o que reconciliar:** o `/siegard-status` já entrega a invocação do `/reconcile`
pronta (file set + slug livre), pela forma `trace.py --check <raiz-do-target> --reconcile-set`.
Não monte o file set à mão a partir do `--check`. `trace.py --owed <raiz-do-target>` mostra o que
reconciliações anteriores acharam e nenhum bind fechou, e os nós que um teste fecharia. Arquivo que
**sumiu** da árvore não vai para o `/reconcile`: sai por `trace.py --release`.

---

### 4.11 `/check-source` — "ler o que ninguém entregou, contra o standard"

**Para que serve:** arquivos mudados **sem tarefa** não aparecem em nenhuma revisão. O
`/check-source` lê um conjunto de arquivos contra as regras do standard **que dependem de leitura**
e registra cada desvio citando **exatamente uma regra**, ao lado do trace. Nunca escreve código e
não roda nada: as regras que uma ferramenta decide ficam com a suíte do projeto, e um resultado
limpo aqui **não** é um resultado limpo contra o standard inteiro.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| file set | **obrigatório** | Lista explícita relativa ao target. Normalmente vem de `trace.py --check --all` ou de uma `/review-change`. Para ver o que mudou antes de nomear: `trace.py --encodes --changed <raiz-do-target> [<ref>]` |
| project root / target | padrões | |
| standard | **obrigatório** | Do `siegard.json` para esse target, salvo se a invocação nomear outro. Sem standard (ou `null`) = stop com o `/siegard-config` pronto |

Útil para o que o drift receipt contou como "suprimido" (targets em `edits_freely`). O registro
vai para `siegard-check/<slug>.md` na raiz git do target; só a pasta `siegard-check/` precisa
estar limpa antes (as edições no código são justamente o que ela lê). Slug já usado = stop. A skill
**não commita**: o commit é seu.

---

### 4.12 `/survey` — "ler código que já existe"

**Para que serve:** ao **adotar** o Siegard num código que já existia, lê as áreas e escreve o
**material** (fatos de domínio, recusas, vocabulários fechados, o que vem de fora), um arquivo por
área, cada fato ao lado do caminho onde foi lido. Entrega a invocação do `/analyse` que o
transforma em nós. **Nunca** escreve nó nem binding.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| project root / target | padrões | |
| slug | **obrigatório** | Nome do survey (pasta em `siegard-survey/`). Slug usado = stop |
| areas | **obrigatório** | Cada uma: nome curto + caminhos/pastas a partir do target. Um arquivo em duas áreas = stop. Testes não são área na forma *source* |
| form | opcional | `tests` = lê os **testes declarados** e escreve *intent material* (o que o código **deve** fazer). É o incremento **depois** da adoção. Exige `tests` declarado no `siegard.json` para o target; sem isso, stop com o `/siegard-config` pronto |

Todo arquivo de cada área precisa estar **commitado**. O `/survey` **não commita**: o commit do
material é seu (ou do `/adopt-scope`, quando ele conduz a rota).

**Exemplos:**
```
/survey . target backend slug orders-v0 areas: orders = src/orders ; billing = src/billing
/survey . target backend slug orders-intent form tests areas: orders = src/orders
```

---

### 4.13 `/adopt-scope` — "adotar um contexto, de ponta a ponta"

**Para que serve:** executa a rota de adoção inteira para **um contexto** de código existente:
`/survey` → `/analyse` (sobre o material) → `/reconcile` em modo adoção → medição, commitando entre
as etapas (`adopt-scope <slug>: <etapa>`) e registrando um log
(`siegard-survey/<slug>/orchestration.md`). Ele **não altera código**, não cria branch (commita
onde o `HEAD` aponta) e não chama o `/deliver-scope`.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| **o pedido** | **obrigatório** | Suas palavras dizendo que esse contexto deve ser adotado de ponta a ponta, citadas literalmente (ou uma condição de goal que nomeie a skill) |
| project root / target | padrões | |
| slug | do pedido, ou derivado | Nomeia também o registro em `siegard-reconcile/`. Já existe `orchestration.md` = **retomada** (continua da etapa cujo commit o log não tem) |
| areas | **obrigatório** | Passadas ao `/survey` sem alterar |
| outside | opcional | Arquivos fora do julgamento. Testes declarados nunca são `outside` |
| certifications | opcional | Testes que você oferece como prova de nós nomeados, no formato do `/reconcile` |

**Pré-requisito:** specification válida e commitada; árvore limpa em spec, target, trace,
`siegard-reconcile` e `siegard-survey/<slug>`. Não faz `/plan-work`, `/implement-task` nem
`/review-change`: um comportamento errado achado vira `contradicts` no registro e a correção é um
**novo pedido** seu.

---

### 4.14 `/siegard-status` — "como estamos?"

**Para que serve:** responde, **do disco** e a cada vez, onde o projeto está: se a specification
está sã, que iniciativas estão vivas, o que falta entregar e o que cada tarefa espera, notas
`BLOCKING`, drift do trace por classe, decisões tomadas em seu nome e o que está sem commit. Onde
há algo a reconciliar, já traz a invocação do `/reconcile` pronta. Só lê. Com um grant armado,
o próximo passo que ele recomenda vira uma decisão que o grant responde como numa parada: segue
sozinho dentro das portas e do orçamento que você armou.

| Parâmetro | Notas |
|---|---|
| project root | O único. Padrão: raiz git |

Use **sempre** em vez de perguntar ao Claude "em que pé estamos?". Se faltar campo no
`siegard.json`, essa ausência **é** o status e ele te entrega o `/siegard-config` pronto.

---

### 4.15 `/siegard-progress` — "a tabela de uma iniciativa"

**Para que serve:** uma linha por tarefa (status + detalhe do porquê) de **uma** iniciativa viva.
Barato e repetível: perfeito dentro de `/loop`.

| Parâmetro | Notas |
|---|---|
| project root | Padrão: raiz git |
| initiative (slug) | Inferida se houver **exatamente uma** viva; se houver mais, lista os slugs e pergunta. Zero viva = stop |

Se o plano está inválido ou `STALE`, essa é a resposta (citada literalmente) e a tabela não sai.

**Exemplo com loop:**
```
/loop 5m /siegard-progress . cupom
```

---

### 4.16 `/siegard-telemetry` — "como o trabalho aconteceu" (custo e fricção)

**Para que serve:** relatório de uma **janela de tempo**: quais agentes rodaram e a que custo
(tokens e tempo), quais comandos do framework recusaram, o que parou para uma pessoa, o que foi
decidido **em nome** dela. Saem dois arquivos lado a lado em `telemetry_root`: JSON + Markdown
(sempre em inglês). É o que você manda de volta ao mantenedor do framework.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| project root | padrão: raiz git | |
| janela: início | **obrigatório** | ISO-8601, um commit (diz qual), ou `last` (continua de onde o relatório anterior fechou). Sem nada e sem relatório anterior = stop |
| janela: fim | opcional | Padrão: agora |

Antes de ler as transcrições da sessão, ele roda um **probe** e **anuncia** literalmente o que vai
ler (nenhum texto de mensagem sai de lá); você pode recusar a leitura nesse ponto.
`telemetry_root` precisa estar declarado. **Não commita:** o `git diff` dos dois arquivos é a sua
revisão.

**Exemplos:**
```
/siegard-telemetry . desde 2026-11-10T00:00:00-03:00
/siegard-telemetry . last
```

---

### 4.17 `/siegard-archive` — "enxugar a árvore" (fechada ao modelo)

**Para que serve:** remove da árvore de trabalho as iniciativas **fechadas** cujos arquivos estejam
todos **commitados** e cujo histórico ainda **valide** (plano + entregas, juntos e inteiros). Uma
iniciativa que falha num critério é pulada, com o motivo. A história continua no git;
specification, decision logs, trace e registros de reconciliação **ficam**. Nunca commita, tagueia
ou faz stage: ele entrega, na ordem, a tag no commit de partida e o commit da remoção por
pathspec, prontos. **Os atos de git são seus**.

| Parâmetro | Obrigatório? | Notas |
|---|---|---|
| project root | padrão: raiz git | |
| escopo | **obrigatório** | `--all` (tudo que está fechado) **ou** os slugs. Nunca inferido |
| `--target <key>` | opcional | Só se os registros de uma entrega não nomearem target e o projeto tiver mais de um |
| só ver o que sairia | — | Peça "só o que sairia": roda `--check` e não muda nada |

**Exemplos:**
```
/siegard-archive . --all
/siegard-archive . cupom frete
```

---

### 4.18 `/clarify-request` — "traduza meu pedido vago" (fechada ao modelo)

**Para que serve:** reescreve um pedido solto ("arruma isso aí", "faz o que a gente combinou") como
**uma instrução precisa**. Resolve por leitura o que a conversa e o projeto já respondem, só te
pergunta o que é decisão **sua** e mantém intenção, modo e escopo. Se o pedido só lê ou planeja
(`ANALYZE`, `PLAN`) e dá para responder só lendo arquivos, ele já **executa na mesma vez**. Se
precisa rodar um comando (até um teste) ou se o pedido age, **entrega a instrução sem executar**.

| Parâmetro | Notas |
|---|---|
| o pedido | **Obrigatório**, em suas palavras. Ausente = stop |

A instrução sai **em inglês** (quem a lê é o executor; você só a audita) e é validada por
`clarify.py`. Ele pergunta no máximo duas vezes; se ainda faltar decisão sua, para sem instrução.

Pedido que já é invocação de skill (`/algo ...`) **não** é reescrito; pedido já preciso também não
ganha acréscimos. Regra de ouro dela: *esclarecer o que você quis dizer, nunca completar o que
você não decidiu*.

---

## 5. Cenários de uso

> Em todos os cenários abaixo, suponha que o projeto já tem `siegard.json` (cenário 0).

### Cenário 0 — Primeiro dia: preparar um projeto novo

1. `/siegard-config` — declare `specification_root`, `targets`, `work_root`, `delivery_root`,
   `telemetry_root` (e `tests`, se quiser). **Commite o `siegard.json`** (e o
   `.claude/settings.json` da instalação, se houver): o `/siegard-standard` para com qualquer
   pendência fora do arquivo do standard.
2. `/siegard-standard` — (opcional, mas recomendado) escreva o standard a partir do que o
   linter/compilador do projeto já faz. Revise o `git diff` do standard.
3. `/siegard-config` com `standard` apontando para ele. **Você** commita o standard e o
   `siegard.json`: nenhuma das duas skills commita (o `git diff` é a sua revisão). As outras skills
   exigem essa árvore limpa.
4. `/siegard-status` — confirme que tudo aparece e que não há linha `rules:`.

---

### Cenário 1 — Desenvolver uma **feature nova**, passo a passo (manual, você no controle)

Use quando quiser **revisar entre as etapas**.

1. **Especifique:** `/analyse . <material com os fatos da feature>`
   O `/analyse` **já commita** a specification; revise o commit (nós + decision logs) e, se
   discordar de algo, faça uma nova mudança.
2. **Planeje:** `/plan-work . target backend slug cupom — <o escopo em prosa>`
   O relatório mostra épicos, tarefas e notas. Fato que a specification não diz é decidido e
   registrado no decision log (revise depois).
3. **Entregue, tarefa por tarefa:** `/implement-task . slug cupom task/<epic>/<name>`
   (sem o id, se só houver uma entregável). Repita até acabar. `/siegard-progress . cupom` mostra
   o que falta.
4. **Revise:** `/review-change . slug cupom tasks <ids>` e leia os *findings*. **Você** decide
   o que fazer com cada um.
5. **Se um finding vira conserto:**
   - código errado ou critério não atendido de uma tarefa deste plano → `/implement-task` de novo
     sobre a **mesma** tarefa (re-delivery);
   - fato no código que nenhum nó afirma → `/analyse`, e depois `/plan-work`;
   - comportamento errado que nenhum critério cobria, em código já entregue → Cenário 2 (ou o 3, se
     a specification estiver errada ou omissa).
6. **Encerre:** `/plan-work . slug cupom — closing: <motivo>`.

> Atalho: depois do passo 1, os passos 2 a 4 inteiros são o `/deliver-scope` (Cenário 4).

---

### Cenário 2 — Corrigir um bug **sem análise** (a specification já está certa)

O comportamento correto **já está escrito** em algum nó; o código é que está errado, e nenhum
critério de tarefa cobre esse comportamento. (Se o bug é um critério não atendido de uma tarefa
recém-entregue, o conserto é `/implement-task` sobre a mesma tarefa: veja o Cenário 1, passo 5.)

1. Identifique o arquivo e o comportamento errado, com a reprodução. O arquivo precisa estar no
   trace (ligado por alguma entrega); se não estiver, o corretivo para.
2. **Plano corretivo:**
   ```
   /plan-work . target backend slug fix-cupom — corrective: cupom expirado ainda é aceito.
   Reprodução: criar cupom com data de ontem e aplicar no checkout. Arquivo: src/coupon/apply.ts
   ```
   (O **épico** do conserto é sempre novo; ele não reabre um épico entregue. O slug pode ser o
   da iniciativa se o plano ainda estiver **vivo**; se o plano já foi **fechado**
   (`closure.md`), o conserto precisa de um slug **novo**, como `fix-cupom`.)
3. `/implement-task . slug fix-cupom` — escreve a correção **e** o teste de forma independente.
4. `/review-change . slug fix-cupom tasks <id>` — produz a evidência (findings); **você** decide se
   o conserto vale.
5. Se tudo OK: `/plan-work . slug fix-cupom — closing: bug corrigido`.

**Por que não consertar "na mão"?** Porque uma única cabeça escreve conserto e teste (concordam por
construção) e o trace fica com um digest que já não existe.

**Se o conserto bateu num silêncio:**
- Se o **binder** não acha um nó que afirme o fato, o próprio `/plan-work` decide o fato às cegas e
  registra no decision log. Você não faz nada (revisa depois).
- Se quem parou foi o **implementador** ("nenhum nó afirma isso"), o relatório entrega duas
  portas: `/plan-work` no modo *decided-fact* (o framework decide e registra) ou `/analyse` (você
  escreve o fato). A recomendação vem junto com as portas.

---

### Cenário 3 — Corrigir um bug **com análise** (a specification está errada ou omissa)

O comportamento "errado" na verdade **nunca foi especificado**, ou a regra escrita está errada.

1. **Descubra:** `/siegard-status` e/ou o relatório da revisão. Ex.: um `contradicts`.
2. **Analise:** `/analyse . <o fato certo, em prosa, com o caso concreto>`
   Os nós **mudam** (evolução da specification). O `/analyse` commita; você revisa o commit.
   Se o nó mudado é implementado por uma tarefa de um plano **vivo**, esse plano passa a acusar
   `MOVED`: rode `/plan-work` de novo sobre o slug antes de seguir.
3. **Planeje o conserto:** `/plan-work . target backend slug fix-cupom — corrective: …`
   Agora o binder acha o nó certo.
4. `/implement-task` → `/review-change` → *closing*, como no Cenário 2.

**Quando é com análise e quando é sem?** Pergunta de ouro: *"existe um nó que diz o que o código
devia fazer?"* Sim → sem análise (Cenário 2). Não, ou o nó está errado → com análise (este).
Dúvida entre os dois? `/siegard-status` e o texto do finding dizem:
- `contradicts` com código certo = analisar;
- `contradicts` com specification certa = se o finding é de uma revisão sobre a tarefa
  recém-entregue, `/implement-task` sobre a mesma tarefa; se é de um `/reconcile` (código mexido
  por fora ou já fechado), plano corretivo.

**Se o código foi mudado por fora (hotfix de incidente):** o `/siegard-status` mostra o drift e já
entrega o `/reconcile` pronto (file set + slug livre); cole essa invocação. O juiz devolve **duas
portas** sem escolher entre elas: "código certo, specification atrasada" (`/analyse` com o achado
como material) ou "specification certa, código errado" (plano corretivo). Use `/check-source` para
ler esses mesmos arquivos contra o standard.

---

### Cenário 4 — Usar o `/deliver-scope` (entrega de ponta a ponta, com você por perto)

Use quando a specification **já está commitada e sã** e você quer que o Siegard faça plano →
entrega → revisão → medição, **commitando a cada etapa**, parando só no que é seu.

**Preparação (o Siegard recusa se faltar):**
- `spec.py` limpo e specification **commitada**;
- árvore limpa nas raízes de trabalho/entrega/código/spec, no `siegard-trace.json` e em
  `siegard-reconcile/`;
- você está no branch onde quer os commits (ele **não** cria branch nem faz push).

**Invocação:**
```
/deliver-scope Leve de ponta a ponta: "permitir cupom de desconto no checkout". Projeto ., target backend, slug cupom.
```
- Para um pedaço de um plano vivo: acrescente `epic/validacao` ou `task/validacao/rejeitar-expirado`.
- Para **retomar** depois de uma pausa: o mesmo slug (plano vivo = retomada).

**O que você vê no fim:** um relatório com o que foi feito (um commit por etapa, log em
`orchestration.md`), as portas *derived* que ele mesmo tomou (linhas `decided:`), os findings da
revisão (que **não** param a execução: o valor de cada um é seu) e, se parou, as portas do stop,
com a recomendada quando houver uma (e a razão + o fato que a reverteria). Exemplos de stop:
contradição entre escopo e specification, um silêncio que a rota *decided-fact* já respondeu nesta
execução, árvore com mudança que não é dele.

**Se parar:** leia a recomendação. Se for *derived* (um fato do disco decide), você pode dizer
"siga", e o Siegard toma. Se for *judged* e você não armou um grant, a decisão é sua.

---

### Cenário 5 — Usar o `/siegard-goal` (autônomo: apontar e voltar depois)

Use quando você quer **sair andando**. O goal só termina quando um script lê `state A` ou
`state B` do disco, então **sempre termina**.

**Receita padrão (a que eu recomendo ao novato):**

1. **Opcional, mas é o que deixa o goal tomar decisões de custo:**
   ```
   /siegard-grant . --budget 5 --commits --close "pode seguir, eu reviso depois"
   ```
2. **Componha primeiro, para ver o que vai acontecer** (não arma):
   ```
   /siegard-goal . "Permitir cupom de desconto no checkout: percentual de 1 a 50%, expira em 30 dias, no máximo um por pedido."
   ```
   Ele confere tudo o que o `/deliver-scope` recusaria e te devolve a linha pronta com `--arm`.
3. **Arme** colando essa linha (ela começa com `/siegard:siegard-goal --arm ...`).
   Ou direto, se já tem certeza:
   ```
   /siegard-goal --arm . "Permitir cupom de desconto no checkout: ..." --target backend --slug cupom --correct contradicts
   ```
4. **Acompanhe:** `/siegard-progress . cupom` (ou `/loop 5m /siegard-progress . cupom`).
5. **Se precisar abortar:** `! python3 -B <plugin>/bin/goal.py --disarm .`
6. **Quando acabar (state A ou B):** leia o relatório e **revise a specification** que o
   `/analyse` escreveu no começo (ela foi commitada à parte, para você revisar depois).

**Escolhas do dia a dia:**

| Situação | Como invocar |
|---|---|
| Objetivo novo, specification ainda não tem os fatos | `--arm` com prosa (o padrão **especifica antes**) |
| Specification **já** tem os fatos e você só quer a entrega | `--arm` com prosa **e** `--no-specify` (ou use `epic/...` de um plano vivo) |
| Plano vivo, só um pedaço | `--arm . epic/<name>` ou `task/<epic>/<name> ...` |
| Pedido longo | `--objective-file docs/pedido.md` |
| Quer que achados `contradicts` sejam corrigidos sem te chamar | `--correct contradicts` |
| Quer ler o objetivo antes de armar | omita o `--arm` (compõe) |
| Seu "objetivo" é "as partes 2 e 3 acima" | Citação: o Siegard compõe, grava o texto citado num arquivo e **você lê antes** de armar |

**O que o goal nunca faz:** push, branch ou reescrita de histórico (o hook do plugin recusa),
editar `siegard.json` ou o standard (um commit que os toque vira `state B`), nem decidir uma
contradição. Quando bate em algo que só você decide, o goal termina em `state B` e o relatório diz
onde parou e por quê.

---

### Cenário 6 — Adotar um projeto que **já tinha código**

**Versão manual (um contexto por vez):**
1. `/siegard-config` (declare os targets e `tests`), commite.
2. `/survey . target backend slug orders-v0 areas: orders = src/orders` — material do código.
   **Commite** `siegard-survey/orders-v0/` (o `/survey` não commita).
3. `/analyse` sobre o material (a porta vem pronta no relatório do survey).
4. `/reconcile` em **adoption**: cole a invocação que o relatório do `/analyse` entrega (sobre o
   ledger); preencha o slug e, se quiser, os arquivos `outside`.
5. Depois da adoção, opcionalmente: `/survey ... form tests` com um slug novo, e então `/analyse`
   sobre esse material de intenção e a `/reconcile` em adoção que o relatório dele entrega (ela
   julga cada arquivo que o material governa, nunca os testes). É o incremento seguinte, não parte
   da adoção.

**Versão automática:** `/adopt-scope Adote de ponta a ponta o contexto "orders". Projeto ., target backend, slug orders-v0, áreas: orders = src/orders.`

---

### Cenário 7 — Alguém editou o código por fora (incidente, merge manual)

1. `/siegard-status` (ou `trace.py --check <raiz-do-target> --reconcile-set`) — lista o drift e já
   entrega o `/reconcile` pronto. Os arquivos precisam estar **commitados** (e o
   `siegard-trace.json` limpo).
2. Cole essa invocação (`/reconcile  file set: <caminho1>, <caminho2>  project root: .  slug:
   <nome>`). Não monte o file set à mão.
3. Leia as duas portas devolvidas para o que o juiz **não** liberou e escolha uma (é sua).
4. Para ler esses mesmos arquivos contra o standard: `/check-source`.

(Arquivo que **sumiu** da árvore não vai para o `/reconcile`: sai por `trace.py --release`.)

---

### Cenário 8 — Retomar depois de uma pausa, uma compactação ou um stop

- **Plano vivo + mesmo slug = retomada.** `/deliver-scope` continua do conjunto entregável como
  está no disco; o relatório diz que é uma retomada. `/adopt-scope` retoma da etapa cujo commit o
  `orchestration.md` ainda não tem.
- Depois de uma **compactação** da conversa, o pedido que autorizou a rota é lido de novo do
  registro (`ask.py --read`, pelo caminho e digest que o `ask.py --record` imprimiu), nunca de um
  resumo. Sob um goal armado, a própria condição (que vale também depois de cada compactação) é a
  autorização, e o hook `Stop` a repete sempre que bloqueia uma parada com `not yet`.
- **Plano fechado** (`closure.md`) não se retoma: um novo escopo usa um slug novo.
- Antes de retomar, `/siegard-status` mostra o que ficou pendente.

---

### Cenário 9 — Rotina de acompanhamento e limpeza

| Quando | O quê |
|---|---|
| Qualquer dúvida sobre "como estamos" | `/siegard-status` |
| Iniciativa em andamento | `/siegard-progress . <slug>` (ou em `/loop`) |
| Retrospectiva de custo/fricção | `/siegard-telemetry . last` (na primeira vez, um instante ISO ou um commit) |
| Iniciativas fechadas e commitadas, árvore pesada | `/siegard-archive . --all`, depois **você** roda os `git` que ele entrega |
| Pedido confuso | `/clarify-request <seu pedido>` |

---

## 6. Quem commita o quê

| Quem | Commita? | Detalhe |
|---|---|---|
| `/analyse`, `/plan-work`, `/implement-task`, `/review-change`, `/reconcile` | **Sim, o que a própria invocação escreveu** | Um commit por invocação, por pathspec, com mensagem que cita a skill e o slug (ex.: `plan-work cupom: plan`). Nunca um arquivo que a skill encontrou pendente. Se uma raiz que ela vai commitar já tinha mudança que não era dela, **para** |
| `/deliver-scope`, `/adopt-scope` | **Sim** | No `/deliver-scope`, cada skill chamada commita o que escreveu, com o próprio nome, e ele commita o log (`deliver-scope <slug>: log`), a medição e as execuções de uma entrega parada. O `/adopt-scope` commita cada etapa ele mesmo (`adopt-scope <slug>: <etapa>`). Sempre por pathspec. Linha de stop no log = nada mais é commitado além da medição (raiz de telemetria, o log com a linha de stop e as execuções capturadas que terminaram `passed`) |
| `/siegard-config`, `/siegard-standard`, `/siegard-archive`, `/survey`, `/check-source`, `/siegard-telemetry` | **Não** | O `git diff` é a sua revisão e o commit é seu (no `/adopt-scope`, o commit do survey é dele, por etapa). O `/siegard-archive` entrega os comandos `git` prontos, na ordem |
| `/siegard-goal`, `/siegard-grant` | Não | Só gravam o arquivo do objetivo/das palavras (sob a raiz de telemetria, que a medição commita) e o registro de arme (dentro de `.git`, nunca commitado) |
| Uma sessão fora de skill | Só com palavras suas | Uma palavra de commit, um "siga" que nomeia o próximo passo, um pedido seu que declare a rota inteira de ponta a ponta (depois de uma compactação, relido por `ask.py --read`, ou a condição de um goal que nomeie a rota), ou um grant com `--commits` quando o `grant.py --commit` aceita. Sempre por pathspec |
| `push`, branch, reescrita de histórico | **Nunca** de skill, goal ou grant | Onde um goal ou grant está armado, o hook do plugin recusa; fora deles só com palavras suas na sessão |
| Arquivos que nenhum grant leva num commit | — | `siegard.json`, um standard, `CLAUDE.md`, credencial, arquivo de specification que o `HEAD` já tem e o commit modifica (fora do decision log e do que um registro nomeia), `closure.md` sem `--close`, e qualquer caminho fora do projeto ou que a rota não escreve |

**Por que importa:** o commit **é** a revisão. Em vez de pedir aprovação antes, o Siegard divulga
tudo (log de decisões, relatório) e você revisa depois; discordar é uma mudança comum.

---

## 7. "Qual skill uso?" — decisão rápida

```
Tenho um documento/ideia com FATOS do domínio ................ /analyse
Quero planejar uma feature ................................... /plan-work
Quero escrever UMA tarefa do plano ........................... /implement-task
Quero conferir o que foi entregue ............................ /review-change
Finding da revisão sobre a tarefa recém-entregue ............. /implement-task (mesma tarefa)
Quero tudo isso de uma vez, commitando, eu por perto ......... /deliver-scope
Quero tudo isso sem ser perguntado (volto depois) ............ /siegard-goal --arm
Quero que o Siegard decida nos stops por mim ................. /siegard-grant
Um bug em código já entregue, que nenhum critério cobria ..... /plan-work (corrective)
Um arquivo foi mexido na mão ................................. /siegard-status → /reconcile pronto
Só um label/cor/espaçamento num target edits_freely .......... edite direto (sem skill)
Remover um comentário proibido (comportamento já certo) ...... edite (só remover) → /reconcile
Ler arquivos mexidos contra o standard ....................... /check-source
Código antigo que quero trazer para o Siegard ................ /survey → /analyse → /reconcile (ou /adopt-scope)
Como estamos? ................................................ /siegard-status
Tabela de uma iniciativa ..................................... /siegard-progress
Custo e fricção .............................................. /siegard-telemetry
Pedido vago .................................................. /clarify-request
Árvore pesada de coisa fechada ............................... /siegard-archive
Campo faltando no siegard.json ............................... /siegard-config
```

---

## 8. Quando algo para: como ler

- **Um stop lista tudo o que falta de uma vez.** Responda tudo numa mensagem só.
- **Uma refusal** cita o que o script recusou. Não tente contornar: resolva o que ela diz.
- **Árvore suja** é uma causa frequente de stop. Commite (ou descarte) o que é seu e rode de novo.
  Pendência que você não fez é trabalho de outra pessoa em andamento.
- **Campo ausente no `siegard.json`:** o relatório traz o `/siegard-config` pronto para colar.
- **Três perguntas são sempre suas** (nenhum modo automático decide por você): uma **contradição**
  entre escopo e specification, **duas leituras** da mesma evidência e o **valor de um achado**
  (a menos que, no goal, você tenha declarado antes a política `--correct contradicts`). Nessas
  três, o relatório não recomenda porta: diz o que decide cada lado.
- **Recomendação** vem sempre com a razão e o fato que a reverteria, e diz se é *derived* ou
  *judged*.

## 9. Limites que valem em tudo

- Nenhum agente tem shell: quem executa são as **skills**. Todo build e teste do seu projeto roda
  por `bin/run.py`, que captura a execução e recusa repetir um nome já usado.
- O Siegard **não compõe comandos nem autoriza pacotes**: tudo vem do **registry do seu projeto**
  (o standard que o `siegard.json` declara para o target). Aprovar um pacote ou step é esse
  registry ganhar a entrada: você edita o arquivo, ou pede com palavras que nomeiam o pacote/step,
  e a sessão grava essas palavras (via `ask.py`), escreve a entrada e commita só esse arquivo.
- Push, branch e reescrita de histórico **nunca** são de uma skill, de um goal ou de um grant.
- Commits das skills são **por pathspec**, um por invocação, e nunca levam um arquivo que a skill
  encontrou pendente.
