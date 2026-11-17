> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md) · Próximo: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md)

## 15. Exemplo completo 1: uma correção feita à mão

**A situação.** Durante um incidente, alguém acrescentou uma guarda em `src/billing/raise.ts` para
que um pedido não pudesse ter duas faturas, e commitou. O comportamento está correto. O arquivo
estava vinculado, no trace, ao nó `rules/sales/invoice-immutable` (que diz que uma fatura emitida
não pode ser alterada — e nada diz sobre quantas faturas um pedido pode ter). O projeto tem um
único target, `backend`, e o `siegard.json` fica na raiz do repositório.

*As saídas de script abaixo foram obtidas rodando os scripts da versão 5.124.1 sobre uma cópia
mínima deste caso; "…" marca um trecho omitido. O retorno do juiz segue o exemplo do próprio
`schemas/conformance-return.json`, e o texto do handoff no passo 10 é ilustrativo: a prosa é
escrita pela sessão, só os rótulos fixos são do script.*

**1. Algo percebe a divergência.** Um CI roda o `--check`:

```
$ trace.py --check backend
trace: …/siegard-trace.json — one file per git toplevel; every target under it reads this same one
backend/src/billing/raise.ts: the file changed without a rebind — 1 binding(s): rules/sales/invoice-immutable

1 drift finding(s) on 1 of 1 binding(s), 1 node–file pair(s):
  0 orphaned: …
  0 moved: …
  0 proof: …
  1 code over 1 file(s), 1 binding(s): bound to a file that changed or is gone; `/reconcile` over the files re-reads a file that changed, and `--release` answers one the tree no longer holds
```

*O que isso diz:* o arquivo mudou, mas o trace ainda afirma o digest antigo (drift da classe
`code`, §9). Não diz se a mudança está certa ou errada.

**2. A pessoa invoca a rota.** Não precisa montar o conjunto de arquivos à mão:
`/siegard:siegard-status` roda `trace.py --check backend --reconcile-set`, que acrescenta ao
relatório acima o conjunto que um `/reconcile` lê e um slug livre:

```
reconcile set over target backend (backend), spelled from the target source root — one /reconcile invocation reads it whole:
  src/billing/raise.ts  (code)
  1 file(s)
  free slug: reconcile-20261117-backend
```

e entrega a invocação pronta. A pessoa pode trocar o slug por um nome que diga algo. O conjunto de
arquivos vai na grafia da raiz do target, sem o prefixo `backend/` (o stage recusa a outra grafia):

```
/siegard:reconcile  file set: src/billing/raise.ts   project root: .   slug: hand-fix-invoicing
```

Com um só target no `siegard.json`, a skill decide o target sozinha e diz isso no relatório. Sem
`project root`, a raiz é o toplevel git da sessão, como `project.py --here` a resolve (§12).

**3. Situate.** A skill roda `project.py`, que dá a raiz da especificação e a do target, e confere a
árvore: `git status --porcelain` sobre `src/billing/raise.ts` e a raiz da especificação não imprime
nada, `siegard-trace.json` está limpo e o target está sob git. Depois lê
`schemas/reconciliation.json`, confirma com `spec.py` que a especificação se sustenta, com
`trace.py backend` que o trace se sustenta (`trace sound: 1 binding(s), …`), e que
`siegard-reconcile/hand-fix-invoicing.md` não existe. Um slug já usado é parada, não sufixo.

**4. Stage.** A skill roda `trace.py --carry backend` (que aqui não carrega nada: o nó não mudou),
`trace.py --check backend`, e prepara um workspace novo (`mktemp -d`; aqui chamado `/tmp/ws`):

```
$ trace.py --stage backend specification hand-fix-invoicing /tmp/ws src/billing/raise.ts
staged hand-fix-invoicing: 1 file(s) to judge over 1 node(s); 0 pair(s) omittable — the binding is current and nothing is owed on them; 0 file(s) with nothing left to judge; 0 file(s) the trace binds nothing to
  manifest and packs at /tmp/ws; candidate index at /tmp/ws/candidates.txt
  save each subagent's return verbatim at …/siegard-reconcile/hand-fix-invoicing.returns/<file path with '/' as '__'>.yaml
  dispatch in 1 wave(s) of at most 20 subagent(s) — …
    wave 1: 1 — src/billing/raise.ts
```

*Resultado:* o workspace passa a conter `manifest.json` (dizendo que `raise.ts` tem um nó a julgar),
`packs/src__billing__raise.ts.md` (com o texto completo de `rules/sales/invoice-immutable`) e
`candidates.txt`. A pasta vazia `siegard-reconcile/hand-fix-invoicing.returns/` é criada. Nenhum
par foi omitido, porque o arquivo mudou; nada caiu no nível `mechanical`, porque nenhum step do
registry nem teste certificado decide esse nó.

**5. Julgar.** Um `siegard:specification-conformance-reviewer` (§13) recebe, como caminhos
absolutos, o arquivo, o pacote, o índice de candidatos, a raiz da especificação e o contrato
`schemas/conformance-return.json`. A sessão não lê o arquivo para decidir: quem julga é um contexto
que não aceitou a premissa de que o código está certo. Quando o juiz responde, a skill roda
`trace.py --save-returns backend /tmp/ws <pasta das transcrições>`, que copia o retorno literalmente
para `siegard-reconcile/hand-fix-invoicing.returns/src__billing__raise.ts.yaml`:

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here, so the next reader looks for it in the specification and does not find it
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule the file cites governs modification of a raised invoice; `if (order.invoices.length >= 1)` states a cap no node holds
```

*O que o juiz disse:* o fato do nó (imutabilidade de fatura emitida) não está neste arquivo
(`held_at: nowhere`), e o arquivo agora afirma uma regra ("no máximo uma fatura por pedido") que o
nó não contém — por isso o finding `contradicts` contra ele. O retorno só pode ter as cinco chaves
do contrato (`findings`, `read`, `nowhere`, `looked_past`, `candidates_opened`); uma sexta faz o
fold recusar.

**6. Capture.** Não houve nível `mechanical` nem reescrita declarada; o passo é pulado e isso é
dito no relatório.

**7. Fold.** A skill escreve a premissa, a única parte do registro que é da pessoa — inclusive
`said`, as palavras dela citadas literalmente, sem o qual o fold recusa:

```yaml
title: Hand correction to invoicing
summary: The nightly run raised two invoices for one order; the guard was added by hand during an incident and the behavior is correct.
said: "<o pedido da pessoa, palavra por palavra>"
target: backend
files:
  - path: src/billing/raise.ts
    change: refuses a second invoice for an order that already has one
```

e roda:

```
$ trace.py --fold backend /tmp/ws /tmp/ws/premise.yaml siegard-reconcile/hand-fix-invoicing.md
folded hand-fix-invoicing.md: 0 node(s) cleared, 1 not — 0 of those collateral, blocked only by an unattributed sibling finding — 0 pair(s) omitted as current and unowed
  next: trace.py --reconciliation siegard-reconcile/hand-fix-invoicing.md
```

O fold aplica as regras: há um finding que nomeia o nó → o nó não está conforme → `conforms:
false`, `observed_at: [src/billing/raise.ts]`, sem `encoded_at`. Em seguida, `--reconciliation`
confirma que o registro cumpre o contrato (`siegard-reconcile/11`):

```
hand-fix-invoicing.md holds: 1 file(s), 0 node(s) the judgment cleared, 1 it did not, 0 file(s) the trace binds nothing to.
--bind-record will write 0 binding(s) from this record and none for rules/sales/invoice-immutable: a node without `encoded_at` is a node this form cannot bind.
```

**8. Bind.** Primeiro a segunda leitura, nunca pulada: `trace.py --stage-release` prepara uma
segunda leitura cega de cada par que o registro leu `nowhere` e que o bind poderia soltar. Aqui o
nó tem um finding contra ele e nenhum outro arquivo, e não há o que preparar (`staged a second
reading of 0 pair(s) over 0 file(s) …`). Depois, uma vez:

```
$ trace.py --bind-record backend specification siegard-reconcile/hand-fix-invoicing.md --workspace /tmp/ws
nothing to bind: siegard-reconcile/hand-fix-invoicing.md names no node with `encoded_at`; a node the record answers only by `how` reached no file, and a bind with none is refused
```

O recibo diz exatamente isso: nada foi vinculado, porque o único nó não foi liberado.

**9. Commit.** A skill commita o que a própria invocação escreveu, e só isso, com pathspec: o
registro e a pasta de retornos em `siegard-reconcile/` (e o `siegard-trace.json`, se o bind o
tivesse mudado), na mensagem `reconcile hand-fix-invoicing`. Nunca um arquivo de código, um push ou
um branch.

**10. Relatório.** A skill roda `handoff.py --prepare --skill reconcile --project . --target backend
--language pt-BR`, que escreve o estado (uma linha de script, nunca da sessão) e marca as duas
portas, cada uma com o que a checagem respondeu:

```
"entry": "/analyse",   "check": {"answer": "not checked", "why": "no script decides what /analyse refuses; its own file states it"}
"entry": "/plan-work", "check": {"answer": "not checked", "why": "/plan-work takes a slug, and none was named"}
```

O relatório completo vai para o disco por `handoff.py --save-report`, e a pessoa recebe o que
`handoff.py --render` imprime. Como são duas leituras da mesma evidência, a decisão é da pessoa: o
handoff não recomenda porta nenhuma, diz o que cada uma supõe e o que decidiria (SPEC-006 R3). Algo
assim:

```
Nenhuma iniciativa em andamento neste projeto.

A guarda em raise.ts limita um pedido a uma fatura, e nenhuma regra da especificação diz isso. Qual dos dois está certo?
   **Decisão sua**: Se a guarda é o comportamento desejado, a especificação está atrasada; se não, o código está errado. …
   Escolha uma:
   - `especificar`: Registra na especificação que um pedido tem no máximo uma fatura; …
   - `corrigir`: Planeja uma correção do código para voltar ao que a especificação diz.
   Se nenhuma for tomada: O arquivo continua com a divergência registrada e nada foi vinculado.

Relatório completo: …/.git/siegard/handoff/<data>-reconcile.md
```

As duas portas, prontas para colar no relatório completo:
- **O código está certo, a especificação está atrasada** → `/siegard:analyse` com o finding como
  material (a evidência, o arquivo onde foi lida e o nó), para que um nó passe a dizer "um pedido tem
  no máximo uma fatura". O `/analyse` commita o próprio incremento e termina listando as
  identidades dos nós que escreveu, como lista de candidatos. Depois, `/reconcile` de novo sobre o
  mesmo arquivo, com slug novo, nomeando o nó novo:
  - numa reconciliação comum, um nó escrito depois do bind entra só como **candidato**
    (`trace.py --stage … --node <nó>`): o juiz pode atribuir a guarda a ele em vez de relatá-la como
    fato sem nó, mas ele não é vinculado — o fold anota `bound from nowhere here`;
  - para que o nó novo seja vinculado, a segunda invocação é uma **adoção** que o nomeia como
    candidato (`adoption`, candidates: o nó novo): cada candidato liberado é vinculado aos arquivos
    onde o juiz achou o fato, e o nó antigo, ainda em drift, é julgado de novo ao lado dele (§10, §11).
- **A especificação está certa, o código está errado** → incremento corretivo do `/plan-work`, na
  forma do seu `argument-hint`: `/siegard:plan-work . target backend slug <slug> — corrective: …`.
  Essa rota termina numa entrega, que faz o próprio bind.

**11. Depois.** `trace.py --owed backend` continua listando o finding até que algum registro libere
o par:

```
$ trace.py --owed backend
reported: the binding is stale, so `--check` already carries this one — the record is what says what was found
  backend/src/billing/raise.ts
    rules/sales/invoice-immutable — found against in hand-fix-invoicing.md

1 finding(s) no bind closed, over 1 file(s):
  0 unseen: …
  0 covered: …
  1 reported: the binding is stale, so `--check` already carries this one — the record is what says what was found
```

O `--check` continua mostrando o drift `code` de `raise.ts`, porque nada foi recarimbado.

**Variações:**
- **Se o único problema fosse um comentário** — por exemplo `// an order may only have one invoice`
  acima de um código que já impõe um nó de regra —, o juiz registraria `kind: restates`, o par
  seria vinculado normalmente onde o código está, e o relatório recomendaria a rota de comentários
  (uma recomendação *derived*, critério `rule violated`): remover **todos** os comentários do
  arquivo, não só o citado, commitar e rodar `/reconcile` sobre o arquivo com slug novo.
- **Se fosse uma mensagem de erro** que o sistema devolve dizendo a mesma coisa que o nó, não
  haveria finding nenhum: texto que o sistema emite é comportamento, e concorda com o nó.
- **Se o trace afirmasse um fato em vários arquivos** e só este o tivesse perdido, sem nada contra o
  nó, os arquivos que ainda o têm seriam recarimbados, e este só seria solto pelo bind se a segunda
  leitura do passo 8, cega à primeira, também o lesse `nowhere` (SPEC-005 R10); senão, o recibo
  entrega `trace.py --release … --node …` como decisão da pessoa.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md) · Próximo: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md)
