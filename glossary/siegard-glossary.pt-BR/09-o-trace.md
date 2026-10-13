> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Revisão (`/review-change`)](08-revisao.md) · Próximo: [Reconciliação (`/reconcile`)](10-reconciliacao.md)

## 9. O trace

### Trace e `siegard-trace.json`
**O que é.** O único vínculo **de longa duração** entre a especificação e o código. Para cada nó
vinculado, ele guarda o digest do nó e o(s) arquivo(s) que contêm o fato dele, cada um com o seu
digest.
**Por que existe.** Planos e registros de entrega existem para fazer o código ser escrito, e podem
ser arquivados depois. O trace fica: é ele que permite perguntar, anos depois e sem nenhum plano,
"este código ainda corresponde à especificação que seguiu?".
**Quem escreve.** Só o `trace.py`. **Nunca edite à mão.**
**Onde fica.** No topo do git, ao lado do `siegard.json`. Os caminhos dentro dele são relativos a
essa pasta.
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
prova o fato.

### Binding (vínculo) e par nó-arquivo
Um **binding** é uma entrada do trace: *o fato deste nó mora nestes arquivos*. Um **par
nó-arquivo** é um nó mais **um** de seus arquivos; a maior parte da reconciliação raciocina par a
par.
**`judged`.** Num arquivo, significa que o julgamento de uma reconciliação liberou aquele par
naquele digest. Ausente significa que o par foi carimbado por uma entrega (ou à mão) e ninguém o
releu desde então contra o nó.
**`node_digest`.** Num arquivo, o digest do nó **contra o qual aquele arquivo foi carimbado** — o
texto do nó como o bind que nomeou o arquivo o leu. Existe porque um bind carimba só os arquivos
que o seu registro nomeia: um nó vinculado em dois targets e revinculado a partir de um deles
mantém os arquivos do outro no texto anterior, e esses arquivos continuam devendo uma leitura. O
`digest` do binding é o mais recente desses textos. Numa entrada gravada antes de o campo existir,
vale o `digest` do binding, que era o que o arquivo de fato tinha.

### Bind (vincular)
**O que é.** Escrever ou estender um binding. Normalmente é feito por uma skill a partir de um
registro:

```sh
trace.py --bind-record <target-root> <spec-root> <record>                    # a partir de um registro de implementação
trace.py --bind-record <target-root> <spec-root> <record> --workspace <dir>  # a partir de um registro de reconciliação
```

**Como funciona.** Lê o registro e vincula exatamente os nós que ele lista com `encoded_at`, nos
arquivos listados, e nada mais. O registro inteiro é um único ato: se um nó ou arquivo não existe,
nada é gravado.
**União.** Por padrão, o bind **acrescenta** ao que o nó já tinha: um arquivo que um bind anterior
associou ao nó continua lá. Duas entregas que colocaram o mesmo nó em dois arquivos não desfazem
uma à outra.
**Forma crua.** `--bind <target-root> <spec-root> <node> <file> ...` vincula sem registro; imprime
um aviso de que o julgamento por trás da entrada não está registrado em lugar nenhum.

### Rebind (revincular)
**O que é.** Vincular um nó de novo para que os digests do trace batam com o que está em disco
agora. Acontece quando uma entrega recarimba os nós da sua tarefa ou quando uma reconciliação
libera um par.
**O problema central.** "Mudou sem rebind": alguém editou um arquivo e ninguém atualizou o trace.
Note que uma entrega recarimba **só os nós da própria tarefa**; se ela reescreveu um arquivo que
outros nós também reivindicam, esses outros ficam desatualizados, e o bind imprime um **recibo**
avisando.

### `--replace`
Faz um bind **substituir a entrada inteira** do nó em vez de acrescentar — para quando um fato
realmente saiu de um arquivo. Todo caminho que deixa de ser reivindicado é impresso num recibo. O
`/reconcile` nunca passa essa flag: ele entrega o comando pronto para a pessoa rodar, porque um
recibo que ninguém lê é uma perda silenciosa.

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
| `moved` (movido) | O texto do nó mudou desde o bind — ou um arquivo ficou carimbado contra um texto anterior do nó, que um bind posterior recarimbou só em outros arquivos (aí a linha é **por arquivo**). | `/reconcile` sobre os arquivos vinculados, ou uma entrega que implemente o nó |
| `code` (código) | Um arquivo vinculado mudou (ou sumiu) sem rebind. | `/reconcile` sobre o arquivo; `--release` se ele sumiu |
| `proof` (prova) | O teste que decide um vínculo certificado mudou. | uma nova certificação; até lá, o vínculo volta a ser decidido por leitura |

**Um trace, vários targets.** O trace é um arquivo só por topo do git, e todo target o lê. Por isso
o step de cada certificação é procurado no standard **do target sob o qual o teste está**, e não no
do target passado ao `--check`: o mesmo trace relata o mesmo drift a partir de qualquer target.

**Exemplo de saída (de uma fixture de teste):**

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

**Leitura.** Linha 1: o nó `gone-from-the-base` foi removido da especificação (órfão). Linha 2: o
texto de `evidence` mudou desde o bind (movido). Linha 3: `case.ts` foi editado sem rebind
(código). A classe `code` é listada **por arquivo**, porque o remédio (uma reconciliação) é
invocado sobre um conjunto de arquivos.
**Código de saída.** `0` = nenhum drift; `1` = há drift. Um CI pode rodar isso a cada commit.
`--all` também lista o drift retido por `edits_freely`.
**Não é um finding.** Drift não diz que o código está errado — um arquivo editado pode estar
perfeito. Diz apenas que o vínculo não descreve mais o que está em disco.

### `--prune`
Remove **só** os vínculos da classe `orphaned` — depois que um `/analyse` removeu nós. Se o git
registra que o arquivo do nó foi **renomeado** para um nó que existe, o `--prune` segue a
renomeação (reescreve o vínculo com a nova identidade) em vez de remover. Nunca use para silenciar
drift `code` ou `moved`: isso apagaria o único registro de a qual nó aquele código responde.

### `--release`
Remove um arquivo **que a árvore não tem mais** de todo vínculo que o nomeia. Recusa um arquivo que
ainda existe (esse é reconciliado, nunca liberado) e recusa a chamada inteira se um dos caminhos
ainda existir.

```sh
trace.py --release <target-root> src/legacy/old-handler.ts
```

### `--encodes`
Responde à pergunta inversa: **quais nós cada arquivo tem vinculados** — inclusive para arquivos
que não tiveram drift, que o `--check` não mostraria.

```
$ trace.py --encodes backend src/troubleshooting/case.ts
backend/src/troubleshooting/case.ts: 2 binding(s)
  domain/troubleshooting/case — stale: the file changed without a rebind
  domain/troubleshooting/gone-from-the-base — matches
```

- `--encodes --changed <target-root> [<ref>]` — o mesmo, sobre os arquivos que o git diz terem
  mudado (contra `HEAD`, ou desde `<ref>`).
- `--encodes --rank <target-root>` — as **contagens de acúmulo**: arquivos ordenados por quantos
  vínculos carregam, e nós ordenados por quantos arquivos têm. Um arquivo com muitos vínculos é
  candidato natural a uma auditoria.

### `--untraced` e os cinco estados de arquivo
Lista todo arquivo rastreado pelo git sob um target que nenhum vínculo nomeia. Cada arquivo está
em exatamente um estado:

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
vinculada. O número é um fato sobre a árvore, não uma meta.

### `--convergence` e os cinco estados de nó
Classifica todo nó da especificação em exatamente um estado, considerando o trace e todas as
iniciativas:

| Estado | Significado |
|---|---|
| `current` (atual) | Vinculado, e todo digest ainda bate. |
| `stale` (defasado) | Vinculado, e algum vínculo teve drift. |
| `planned-unbound` (planejado, não vinculado) | Uma tarefa o implementa ou um épico o cobre, mas nada o vincula ainda. |
| `declared-uncovered` (declarado não coberto) | Um épico o examinou e escreveu por que não está sendo construído. |
| `unreached` (não alcançado) | Nenhuma iniciativa o nomeia e nada o vincula. |

```sh
trace.py --convergence <target-root> <spec-root> <work-root-parent>
```

É uma consulta: saída sempre `0`, sem nota. Uma pasta de trabalho que não existe (situação comum
num projeto adotado) é lida como "nenhuma iniciativa".

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Revisão (`/review-change`)](08-revisao.md) · Próximo: [Reconciliação (`/reconcile`)](10-reconciliacao.md)
