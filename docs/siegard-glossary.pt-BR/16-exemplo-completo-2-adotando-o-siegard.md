> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md) · Próximo: [Perguntas frequentes](17-perguntas-frequentes.md)

## 16. Exemplo completo 2: adotando o Siegard num sistema existente

**A situação.** Um projeto tem um backend de pedidos escrito antes do Siegard. O `siegard.json` já
foi criado com `/siegard:siegard-config`, com o target `backend` e, antes de qualquer survey, os
testes do target declarados em `tests` (por exemplo, `under: tests`, `suffix: .spec.ts`). A
especificação está vazia e não há trace.

*Este exemplo é ilustrativo: os números, as áreas e a redação das invocações foram escolhidos para
a explicação, e não copiados de uma execução real. A forma de cada saída é a que os scripts da
versão 5.124.1 imprimem; "…" marca um trecho omitido.*

**1. Ponto de partida.** Medir e separar a árvore:

```
$ trace.py --untraced backend
120 tracked file(s) under backend: 0 bound, 120 no binding names — no trace file at …/siegard-trace.json, so nothing has been bound yet
  0 holds-nothing: judged by an adoption, which bound none of its candidates to it
  0 outside: kept outside an adoption's judgment
  14 uncertified: in the target's declared test scope, and no certification names it
  106 unsurveyed: no binding and no adoption names it

directories by unsurveyed files:
  …
```

Antes de uma adoção, todo arquivo é `unsurveyed`, menos os testes declarados, que são
`uncertified` (§11). A pessoa decide o lugar de cada um antes do primeiro survey: fonte de um
contexto, ou fora — configuração, fiação, um submódulo —, nomeado na adoção do contexto vizinho.

**2. Levantamento.** A pessoa começa pelo contexto de pedidos e divide o código em duas áreas:

```
/siegard:survey  project root: .  target: backend  slug: orders  areas: placement = src/orders/place/, billing = src/billing/
```

A skill confere que todo arquivo das áreas está commitado, roda `spec.py --digest` (o "contexto
até aqui"; vazio no primeiro survey), guarda a linha do `--untraced` e roda `trace.py --area` por
área — a lista de arquivos de cada área é a do script, e os testes declarados ficam de fora e são
nomeados:

```
$ trace.py --area backend src/billing/
4 file(s) in the area under backend
  …
```

Depois dispara dois `siegard:domain-surveyor` (§13), um por área, em ondas de no máximo vinte, e
salva cada retorno literalmente em `siegard-survey/orders/placement.md` e
`siegard-survey/orders/billing.md` (contrato `schemas/survey.json`). O surveyor lê o código, nunca a
documentação nem os comentários. `trace.py --survey` confere cada arquivo e conta as linhas de fato:

```
$ trace.py --survey siegard-survey/orders/placement.md siegard-survey/orders/billing.md
siegard-survey/orders/placement.md: 48 fact line(s) over 6 file(s) — Facts 30, Answers 12, Vocabularies 4, Upstream artifacts 2
siegard-survey/orders/billing.md: 31 fact line(s) over 4 file(s) — Facts 22, Answers 6, Vocabularies 3, Upstream artifacts 0
```

O relatório repete essas contagens, junta os comportamentos que discordam (anotados em
`## Observed and not decided here`) e os arquivos abertos fora da área (`read_outside_area`), e
termina com a invocação do `/analyse` pronta. O `/survey` **não commita**: o commit do material é
da pessoa (ou do `/adopt-scope`, quando ele conduz a rota).

**3. Análise.** A pessoa cola a invocação entregue:

```
/siegard:analyse  project root: .  material: siegard-survey/orders/placement.md, siegard-survey/orders/billing.md
```

O `/analyse` escreve os nós (contexto `orders`, agregado `order`, regras, contratos), registra cada
valor que decidiu no log ao lado do nó (`<nó>.log.md`, escrito por `spec.py --decide`), e escreve
`siegard-survey/orders/ledger.md`, com uma entrada por linha de fato: um nó, ou `outside` com o
motivo, ou `open` com o que falta responder. `trace.py --ledger` confirma que nenhuma linha ficou
sem destino e imprime os candidatos por arquivo:

```
$ trace.py --ledger siegard-survey/orders/ledger.md specification
ledger sound: 79 fact line(s) over 2 material file(s) — 71 landed in 18 node(s), 8 left out with a reason, 0 open
  …
  file set: 10 file(s) the material read; candidates per file:
    …
ledger: keep — an adoption reads it; the commit takes the ledger, and the adoption's commit removes it
```

A última linha diz o destino do ledger: ele vive enquanto o material está em uso. O `/analyse`
commita a raiz da especificação e o ledger juntos, com pathspec (`analyse <slug, ou o nome do
material>: analyse`), e o commit da adoção o remove. O relatório termina com a invocação do `/reconcile` como adoção sobre o ledger, antes da
do `/plan-work` e no lugar dela como próximo passo, com um espaço para o slug e outro para os
arquivos que a pessoa deixa fora do julgamento. Uma linha ainda `open` impede a adoção: o ledger
precisa estar fechado.

**4. Adoção.**

```
/siegard:reconcile  adoption  ledger: siegard-survey/orders/ledger.md  project root: .  slug: adopt-orders  outside: src/orders/config.ts
```

O stage (`--adopt --ledger`) toma como conjunto de arquivos as áreas do material e monta um pacote
por arquivo com os candidatos que os fatos *daquele* arquivo alcançaram, não o incremento inteiro;
um arquivo que nenhum fato nomeia não recebe juiz. Não precisa de trace para começar:

```
$ trace.py --stage backend specification adopt-orders <workspace> --adopt --ledger siegard-survey/orders/ledger.md --outside src/orders/config.ts
staged adopt-orders: 10 file(s) to judge over 0 node(s); staged as an adoption — 18 candidate node(s) from the ledger, … each bound by the fold to the files that hold its fact; 1 file(s) kept outside the judgment; …
  …
    wave 1: 10 — …
```

Os juízes (`siegard:specification-conformance-reviewer`, um por arquivo) leem; o fold escreve
`adopted: true`, vincula cada candidato liberado aos arquivos onde o juiz encontrou o fato, e lista
em `unheld` os candidatos que nenhum juiz encontrou. O bind **cria** o `siegard-trace.json`. Testes
que a pessoa sabe que provam um nó podem ser oferecidos na mesma rodada como certificações
(`certifications`, julgadas pelo `siegard:coverage-auditor`). A skill commita como `reconcile
adopt-orders` — o trace, `siegard-reconcile/adopt-orders.*` e a remoção do ledger.

**5. O que volta.** Nada disso para a adoção; tudo vai no relatório:
- candidatos `unheld`, findings `contradicts` e `unstated` → novo `/analyse`, depois nova
  reconciliação sobre os arquivos restantes;
- `restates` → remover **todos** os comentários do arquivo, não só o citado, e reconciliar o arquivo
  de novo;
- um comportamento que o negócio quer mudado → incremento corretivo do `/plan-work`, num pedido
  novo: a adoção não muda código.

**6. Progresso.** Depois do bind:

```
$ trace.py --untraced backend
120 tracked file(s) under backend: 10 bound, 110 no binding names
  0 holds-nothing: …
  1 outside: kept outside an adoption's judgment
  14 uncertified: …
  95 unsurveyed: no binding and no adoption names it
```

Cada arquivo está em exatamente um estado: `bound`, `holds-nothing`, `outside`, `uncertified` ou
`unsurveyed`. A adoção está completa quando nenhum arquivo estiver `unsurveyed` e o `--convergence`
não mostrar nó `unreached`; `/siegard:siegard-status` imprime os dois. Isso é medido, não é portão:
trabalho novo pode começar antes, e a primeira revisão que alcançar um arquivo `unsurveyed` paga
por ele.

**7. Depois da adoção do contexto.** A documentação do sistema entra como material de um
`/analyse` comum sobre a especificação adotada — nunca misturada ao primeiro material, que vem só
do código. O que ela corrigir aparece como drift. E, onde o target declara testes, o `/survey` na
forma `tests` lê os testes declarados (pelo `siegard:test-intent-reader`) e escreve *intent
material* (`schemas/intent.json`): o que o código *deveria* fazer, cada fato ao lado do teste onde
foi lido e do arquivo de código que ele governa. Segue a mesma rota: `/analyse` com ledger, e a
adoção sobre esse ledger julga cada arquivo governado — nunca os testes.

**Atalho.** Os passos 2 a 4 podem ser pedidos de uma vez ao `/siegard:adopt-scope`, com um pedido
nas palavras da pessoa dizendo que esse contexto deve ser adotado de ponta a ponta (citado
literalmente; sem isso, é parada), nomeando as áreas e o que fica fora. Ele invoca as três skills,
faz um commit por passo, com pathspec (`adopt-scope orders: survey`, `…: analyse`, `…: adopt`,
`…: measure` — este último com a medição de `telemetry.py --probe`), registra cada passo em
`siegard-survey/orders/orchestration.md` (que também permite retomar de onde parou), para nas
mesmas paradas das skills que invoca e relata todo o resto para revisão posterior. Nunca cria
branch, nunca faz push, e nunca chama `/plan-work`, `/implement-task`, `/review-change` nem
`/deliver-scope`. Um `/goal` cuja condição o nomeia e lê mecanicamente — `trace.py --untraced
<target>` imprimindo `0 unsurveyed` — leva um contexto após o outro.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md) · Próximo: [Perguntas frequentes](17-perguntas-frequentes.md)
