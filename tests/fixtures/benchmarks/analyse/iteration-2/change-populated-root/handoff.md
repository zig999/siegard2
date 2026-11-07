# /analyse — reabertura de caso (change-populated-root)

Raiz do projeto: `/tmp/analyse-bench/iteration-2/projects/change-populated-root`
Raiz da especificação: `spec` (lida de `siegard.json`)
Material: prosa da conversa (pt-BR), não um arquivo.

## Nós escritos (campos decididos por esta invocação, como `--shape --of` imprimiu)

Criados:
- `domain/troubleshooting/reopening` — 3 decididos / 7 declarados
- `rules/troubleshooting/reopen-within-seven-days` — 1 decidido / 3 declarados

Alterados:
- `domain/troubleshooting/case` — 0 decididos / 26 declarados (ganhou o atributo `reopenings: reopening, many` e a operação `reopen`)
- `rules/troubleshooting/case-transitions` — 6 decididos / 35 declarados (1 decisão anterior + 5 desta invocação; `resolved` deixou de ser terminal, transição `resolved --reopen--> investigating`, cinco rejeições novas)

Removidos: nenhum.

## Conjunto de impacto lido

`spec.py --impact` sobre `domain/troubleshooting/case`, `domain/troubleshooting/case-status`, `rules/troubleshooting/case-transitions`, `domain/troubleshooting/resolution`, `contracts/troubleshooting/case-resolved`, `constraints/asynchronous-events` (12 nós, um salto):
- spec/constraints/asynchronous-events.md
- spec/contracts/troubleshooting/case-resolved.md
- spec/domain/troubleshooting/case.md
- spec/domain/troubleshooting/case-id.md
- spec/domain/troubleshooting/case-status.md
- spec/domain/troubleshooting/hypothesis.md
- spec/domain/troubleshooting/investigation.md
- spec/domain/troubleshooting/resolution.md
- spec/rules/troubleshooting/alert-opens-case.md
- spec/rules/troubleshooting/case-transitions.md
- spec/rules/troubleshooting/case-transitions.log.md
- spec/scenarios/system/troubleshoot-from-alert.md
Também lidos: `spec/domain/troubleshooting/_context.md` (achado por grep) e `spec/domain/troubleshooting/evidence.log.md` (formato de log existente).

## Decisões registradas nesta invocação

- `rules/troubleshooting/case-transitions` · `rejections.resolved.cancel` — `decided: rules/troubleshooting/case-transitions.log.md entries[1] — rejections.resolved.cancel` — cancel rejeitado em resolved; por quê: cancelar abandona um problema nunca resolvido, e um caso resolvido já foi resolvido.
- `rules/troubleshooting/case-transitions` · `rejections.resolved.resolve` — `decided: rules/troubleshooting/case-transitions.log.md entries[2] — rejections.resolved.resolve` — resolve rejeitado em resolved; por quê: um caso resolvido só volta à resolução por uma investigação reaberta.
- `rules/troubleshooting/case-transitions` · `rejections.resolved.start-investigation` — `decided: rules/troubleshooting/case-transitions.log.md entries[3] — rejections.resolved.start-investigation` — por quê: o material leva o caso resolvido de volta à investigação só pela reabertura.
- `rules/troubleshooting/case-transitions` · `rejections.open.reopen` — `decided: rules/troubleshooting/case-transitions.log.md entries[4] — rejections.open.reopen` — por quê: o material faz da reabertura algo que acontece a um caso resolvido.
- `rules/troubleshooting/case-transitions` · `rejections.investigating.reopen` — `decided: rules/troubleshooting/case-transitions.log.md entries[5] — rejections.investigating.reopen` — por quê: um caso em investigação já está onde a reabertura o levaria.
- `rules/troubleshooting/reopen-within-seven-days` · `statement` — `decided: rules/troubleshooting/reopen-within-seven-days.log.md entries[0] — statement` — sete períodos de 24 horas contados de `resolved_at` do caso (a resolução mais recente), com o instante-limite ainda permitido; por quê: `resolved_at` é o único instante que o caso registra para sua resolução.
- `domain/troubleshooting/reopening` · `type` — `decided: domain/troubleshooting/reopening.log.md entries[0] — type` — value-object; por quê: duas reaberturas com o mesmo motivo e instante são registros intercambiáveis dentro do caso.
- `domain/troubleshooting/reopening` · `attributes.reopened_at` — `decided: domain/troubleshooting/reopening.log.md entries[1] — attributes.reopened_at` — datetime obrigatório; por quê: a janela de 7 dias só pode ser verificada contra o instante da reabertura.
- `domain/troubleshooting/reopening` · `attributes.reason.type` — `decided: domain/troubleshooting/reopening.log.md entries[2] — attributes.reason.type` — string; por quê: o motivo é o que o cliente disse, sem conjunto fechado de valores no material.

Fatos lidos do material (não decididos): `resolved --reopen--> investigating`; `cancelled` permanece terminal (caso cancelado nunca é reaberto — a declaração `terminal` é a casa dessa afirmação); `reason` obrigatório em cada reabertura; limite de 7 dias após a resolução.

## Leitura de `--shape`

- `domain/troubleshooting/case` (85w) e `domain/troubleshooting/reopening` (50w) no p90 de elementos: relidos inteiros; o comprimento é de campos declarados, a prosa tem uma frase por título. Mantidos.
- `reopening` 3/7 decididos: verdadeiro — o material nomeia a reabertura e o motivo, e nada mais sobre sua forma.
- `why` no p90 em `reopening.log` e `case-transitions.log`: relidos; cada um carrega uma afirmação só.
- Fecho de leitura de `reopen-within-seven-days`: 1 nó (107w) — a frase de fronteira nomeia `case-transitions` como o nó que decide em que estado reabrir é possível. Mantida como fronteira, não argumento.
- Nenhuma frase compartilhada, nenhum nome sem nó, nenhum statement com mais de uma frase.

## Verificação cruzada

Pares tomados (`--shape` não nomeou nenhum; o material juntou estes):
- `reopen-within-seven-days` × `case-transitions`: a transição declara que `reopen` é permitido em `resolved`; o invariante recusa depois de 7 dias. Nenhum caso decidido de forma diferente — a transição é permissão, o invariante a restringe. Sem sobreposição: um decide estado, o outro tempo.
- `reopen-within-seven-days` × `hypothesis-requires-evidence`: um caso reaberto volta a `investigating` e a nova resolução continua exigindo evidência. Sem conflito.

Itens de vigilância (sem caso concreto a decidir):
- O que acontece com a `resolution` (composição `0..1`) e com `case.resolved_at` quando o caso é reaberto e depois resolvido de novo não está dito; a especificação admite uma só `resolution`. A janela usa a resolução mais recente (decidido acima), mas se a resolução anterior é substituída ou mantida como histórico fica para um material futuro.
- `case.resolved_at` e `resolution.resolved_at` registram o mesmo instante em dois lugares (anterior a esta invocação, fora do que ela muda).
- Nenhum evento `case-reopened` foi publicado: o material não diz que outro contexto precisa saber de uma reabertura.

## Ledger

O material não foi um arquivo: foi dado só na conversa, não tem linhas e não deve ledger.

## O que este incremento pode ter colocado o código entregue em violação

Esta etapa nunca lê o código-alvo, deliberadamente. As decisões deste incremento — `resolved` deixou de ser terminal, a transição `reopen`, as cinco rejeições novas, a janela de 7 dias e o motivo obrigatório — podem contradizer código já entregue (por exemplo, um código que trata `resolved` como estado final). A reconciliação é o que descobre isso, se alguém rodar uma. Nada agenda isso.

## Candidatos para uma reconciliação

- domain/troubleshooting/case
- domain/troubleshooting/reopening
- rules/troubleshooting/case-transitions
- rules/troubleshooting/reopen-within-seven-days

## Saída final do validador

```
specification sound: 11 element(s), 4 rule(s), 2 scenario(s), 4 contract(s), 1 constraint(s) across 2 context(s); 11 decision(s) disclosed
```

`--project` escreveu:
```
projected 7 file(s) into spec/projections: capability-map.mmd, class-diagram-monitoring.mmd, class-diagram-troubleshooting.mmd, context-map.mmd, full-text.md, overview.md, state-troubleshooting-case.mmd
```

## Próximo passo

`/plan-work` invocation ready to paste:

```
/plan-work /tmp/analyse-bench/iteration-2/projects/change-populated-root target <alvo> slug <slug-da-iniciativa> — <o escopo: reabertura de caso resolvido em até 7 dias, com motivo>
```

`/reconcile`, sobre os arquivos do alvo que implementam o ciclo de vida do caso, com os quatro candidatos acima, se já existe código entregue para ele.

A revisão é `git diff -- spec`; quem fizer o commit da especificação o faz por caminho. Nada foi commitado.
