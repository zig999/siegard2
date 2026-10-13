> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md) · Próximo: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md)

## 15. Exemplo completo 1: uma correção feita à mão

**A situação.** Durante um incidente, alguém acrescentou uma guarda em `src/billing/raise.ts` para
que um pedido não pudesse ter duas faturas, e commitou. O comportamento está correto. O arquivo
estava vinculado, no trace, ao nó `rules/sales/invoice-immutable` (que diz que uma fatura emitida
não pode ser alterada — e nada diz sobre quantas faturas um pedido pode ter).

**1. Algo percebe a divergência.** Um CI roda o `--check`:

```
$ trace.py --check backend
backend/src/billing/raise.ts: the file changed without a rebind — 1 binding(s): rules/sales/invoice-immutable
...
1 code over 1 file(s): …
```

*O que isso diz:* o arquivo mudou, mas o trace ainda afirma o digest antigo. Não diz se a mudança
está certa ou errada.

**2. A pessoa invoca a rota.** Nomeia o conjunto de arquivos (na grafia da raiz do target, sem o
prefixo `backend/`), a raiz do projeto e um slug novo:

```
/siegard:reconcile  file set: src/billing/raise.ts   project root: .   slug: hand-fix-invoicing
```

**3. Situate.** A skill confirma que a especificação e o trace são válidos, que
`siegard-reconcile/hand-fix-invoicing.md` não existe e que `raise.ts` está commitado.

**4. Stage.** A skill roda:

```sh
trace.py --stage backend specification hand-fix-invoicing /tmp/ws src/billing/raise.ts
```

*Resultado:* o workspace `/tmp/ws` passa a conter `manifest.json` (dizendo que `raise.ts` tem um
nó a julgar), `packs/src__billing__raise.ts.md` (com o texto completo de
`rules/sales/invoice-immutable`) e `candidates.txt`. A pasta vazia
`siegard-reconcile/hand-fix-invoicing.returns/` é criada. Nenhum par foi omitido, porque o arquivo
mudou.

**5. Julgar.** Um `siegard:specification-conformance-reviewer` recebe o arquivo, o pacote, o índice
de candidatos, a especificação e o contrato. Ele devolve o retorno abaixo, que a skill salva
literalmente como `siegard-reconcile/hand-fix-invoicing.returns/src__billing__raise.ts.yaml`:

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule governs modification of a raised invoice; the guard states a cap no node holds
candidates_opened:
  - rules/sales/invoice-immutable
```

*O que o juiz disse:* o fato do nó (imutabilidade de fatura emitida) não está mais neste arquivo
(`held_at: nowhere`), e o arquivo agora afirma uma regra ("no máximo uma fatura por pedido") que o
nó não contém — por isso o finding `contradicts` contra ele.

**6. Capture.** Não houve camada mecânica; o passo é pulado e isso é dito no relatório.

**7. Fold.** A skill escreve a premissa:

```yaml
title: Hand correction to invoicing
summary: Added by hand during an incident; the behavior is correct.
target: backend
files:
  - path: src/billing/raise.ts
    change: refuses a second invoice for an order that already has one
```

e roda `trace.py --fold backend /tmp/ws /tmp/ws/premise.yaml siegard-reconcile/hand-fix-invoicing.md`.
O fold aplica as regras: há um finding que nomeia o nó → o nó não está conforme → `conforms:
false`, `observed_at: [src/billing/raise.ts]`, sem `encoded_at`. Em seguida,
`trace.py --reconciliation` confirma que o registro cumpre o contrato.

**8. Bind.** `trace.py --bind-record … --workspace /tmp/ws` não vincula nada (nenhum nó tem
`encoded_at`), e o recibo diz exatamente isso.

**9. Relatório.** Duas portas, e a skill não escolhe nenhuma:
- **O código está certo, a especificação está atrasada** → `/analyse` com o finding como material,
  para que um nó passe a dizer "um pedido tem no máximo uma fatura"; depois, `/reconcile` de novo
  sobre o mesmo arquivo, com slug novo. Nessa segunda reconciliação, o novo nó entra como
  candidato, o juiz o encontra no código, e ele é vinculado.
- **A especificação está certa, o código está errado** → incremento corretivo do `/plan-work`.

**10. Depois.** `trace.py --owed backend` continua listando o finding até que algum registro libere
o par. O `--check` continua mostrando o drift `code` de `raise.ts`, porque nada foi recarimbado.

**Variações:**
- **Se o único problema fosse um comentário** — por exemplo `// an order may only have one invoice`
  acima de um código que já impõe um nó de regra —, o juiz registraria `kind: restates`, o nó seria
  vinculado normalmente, e o relatório entregaria a rota de comentários: apagar o comentário,
  commitar, `/reconcile` sobre o arquivo com slug novo.
- **Se fosse uma mensagem de erro** que o sistema devolve dizendo a mesma coisa que o nó, não
  haveria finding nenhum: é comportamento que concorda com o nó.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Palavras informais e seus termos oficiais](14-palavras-informais-e-seus-termos-oficiais.md) · Próximo: [Exemplo completo 2: adotando o Siegard num sistema existente](16-exemplo-completo-2-adotando-o-siegard.md)
