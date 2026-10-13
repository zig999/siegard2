> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md) · Próximo: [Perguntas frequentes](17-perguntas-frequentes.md)

## 16. Exemplo completo 2: adotando o Siegard num sistema existente

**A situação.** Um projeto tem um backend de pedidos escrito antes do Siegard. O `siegard.json` já
foi criado com `/siegard-config`, com o target `backend`. Não há especificação nem trace.

*Este exemplo é ilustrativo: os números, as áreas e a redação das invocações foram escolhidos para
a explicação, e não copiados de uma execução real.*

**1. Ponto de partida.**

```
$ trace.py --untraced backend
120 tracked file(s) under backend: 0 bound, 120 no binding names
  ...
  120 unsurveyed: no binding and no adoption names it
```

**2. Levantamento.** A pessoa escolhe começar pelo contexto de pedidos e divide o código em duas
áreas:

```
/siegard:survey  project root: .  slug: orders  areas: placement = src/orders/place/, billing = src/billing/
```

A skill dispara dois `domain-surveyor`, salva `siegard-survey/orders/placement.md` e
`siegard-survey/orders/billing.md`, e roda `trace.py --survey` sobre eles. O relatório lista, por
exemplo, 48 linhas de fato em `placement` e 31 em `billing`, e dois comportamentos que discordam
(anotados em "Observed and not decided here").

**3. Análise.** A pessoa cola a invocação entregue:

```
/siegard:analyse  material: siegard-survey/orders/placement.md, siegard-survey/orders/billing.md  project root: .
```

O `/analyse` escreve os nós (contexto `orders`, agregado `order`, regras, contratos), registra no
log o que decidiu, e escreve `siegard-survey/orders/ledger.md`, com uma entrada por linha de fato.
`trace.py --ledger` confirma que nenhuma linha ficou sem destino e imprime os candidatos por
arquivo. O relatório termina com a invocação da adoção.

**4. Adoção.**

```
/siegard:reconcile  adoption  ledger: siegard-survey/orders/ledger.md  project root: .  slug: adopt-orders
```

O stage (`--adopt --ledger`) monta um pacote por arquivo com os candidatos daquele arquivo; os
juízes leem; o fold escreve `adopted`, vincula cada candidato liberado aos arquivos onde o juiz o
encontrou, e lista em `unheld` os candidatos que nenhum juiz encontrou. O bind **cria** o
`siegard-trace.json`.

**5. O que volta.** Candidatos `unheld`, `contradicts` e `unstated` → novo `/analyse`, depois nova
reconciliação sobre os arquivos restantes. `restates` → remover comentários e reconciliar.

**6. Progresso.** `trace.py --untraced backend` mostra os arquivos desse contexto como `bound`,
`holds-nothing` ou `outside`. Quando nenhum arquivo estiver `unsurveyed` e o `--convergence` não
mostrar nó `unreached`, a adoção está completa. Só então a documentação do sistema entra como
material de um `/analyse` comum.

**Atalho.** Os passos 2 a 4 podem ser pedidos de uma vez ao `/adopt-scope`, que faz um commit por
passo (`adopt-scope orders: survey`, `…: analyse`, `…: adopt`, `…: measure`) e para nas mesmas
paradas.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md) · Próximo: [Perguntas frequentes](17-perguntas-frequentes.md)
