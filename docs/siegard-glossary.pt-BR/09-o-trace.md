> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Revisão (`/review-change`)](08-revisao.md) · Próximo: [Reconciliação (`/reconcile`)](10-reconciliacao.md)

## 9. O trace

### Trace e `siegard-trace.json`
**O que é.** O único vínculo **de longa duração** entre a especificação e o código. Para cada nó
vinculado, ele guarda o digest do nó e o(s) arquivo(s) que contêm o fato dele, cada um com o seu
digest.
**Por que existe.** Planos e registros de entrega existem para fazer o código ser escrito, e podem
ser arquivados depois. O trace fica: é ele que permite perguntar, anos depois e sem nenhum plano,
"este código ainda corresponde à especificação que seguiu?".
**Quem escreve.** Só o `trace.py`. **Nunca edite à mão** — o hook `hooks/bounds.py` do plugin
recusa uma escrita direta no `siegard-trace.json`, em qualquer estado da sessão.
**Onde fica.** No topo do git, ao lado do `siegard.json`. Os caminhos dentro dele são relativos a
essa pasta. Já os caminhos que se passam ao `trace.py` na linha de comando (e os que os registros
carregam) são relativos à **raiz de código do target**; o script converte.
**Validar.** `trace.py <target-root>` só lê e valida o arquivo: `trace sound: N binding(s), …`.
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
          "node_digest": "sha256:9e85d914…",
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

**Leitura do exemplo.** O primeiro vínculo diz: "o fato do nó `domain/troubleshooting/case` mora em
`case.ts`; quando isso foi registrado, o nó tinha o digest `9e85…` e o arquivo `dce3…`; o arquivo
foi carimbado contra esse mesmo texto do nó (`node_digest`); e uma reconciliação julgou esse par
(`judged: true`)". O segundo diz o mesmo para outra regra e
acrescenta que ela é **decidida por teste**: o arquivo `raise.spec.ts`, rodado pelo step `test`,
prova o fato (ver "Certificação e `decided_by: test`", §10).

### Binding (vínculo) e par nó-arquivo
Um **binding** é uma entrada do trace: *o fato deste nó mora nestes arquivos*. Um **par
nó-arquivo** é um nó mais **um** de seus arquivos; a maior parte da reconciliação raciocina par a
par. Há no máximo um binding por nó.
**`judged`.** Num arquivo, significa que o julgamento de uma reconciliação liberou aquele par
naquele digest. Ausente significa que o par foi carimbado por uma entrega (ou à mão) e ninguém o
releu desde então contra o nó. A preparação de uma revisão só deixa de rejulgar um par que tem
`judged` (§8, §10).
**`node_digest`.** Num arquivo, o digest do nó **contra o qual aquele arquivo foi carimbado** — o
texto do nó como o bind que nomeou o arquivo o leu. Existe porque um bind carimba só os arquivos
que o seu registro nomeia: um nó vinculado em dois targets e revinculado a partir de um deles
mantém os arquivos do outro no texto anterior, e esses arquivos continuam devendo uma leitura. O
`digest` do binding é o mais recente desses textos. Numa entrada gravada antes de o campo existir,
vale o `digest` do binding.
**`decided_by`, `step`, `proof`.** O que decide se o fato ainda vale quando um arquivo muda:
ausente ou `reading` (o padrão) = uma leitura de conformidade; `test` = um teste certificado, rodado
pelo `step` do registro, com os arquivos de `proof` fixados pelo digest.
**O que nunca é vinculado.** Um descritor de contexto (`domain/<contexto>/_context`): não carrega
fato operativo, então nenhum arquivo o contém. O `--bind` o recusa.

### Bind (vincular)
**O que é.** Escrever ou estender um binding. Normalmente é feito por uma skill a partir de um
registro:

```sh
trace.py --bind-record <target-root> <spec-root> <record>                    # a partir de um registro de implementação
trace.py --bind-record <target-root> <spec-root> <record> --workspace <dir>  # a partir de um registro de reconciliação
```

**Como funciona.** Lê o registro e vincula exatamente os nós que ele lista com `encoded_at`, nos
arquivos listados, e nada mais. Um erro de forma (um nó que a especificação não tem, um arquivo
que não existe) recusa o registro inteiro antes de gravar qualquer coisa. Um registro sem nenhum
`encoded_at` não é falha: simplesmente não há o que gravar.
**Registro de implementação: preso ao que as execuções viram.** O bind recusa um arquivo cujos
bytes não são os que alguma execução apontada pelo registro de implementação ou pelo registro de
prova da tarefa viu (§7). Assim, o que fica carimbado é o código que o build e a suíte de fato
rodaram.
**Registro de reconciliação.** Vincula par a par: os pares liberados entram, os demais ficam como
estavam, e o recibo nomeia o que não foi gravado (§10). Com `--workspace`, recusa tudo se um
arquivo ou nó mudou desde a preparação.
**União.** Por padrão, o bind **acrescenta** ao que o nó já tinha: um arquivo que um bind anterior
associou ao nó continua lá. Duas entregas que colocaram o mesmo nó em dois arquivos não desfazem
uma à outra.
**Forma crua.** `--bind <target-root> <spec-root> <node> <file> ...` vincula sem registro; imprime
um recibo dizendo que o julgamento por trás da entrada não está registrado em lugar nenhum
(`this binding rests on no record: …`). Nenhuma skill usa essa forma.

### Rebind (revincular)
**O que é.** Vincular um nó de novo para que os digests do trace batam com o que está em disco
agora. Acontece quando uma entrega recarimba os nós da sua tarefa ou quando uma reconciliação
libera um par.
**O problema central.** "Mudou sem rebind": alguém editou um arquivo e ninguém atualizou o trace.
Note que uma entrega recarimba **só os nós da própria tarefa**; se ela reescreveu um arquivo que
outros nós também reivindicam, esses outros ficam desatualizados, e o bind imprime um **recibo**
avisando (`this act leaves N binding(s) stale — …`), com a reconciliação como rota.

### `--replace`
Faz um bind **substituir a entrada inteira** do nó em vez de acrescentar — para quando um fato
realmente saiu de um arquivo. Atenção: substitui **a entrada toda**, não só os arquivos que a
chamada nomeia, e cada arquivo nomeado é recarimbado no conteúdo de agora. Todo caminho que deixa
de ser reivindicado é impresso num recibo. O `/reconcile` nunca passa essa flag. Para tirar **um
único par** que uma reconciliação leu `nowhere`, a forma certa é `--release … --node` (abaixo), que
não toca nos outros arquivos do nó.

### Recibo (receipt)
As linhas que um comando imprime sobre o que ele **não** fez ou descartou: nós não vinculados,
caminhos liberados, certificações liberadas, vínculos deixados desatualizados, drift retido por
`edits_freely`. Os recibos devem ir para o relatório: são o único lugar em que uma ação parcial diz
que foi parcial.

### Drift (divergência) e `--check`
**O que é.** **Drift** é qualquer divergência entre o que o trace afirma e o que está em disco
agora. O `--check` recalcula todos os digests e reporta o drift em quatro **classes**, porque cada
uma tem um remédio diferente:

| Classe | Significa | Resolvido por |
|---|---|---|
| `orphaned` (órfão) | O vínculo aponta para um nó que a especificação não contém mais. | `trace.py --prune` |
| `moved` (movido) | O texto do nó mudou desde o bind — ou um arquivo ficou carimbado contra um texto anterior do nó, que um bind posterior recarimbou só em outros arquivos. | `trace.py --carry` quando a mudança foi só de forma; senão `/reconcile` sobre os arquivos vinculados, ou uma entrega que implemente o nó (que recarimba só os arquivos que o seu registro nomeia) |
| `code` (código) | Um arquivo vinculado mudou (ou sumiu) sem rebind. | `/reconcile` sobre o arquivo; `--release` se ele sumiu |
| `proof` (prova) | O teste que decide um vínculo certificado mudou ou sumiu, ou o step que o roda não existe mais no registro. | uma nova certificação; até lá, o vínculo volta a ser decidido por leitura |

**Um trace, vários targets.** O trace é um arquivo só por topo do git, e todo target o lê — a
primeira linha do `--check` diz isso. Por isso o step de cada certificação é procurado no standard
**do target sob o qual o teste está**, e não no do target passado ao `--check`: o mesmo trace
relata o mesmo drift a partir de qualquer target.

**Exemplo de saída** (digests e descrições das classes abreviados):

```
$ trace.py --check backend
trace: /repo/siegard-trace.json — one file per git toplevel; every target under it reads this same one
constraints/asynchronous-events: no longer in the specification; the binding is stale
domain/troubleshooting/case-status: bound at sha256:551f…, now sha256:bb1b…; the specification moved since this bind
backend/src/orders/place.ts: the file changed without a rebind — 2 binding(s): constraints/asynchronous-events, domain/troubleshooting/case

4 drift finding(s) on 3 of 3 binding(s), 3 node–file pair(s):
  1 orphaned over 1 binding(s): bound to a node the specification no longer holds — …
  1 moved over 1 binding(s): bound to a node whose text moved since the bind, … `/reconcile` over the bound files …
  0 proof: decided by a test whose text changed since it was certified — …
  2 code over 1 file(s), 2 binding(s): bound to a file that changed or is gone; `/reconcile` over the files …
```

**Leitura.** Linha 2: o nó `asynchronous-events` foi removido da especificação (órfão). Linha 3: o
texto de `case-status` mudou desde o bind (movido). Linha 4: `place.ts` foi editado sem rebind
(código), e isso atinge os dois vínculos que o nomeiam. A tabela final conta achados, vínculos e
pares, e a linha de `code` diz **sobre quantos arquivos**: dois achados aqui são **um** ato, uma
reconciliação sobre um arquivo.
**Como cada classe é listada.**
- `code` é listado **por arquivo**, porque o remédio (uma reconciliação) é invocado sobre um
  conjunto de arquivos. Um arquivo que sumiu aparece como `the file no longer exists — --release is
  what answers a deleted file`.
- O `moved` por arquivo (arquivo carimbado contra um texto anterior) é dobrado **por nó** — uma
  edição de um nó vinculado a quarenta arquivos é uma leitura devida — e o `--all` lista os
  arquivos.
- Se git registra que o nó órfão foi **renomeado**, a linha do órfão diz para onde ele foi.
- Achados `code` sobre pares que um step do registro ou um teste certificado decide ganham uma
  linha própria dizendo isso: são respondidos por uma execução, não por um juiz (§10).

**Código de saída.** `0` = nenhum drift; `1` = há drift. Um CI pode rodar isso a cada commit, mas
`moved` é o estado normal entre uma mudança na especificação e a entrega que a responde; leia as
classes, não só o código de saída.
**`edits_freely`.** Os achados `code` sob um target que o `siegard.json` declara em
`edits_freely` (§4) saem da listagem — nunca da leitura: um recibo diz quantos foram suprimidos
(`suppressed N `code` finding(s) …`), e o `--all` os lista.
**Não é um finding.** Drift não diz que o código está errado — um arquivo editado pode estar
perfeito. Diz apenas que o vínculo não descreve mais o que está em disco.

### `--check --reconcile-set` — o conjunto pronto para o `/reconcile`
**O que é.** O mesmo `--check`, seguido do **conjunto de arquivos** que uma invocação do
`/reconcile` sobre o target deve ler, já escrito a partir da raiz de código do target, com um
**slug livre** sugerido.
**Por que existe.** O `code` é listado por arquivo e o `moved` por nó; montar o conjunto à mão a
partir das duas listas erra de jeitos que nada pega (arquivo de outro target, caminho escrito a
partir do topo do git, nó com texto ainda não commitado).
**O que ele separa à parte, com o motivo.**
- **`retained`** — arquivos vinculados a um nó cujo arquivo na especificação não está commitado: um
  bind carimbaria um texto que o próximo checkout pode apagar.
- **`left to a delivery`** — arquivos de um nó movido que uma tarefa viva, ainda não entregue,
  implementa: a entrega dela já revincula o nó.
- **Teste certificado que mudou** — respondido por uma nova certificação, não por leitura.
- Arquivos com drift `code` suprimido por `edits_freely` — o `/check-source` é quem os lê.

```
reconcile set over target backend (backend), spelled from the target source root — one /reconcile invocation reads it whole:
  src/orders/place.ts  (code)
  1 file(s)
  free slug: reconcile-20261117-backend
```

O `/siegard-status` (§12) usa essa saída para entregar a invocação do `/reconcile` pronta.

### Recibo de drift no início da sessão
Num projeto que declara `siegard.json`, o hook `SessionStart` do plugin (`hooks/drift.py`) conta o
drift do trace e coloca na sessão **só a contagem** por classe (`N drift finding(s) — 1 moved, 2
code`), quantos arquivos têm drift `code` e quantos nós um teste finito poderia decidir (contagem do
`--owed`). É uma contagem, não uma parada: nada ali é devido antes de outro trabalho, e a listagem
continua sendo do `--check` e do `/siegard-status`.

### `--prune`
Remove **só** os vínculos da classe `orphaned` — depois que um `/analyse` removeu nós. Se o git
registra que o arquivo do nó foi **renomeado** para um nó que existe, o `--prune` segue a
renomeação (reescreve o vínculo com a nova identidade, mantendo arquivos e digest) em vez de
remover; uma cadeia de renomeações é seguida até o fim. Nunca use para silenciar drift `code` ou
`moved`: isso apagaria o único registro de a qual nó aquele código responde.

### `--release`
Remove um arquivo **que a árvore não tem mais** de todo vínculo que o nomeia. Recusa um arquivo que
ainda existe (esse é reconciliado, nunca liberado) e recusa a chamada inteira se um dos caminhos
ainda existir.

```sh
trace.py --release <target-root> src/legacy/old-handler.ts
```

**`--release <arquivo> … --node <nó>`.** A outra forma: tira **só aqueles arquivos do vínculo de
um nó**, para um par que uma reconciliação leu `nowhere` com o arquivo ainda na árvore. Os demais
arquivos do nó ficam com o carimbo que tinham. Recusa a chamada inteira se um par não é do nó ou se
nenhum registro o lê `nowhere`. Normalmente o próprio bind de uma reconciliação faz essa liberação
quando uma segunda leitura confirma o `nowhere`; quando não pode, o recibo entrega esta invocação
pronta, e a decisão é da pessoa (§10).

### `--carry` — mudança só de forma no nó
**O que é.** Responde ao drift `moved` que nenhuma leitura precisa responder: um nó cujo texto mudou
**só na forma** (ordem de chaves, aspas, quebra de linha) e não no que obriga.
**Como funciona.** Para cada arquivo de cada vínculo, recupera do git o texto do nó contra o qual o
arquivo foi carimbado e compara a sua **leitura** com a do nó de agora. Onde são iguais, o par é
recarimbado no nó atual. Um par fica como estava, com o motivo numa linha própria, quando o git não
tem o texto carimbado, a leitura mudou, há finding aberto contra o par, ou um plano vivo fixa o nó
no digest anterior.

```
$ trace.py --carry backend
left domain/troubleshooting/case-status backend/src/orders/status.ts: the node's reading changed, not its form alone

0 pair(s) carried over 0 node(s) at /repo/siegard-trace.json; 1 left as they stood.
```

**O que não é.** Um par carregado não é uma leitura: não libera nem fecha nenhum finding, e o
digest do arquivo, o `judged`, o `decided_by` e a prova ficam intactos. O `/reconcile` roda o
`--carry` antes do `--check` (§10). `--node <nó>` restringe a nós nomeados.

### `--encodes`
Responde à pergunta inversa: **quais nós cada arquivo tem vinculados** — inclusive para arquivos
que não tiveram drift, que o `--check` não mostraria.

```
$ trace.py --encodes backend src/orders/place.ts
backend/src/orders/place.ts: 2 binding(s)
  constraints/asynchronous-events — stale: the file changed without a rebind
  domain/troubleshooting/case — stale: the file changed without a rebind
```

- `--encodes --changed <target-root> [<ref>]` — o mesmo, sobre os arquivos que o git diz terem
  mudado (contra `HEAD`, incluindo não rastreados, ou desde `<ref>`).
- `--encodes --rank <target-root> [--all]` — as **contagens de acúmulo**: arquivos ordenados por
  quantos vínculos carregam, e nós ordenados por quantos arquivos têm. Um arquivo com muitos
  vínculos é candidato natural a uma auditoria (§10). A contagem distingue vínculos decididos por
  leitura dos decididos por um step ou um teste.

### `--untraced` e os cinco estados de arquivo
Lista todo arquivo rastreado pelo git sob um target que nenhum vínculo nomeia. Cada arquivo está
em exatamente um estado (no primeiro da lista que o descreve):

| Estado | Significado |
|---|---|
| **bound** (vinculado) | Algum vínculo o nomeia — como arquivo que codifica o fato ou como a prova que uma certificação fixou. |
| **holds-nothing** (não contém nada) | Uma adoção o julgou e não vinculou nenhum candidato a ele. |
| **outside** (fora) | Uma adoção o deixou deliberadamente fora do julgamento (configuração, fiação). |
| **uncertified** (não certificado) | Está no escopo de testes que o target declara em `tests` (§4), e nenhuma certificação o nomeia. Só aparece quando o target declara os seus testes. |
| **unsurveyed** (não levantado) | Nenhum dos anteriores: ninguém olhou para ele ainda. |

```
$ trace.py --untraced backend
5 tracked file(s) under backend: 2 bound (1 as a certification's proof), 3 no binding names
  0 holds-nothing: judged by an adoption, which bound none of its candidates to it
  0 outside: kept outside an adoption's judgment
  2 uncertified: in the target's declared test scope, and no certification names it
  1 unsurveyed: no binding and no adoption names it
```

**Submódulos.** O git rastreia um submódulo como uma única entrada, e ela também entra na
contagem. Como um submódulo não contém nada deste repositório, `outside` é o único estado para o
qual uma adoção pode movê-lo: o `--stage --adopt --outside` o aceita, e o `--area` nunca o entrega
a um levantamento.

Não recusa nada: a maioria dos arquivos de um sistema real não contém fato de negócio e nunca será
vinculada. O número é um fato sobre a árvore, não uma meta. `--all` lista todos os arquivos.

### `--convergence` e os cinco estados de nó
Classifica todo nó da especificação em exatamente um estado, considerando o trace e todas as
iniciativas (inclusive as que o `/siegard-archive` já removeu, lidas do git):

| Estado | Significado |
|---|---|
| `current` (atual) | Vinculado, e todo digest ainda bate. |
| `stale` (defasado) | Vinculado, e algum vínculo teve drift. |
| `planned-unbound` (planejado, não vinculado) | Uma tarefa o implementa ou um épico o cobre, mas nada o vincula ainda. |
| `declared-uncovered` (declarado não coberto) | Um épico o examinou e escreveu por que não está sendo construído. |
| `unreached` (não alcançado) | Nenhuma iniciativa o nomeia e nada o vincula. |

```sh
trace.py --convergence <target-root> <spec-root> <work-root> [--all]
```

`<work-root>` é o `work_root` do projeto, onde ficam as iniciativas. Além dos cinco estados (cada um
com a contagem por classe de nó), a saída diz quantos arquivos do target estão vinculados, quantos
nós vinculados nenhuma iniciativa nomeia (vinculados por uma reconciliação ou por um `--bind` cru)
e, **à parte**, o lado julgado: os findings que as reconciliações deixaram abertos, os fatos
`unstated`, os `restates` e as sobras testáveis — os mesmos números do `--owed` (§10). Um vínculo
que bate é um fato sobre bytes; um registro que achou algo contra um nó é um fato sobre uma
leitura; por isso os dois lados não se misturam.

É uma consulta: saída sempre `0`, sem nota. Uma pasta de trabalho que não existe (situação comum
num projeto adotado) é lida como "nenhuma iniciativa".

### As outras formas do `trace.py`
O `trace.py` também é o script da reconciliação e da adoção. Essas formas são explicadas nos
capítulos de quem as usa:

| Forma | Para quê | Onde |
|---|---|---|
| `--stage`, `--save-return(s)`, `--fold`, `--reconciliation`, `--stage-release` | preparar, salvar, dobrar e validar uma reconciliação | §10 |
| `--owed [--all] [--plan <work-root>]` | o que as reconciliações acharam e nenhum bind fechou | §10 |
| `--area`, `--survey`, `--ledger` | áreas de um levantamento, validação do material e do ledger (que termina com `ledger: keep` ou `ledger: remove`) | §11 |

Não confundir com `deliver.py --unrecorded`, que confere se todo caminho alterado por uma entrega
está nomeado num registro dela (§7): é do `deliver.py`, não do trace.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Revisão (`/review-change`)](08-revisao.md) · Próximo: [Reconciliação (`/reconcile`)](10-reconciliacao.md)
