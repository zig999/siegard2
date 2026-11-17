# Parte III — Consulta

> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Os agentes](13-os-agentes.md) · Próximo: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md)

## 14. Palavras informais e seus termos oficiais

Estas palavras aparecem em conversas, notas de sessão ou mensagens de commit. **Não** são campos
nem flags do framework (exceto onde indicado); eis o termo oficial que cada uma representa.

| Você pode ouvir | Significa | Termo oficial |
|---|---|---|
| **fold** (dobrar, dobra) | Combinar os retornos salvos dos juízes e a premissa no registro de reconciliação, por regras fixas. | `trace.py --fold` |
| **refold / re-fold** (redobrar) | Rodar o `--fold` de novo sobre os **mesmos retornos salvos** — tipicamente depois que uma correção do framework mudou uma regra do fold, e antes de o registro ser commitado. Só é possível porque os retornos são guardados literalmente e o fold é mecânico. Nunca é uma edição à mão do registro e nunca pergunta de novo aos juízes. | `trace.py --fold` (de novo) |
| **unfold / unfolded** | Nome interno no `deliver.py` para uma revisão cujo passe de conformidade rodou sobre um target com trace mas **não dobrou nenhum registro de reconciliação**. O `deliver.py` imprime um recibo: os outros nós vinculados aos arquivos revisados ainda carregam digests antigos, e um `/reconcile` sobre esses arquivos os fecha. | o recibo de "revisão não reconciliada" |
| **certificate** (certificado) | Uma certificação que se sustentou. | `decided_by: test` (+ `step`, `proof`) |
| **comment findings** | Findings `restates` em que o texto é um **comentário** ou docstring no código. | `kind: restates` |
| **emitted-text findings** | Findings sobre texto que o **sistema em execução emite** — descrição de ferramenta ou API, mensagem de erro, prompt, linha de log. Esse texto é comportamento, nunca `restates`: se concorda com o nó, não é finding; se discorda, é `contradicts`; se afirma um fato que nenhum nó contém, é `unstated`. Texto que só nomeia um controle (rótulo, nome acessível, placeholder) e o ajuste que um cliente faz das próprias requisições (tempo de cache, número de tentativas) não são finding nenhum (§10). | nenhum finding, `kind: contradicts` ou `kind: unstated` |
| **unheld** | *(este é oficial)* Um candidato de adoção que nenhum arquivo contém. | `unheld` no registro |
| **onda** (wave) | *(este é oficial)* Um grupo de no máximo `n` delegações, disparado de uma vez e encerrado quando o `--save-return` informa `0 pending`. | `waves` no manifesto |
| **repetição** (repeat) | Um agente que recebeu exatamente o mesmo prompt que outro do mesmo tipo, antes, na mesma janela. É candidata a retrabalho; se foi retrabalho, quem julga é o leitor. | `repeats_earlier` na telemetria |
| **o corpus** | Todos os registros em `siegard-reconcile/`, lidos em conjunto. | lido pelo `--owed` |
| **par** | Um nó + um de seus arquivos. | par nó-arquivo |
| **liberar / liberado** (clear / cleared) | O julgamento não encontrou nada contra um nó: ele está conforme e é vinculado. | `conforms: true` + `encoded_at` |
| **carimbar / recarimbar** (stamp / restamp) | Escrever os digests atuais no trace. | bind / rebind |
| **juiz** | Um agente a quem foi delegado um julgamento. | uma delegação |
| **porta** (door) | Uma invocação pronta para colar que um relatório entrega. | `door` (definido nos "Terms" de cada skill) |
| **porta recomendada** | A porta que o relatório indica quando entrega mais de uma, com o motivo, o fato que a decide e o fato que a mudaria. | recomendação `derived` ou `judged` (§12); `recommended:` no log de orquestração |
| **tomar a porta** | Seguir a porta recomendada sem perguntar, onde a pessoa já autorizou. | uma linha `decided: <door> — <criterion> — <deciding fact>` no log de orquestração |
| **piloto automático**, **modo autônomo** | Apontar um escopo e só voltar no fim. | um goal armado por `/siegard-goal --arm`, que termina em `state A` ou `state B` |
| **carta branca** | Deixar o framework tomar as decisões das paradas sem perguntar. | um grant armado por `/siegard-grant` |
| **decidido sozinho** | Um fato que a especificação não dizia, decidido no planejamento ou na entrega e gravado no nó. | a rota *decided-fact* do `/plan-work`; a entrada no decision log (`<slug>.log.md`) |
| **parou** | Uma rota de ponta a ponta que encontrou algo que só a pessoa resolve. | uma linha `stop: <class> — <fact>` no `orchestration.md` |
| **retomar** | Invocar de novo uma rota sobre uma iniciativa que já tem plano vivo. | o mesmo slug no `/deliver-scope` |
| **medição** | A contagem de custo e de fricção que fecha uma execução de ponta a ponta. | `telemetry.py` (precedido de `--probe`), gravado na raiz de telemetria e commitado como `deliver-scope <slug>: measure` |
| **sobra** (remainder) | O que resta depois de uma ação parcial: arquivos ainda devidos numa reconciliação, ou o que uma certificação não cobriu. | "the remainder" / `remainder` |
| **pacote** (pack) | O arquivo com o texto dos nós que um juiz deve ler. | node pack / certification pack |

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Os agentes](13-os-agentes.md) · Próximo: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md)
