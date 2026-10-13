> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Como ler este glossário](00-como-ler-este-glossario.md) · Próximo: [O panorama: que problema o Siegard resolve](02-o-panorama-que-problema-o-siegard.md)

## 1. Conceitos prévios

O Siegard é construído sobre algumas ferramentas e ideias que ele pressupõe conhecidas. Esta
seção as resume, para que o restante do texto não dependa de nenhum conhecimento externo.

### Claude Code
**O que é.** Um assistente de programação da Anthropic que roda no terminal (e em IDEs), capaz de
ler e escrever arquivos e executar comandos a pedido de uma pessoa. O Siegard é um **plugin** do
Claude Code: um pacote que acrescenta ao assistente novas skills, agentes, scripts e regras.

### Sessão
Uma conversa contínua entre a pessoa e o Claude Code. Tudo o que é dito numa sessão fica no
**contexto** dela (a "memória de trabalho" do modelo). O Siegard trata a conversa como **não
confiável como registro**: o que importa é o que foi gravado em disco. Uma informação que existe
apenas na conversa "não aconteceu" para o framework.

### Skill (e "entry point", ponto de entrada)
**O que é.** Um procedimento documentado que o Claude Code executa quando a pessoa digita
`/<nome>` (por exemplo `/analyse` ou `/reconcile`). Cada skill tem um arquivo `SKILL.md` que
descreve, passo a passo, o que deve ser feito, o que é proibido e quando parar.
**Por que importa.** No Siegard, cada tipo de mudança tem **uma** skill responsável — o seu ponto
de entrada. Fazer o trabalho de uma skill "à mão", sem invocá-la, é contornar as garantias que ela
oferece.

### Agente (subagente) e delegação
**O que é.** Um agente é uma instância separada do modelo, iniciada por uma skill, com um arquivo
de instruções próprio (em `agents/`) e um **contexto limpo** — isto é, sem nada da conversa que o
criou. **Delegar** é iniciar um agente e entregar a ele uma tarefa delimitada. O agente devolve uma
resposta (o **retorno**) e termina.
**Por que existe.** O Siegard usa agentes para garantir que **quem julga não é quem produziu**. Um
contexto que escreveu um código tende a considerá-lo correto; um contexto novo, que só recebe o
código e a regra, não tem esse viés. Ver "a regra do juiz separado" na §2.
**Como se espera um agente.** Um agente disparado roda em segundo plano, e o ambiente entrega uma
**notificação** quando ele responde. A sessão espera essa notificação e nada mais: nunca um
`sleep`, um despertar agendado, uma listagem de agentes ou uma mensagem ao agente perguntando se
já terminou. Cada uma dessas esperas é um turno pago para ler nada. Desde a 5.11.0 as skills que
delegam (`/review-change`, `/reconcile`, `/survey`, `/plan-work` e `/implement-task`) dizem isso
por escrito.
**Nome completo.** Os agentes são sempre chamados pelo nome com escopo do plugin, como
`siegard:specification-conformance-reviewer`. O nome sem prefixo poderia ser "sombreado" por um
agente homônimo que o próprio projeto tenha criado.

### Script
Um programa Python em `bin/` (`spec.py`, `plan.py`, `deliver.py`, `trace.py`, `run.py`,
`project.py`, `telemetry.py`, `clarify.py`). Os scripts fazem tudo o que é **mecanicamente decidível**:
validar arquivos, calcular digests, comparar, recusar. Nenhum script "opina". A regra geral é:
**o que um script pode decidir, um script decide; um agente só é usado quando é preciso
julgamento.**

### Hook
Um gatilho do Claude Code que executa algo automaticamente em certos momentos (por exemplo, no
início de cada sessão ou de cada subagente). O Siegard usa hooks para injetar suas regras de
sessão (`hooks/rules.md`, ver §4) em toda sessão e em todo agente de um projeto Siegard, sem que
ninguém precise lembrar de carregá-las.

### Schema (contrato)
**O que é.** Um arquivo JSON Schema em `schemas/` que define exatamente quais campos um arquivo
pode e deve ter, com quais tipos e valores. É o **contrato** daquele tipo de arquivo.
**Por que importa.** Os scripts validam cada arquivo contra o seu schema. Um arquivo fora do
contrato é recusado. Por isso as skills dizem "leia o contrato; não trabalhe de memória": o que
você lembra não é o que o validador aplica.

### Git: o mínimo necessário
O Siegard depende do git para quase tudo. Os termos que aparecem neste glossário:

| Termo | Significado |
|---|---|
| **repositório** | A pasta versionada pelo git, com todo o histórico. |
| **commit** | Uma fotografia registrada dos arquivos. "Commitado" = gravado no histórico. |
| **árvore de trabalho (working tree)** | Os arquivos como estão agora no disco. |
| **árvore limpa** | Nenhuma alteração pendente (não commitada). `git status --porcelain` não imprime nada. |
| **pathspec** | Uma lista de caminhos que restringe um comando git a esses caminhos. |
| **topo do git (git toplevel)** | A pasta raiz do repositório (`git rev-parse --show-toplevel`). |
| **diff** | A diferença entre duas versões. No Siegard, **"o diff é a revisão"**: uma pessoa revisa o que uma skill fez lendo o `git diff`. |
| **worktree** | Uma segunda cópia de trabalho do mesmo repositório, em outra pasta, útil para trabalhar em paralelo. |
| **HEAD** | O commit em que a árvore de trabalho está baseada no momento. |

**Por que a árvore precisa estar limpa.** Quase toda skill começa verificando que as pastas que
ela vai escrever estão sem alterações pendentes. O motivo: se a árvore começa limpa, o `git diff`
ao final mostra **exatamente** o que a skill fez, e nada mais. Se já houvesse alterações, seria
impossível separar o trabalho da skill do trabalho de outra pessoa.

### YAML e frontmatter
**YAML** é um formato de texto para dados estruturados (listas e chaves com valores), legível por
pessoas. **Frontmatter** é um bloco YAML no topo de um arquivo markdown, delimitado por linhas
`---`. Quase todo arquivo do Siegard é um markdown com frontmatter: o frontmatter carrega os dados
que os scripts validam, e o corpo carrega texto explicativo.

```markdown
---
statement: A hypothesis MUST hold at least one piece of evidence.
constrains:
  - domain/troubleshooting/hypothesis
---

## Description

No case resolves on an unsupported explanation.
```

**Block scalar (`|-`).** Uma forma de escrever um texto longo em YAML, em várias linhas, sem que um
caractere especial (como dois-pontos) quebre o arquivo. O Siegard pede essa forma para textos
livres nos retornos dos agentes.

### Hash, SHA-256, digest
**O que é.** Um **hash** é um número calculado a partir do conteúdo exato de um arquivo. O
**SHA-256** é um algoritmo de hash. O resultado, escrito `sha256:<64 caracteres hexadecimais>`, é
o **digest** do arquivo.
**A propriedade que importa.** Se um único byte do arquivo mudar, o digest muda completamente. Se
o arquivo não mudar, o digest é sempre o mesmo. Por isso o digest funciona como uma **impressão
digital**: comparar o digest guardado com o digest atual responde "este arquivo mudou desde
então?" sem precisar guardar uma cópia do arquivo.
**Como calcular à mão.** `sha256sum <arquivo>` imprime o mesmo valor que o Siegard usa.

### Slug e kebab-case
Um **slug** é um nome curto, só com letras minúsculas, números e hífens, como
`hand-fix-invoicing`. Essa grafia chama-se **kebab-case**. O Siegard usa slugs para nomear
iniciativas, execuções, reconciliações, levantamentos e arquivos de nós.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Como ler este glossário](00-como-ler-este-glossario.md) · Próximo: [O panorama: que problema o Siegard resolve](02-o-panorama-que-problema-o-siegard.md)
