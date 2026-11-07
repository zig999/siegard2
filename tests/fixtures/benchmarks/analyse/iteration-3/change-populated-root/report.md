# /analyse — reabertura de caso resolvido (raiz populada)

Projeto: `/tmp/analyse-bench/iteration-3/projects/change-populated-root` · raiz de especificação: `spec` · material em prosa (não é arquivo).

## Nós escritos (campos decididos, como `--shape --of` imprimiu)

Criados:
- `domain/troubleshooting/reopening` — 3 decided / 7 declared
- `rules/troubleshooting/reopen-within-seven-days` — 2 decided / 5 declared

Alterados:
- `domain/troubleshooting/case` — 2 decided / 26 declared (atributo `reopenings`, operação `reopen`, cardinalidade de `resolution` 0..1 → 0..*, `## Responsibility` estendida)
- `rules/troubleshooting/case-transitions` — 1 decided / 35 declared (o campo `rejections`, decidido 3× no log, conta uma vez; `resolved` deixa de ser terminal; transição `resolved --reopen--> investigating`; 5 rejeições novas)

Removidos: nenhum.

## Conjunto de impacto lido

Nós de entrada: `domain/troubleshooting/case`, `domain/troubleshooting/case-status`, `rules/troubleshooting/case-transitions`, `domain/troubleshooting/resolution`, `constraints/asynchronous-events` (único nó em `constraints/`).
Lidos (saída de `spec.py --impact`, 12 nós): constraints/asynchronous-events, contracts/troubleshooting/case-resolved, domain/troubleshooting/case, case-id, case-status, hypothesis, investigation, resolution, rules/troubleshooting/alert-opens-case, rules/troubleshooting/case-transitions (+ case-transitions.log), scenarios/system/troubleshoot-from-alert.

## Decisões registradas nesta invocação (primeira linha do writer)

1. `decided: domain/troubleshooting/reopening.log.md entries[0] — type` — value-object; uma reabertura nunca muda depois de registrada, então duas com mesmo motivo e instante são intercambiáveis.
2. `decided: domain/troubleshooting/reopening.log.md entries[1] — attributes.reason.type` — string; o motivo é o relato do próprio cliente, que nenhum conjunto fechado comporta.
3. `decided: domain/troubleshooting/reopening.log.md entries[2] — attributes.reopened_at` — datetime obrigatório; a janela de 7 dias só se verifica contra o instante da reabertura.
4. `decided: domain/troubleshooting/case.log.md entries[0] — attributes.reopenings` — atributo do caso com muitos valores `reopening`; nada no material limita um caso a uma reabertura.
5. `decided: domain/troubleshooting/case.log.md entries[1] — relationships.resolution.cardinality` — 0..*; um caso reaberto é resolvido de novo, e manter cada resolução preserva aquela de onde a janela contou.
6. `decided: rules/troubleshooting/case-transitions.log.md entries[1] — rejections` — `reopen` rejeitado em `open` e `investigating`; o material só permite reabrir caso resolvido.
7. `decided: rules/troubleshooting/case-transitions.log.md entries[2] — rejections` — `start-investigation`, `resolve` e `cancel` rejeitados em `resolved`; o material nomeia a reabertura como único movimento de um caso resolvido.
8. `decided: rules/troubleshooting/reopen-within-seven-days.log.md entries[0] — statement` — a janela conta da resolução mais recente; o problema que o cliente diz ter voltado é o que a última resolução afirmou resolver.
9. `decided: rules/troubleshooting/reopen-within-seven-days.log.md entries[1] — expression` — no máximo 168 horas após o `resolved_at` da última resolução, limite incluído.

Fatos lidos do material, não decididos: reabrir leva `resolved` a `investigating`; o gatilho é o cliente informar que o problema voltou; limite de 7 dias após a resolução; `cancelled` nunca reabre (permanece terminal); cada reabertura registra o motivo informado pelo cliente (`reason`, `required: true`).

## Leitura do `--shape` — o que ficou de pé e por quê

- `domain/troubleshooting/case` (95w) e `domain/troubleshooting/reopening` (53w) no p90 de element: o comprimento de `case` vem dos campos declarados (o nó é a raiz do agregado); `reopening` carrega uma frase de descrição com o termo do material ("reabertura") para mapear de volta à fonte. Mantidos.
- `why` no p90 (18w) em três logs: entradas de `case` e `reopening.type` carregam uma afirmação cada. A entrada `expression` de `reopen-within-seven-days` junta duas razões (leitura de "até" como inclusivo, e horas decorridas em vez de dias de calendário) — fica como está porque entradas não se editam (SPEC-001 R9); um revisor que discorde de uma das duas metades corrige por mudança comum.
- `rejections` decidido 3× em `case-transitions.log`: a entrada anterior (open/resolve) e as duas novas cobrem pares distintos e não se contradizem.
- Fecho de leitura de `reopen-within-seven-days` (1 nó, 107w): a descrição nomeia `case-transitions` só como fronteira (o que este nó não decide e quem decide).
- Nenhum statement com mais de uma frase, nenhuma expression maior que o statement, nenhuma frase compartilhada, nenhum nome sem nó.

## Cross-check — itens de observação (sem caso concreto decidido de modo diferente)

- `case-transitions` × `reopen-within-seven-days`: a máquina declara `resolved --reopen--> investigating` sem condição; o invariante recusa a reabertura após 168 horas. Não há caso decidido de forma oposta (a máquina diz por onde o caso pode ir, o invariante restringe quando) — mesmo padrão de `hypothesis-requires-evidence` sobre `resolve`. Nenhuma decisão registrada.
- `case.resolved_at` × `resolution.resolved_at`: duplicação anterior a esta invocação; com várias resoluções por caso, o significado de `case.resolved_at` após nova resolução não é declarado. Fora do que o material pede; não reaberto.
- `contracts/troubleshooting/case-resolved`: o evento é publicado ao resolver; nada publica a reabertura, e o material não pede. Um consumidor do evento pode tomar como final um caso que ainda reabre.

## Ledger

O material foi dado na conversa, não como arquivo: não há linhas, nenhum ledger é devido (SPEC-001 R16), e `trace.py --ledger` não rodou.

## O que este incremento pode ter posto o código entregue em violação

Este passo nunca lê o alvo `app`. Os nós escritos aqui podem declarar uma obrigação que o código já viola — em particular, `resolved` deixou de ser terminal e a resolução passou a 0..*: código entregue que trata `resolved` como final, ou que guarda uma única resolução, contraria a especificação agora. Só uma reconciliação descobre isso, se alguém rodar uma; nada a agenda.

## Candidatos para uma reconciliação

Nós que este incremento escreveu (não vinculados a nenhum código):
domain/troubleshooting/reopening, rules/troubleshooting/reopen-within-seven-days, domain/troubleshooting/case, rules/troubleshooting/case-transitions

## Validação final (verbatim)

```
specification sound: 11 element(s), 4 rule(s), 2 scenario(s), 4 contract(s), 1 constraint(s) across 2 context(s); 11 decision(s) disclosed
```

`spec.py --project`:
```
projected 7 file(s) into spec/projections: capability-map.mmd, class-diagram-monitoring.mmd, class-diagram-troubleshooting.mmd, context-map.mmd, full-text.md, overview.md, state-troubleshooting-case.mmd
```

## Próximo passo

`/plan-work` invocation ready to paste:

```
/plan-work /tmp/analyse-bench/iteration-3/projects/change-populated-root target <key> slug <slug> — <o escopo, em prosa>
```

`/reconcile` invocation ready to paste (para verificar código entregue contra os candidatos acima):

```
/reconcile /tmp/analyse-bench/iteration-3/projects/change-populated-root <arquivos> — candidatos: domain/troubleshooting/reopening, rules/troubleshooting/reopen-within-seven-days, domain/troubleshooting/case, rules/troubleshooting/case-transitions
```

A revisão é `git diff` sobre `spec/`; quem fizer o commit da especificação o faz por caminho. Nada foi commitado.

## Handoff (verbatim, as `handoff.py --render` printed it)

```
Nenhuma iniciativa em andamento neste projeto.
```

1. Reabrir caso resolvido (até 7 dias, com motivo) está especificado; qual o próximo passo?
   - **Recomendado** `a`: Planejar a entrega da reabertura. Julgamento: a especificação valida e as regras novas não têm código ligado. Mudaria se já houver código entregue tratando caso resolvido como final.
   - `b`: Conferir o código entregue contra os quatro nós escritos agora.
   - Se nenhuma for tomada: A especificação fica alterada, sem commit.

   ```
   /plan-work /tmp/analyse-bench/iteration-3/projects/change-populated-root target <key> slug <slug> — <o escopo, em prosa>
   ```

Relatório completo: /tmp/analyse-bench/iteration-3/projects/change-populated-root/.git/siegard/handoff/20261107T133206Z-analyse.md
