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
| **emitted-text findings** | Findings sobre texto que o **sistema em execução emite** — descrição de ferramenta ou API, mensagem de erro, prompt, linha de log. Desde a 4.21.3, esse texto é comportamento, nunca `restates`: se concorda com o nó, não é finding; se discorda, é `contradicts`. (Antes da 4.21.3, uma descrição repetindo um fato que o código impunha era registrada como `restates`, por isso registros antigos ainda podem ter entradas assim.) Desde a 5.4.0, texto que só nomeia um controle (rótulo, nome acessível, placeholder) não é finding nenhum (§10). | nenhum finding, ou `kind: contradicts` |
| **unheld** | *(este é oficial)* Um candidato de adoção que nenhum arquivo contém. | `unheld` no registro |
| **onda** (wave) | *(este é oficial)* Um grupo de no máximo `n` delegações, disparado de uma vez e encerrado quando o `--save-return` informa `0 pending`. | `waves` no manifesto |
| **repetição** (repeat) | Um agente que recebeu exatamente o mesmo prompt que outro do mesmo tipo, antes, na mesma janela. É candidata a retrabalho; se foi retrabalho, quem julga é o leitor. | `repeats_earlier` na telemetria |
| **o corpus** | Todos os registros em `siegard-reconcile/`, lidos em conjunto. | lido pelo `--owed` |
| **par** | Um nó + um de seus arquivos. | par nó-arquivo |
| **liberar / liberado** (clear / cleared) | O julgamento não encontrou nada contra um nó: ele está conforme e é vinculado. | `conforms: true` + `encoded_at` |
| **carimbar / recarimbar** (stamp / restamp) | Escrever os digests atuais no trace. | bind / rebind |
| **juiz** | Um agente a quem foi delegado um julgamento. | uma delegação |
| **porta** (door) | Uma invocação pronta para colar que um relatório entrega. | "the invocation ready to paste" |
| **sobra** (remainder) | O que resta depois de uma ação parcial: arquivos ainda devidos numa reconciliação, ou o que uma certificação não cobriu. | "the remainder" / `remainder` |
| **pacote** (pack) | O arquivo com o texto dos nós que um juiz deve ler. | node pack / certification pack |

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [Os agentes](13-os-agentes.md) · Próximo: [Exemplo completo 1: uma correção feita à mão](15-exemplo-completo-1-uma-correcao-feita.md)
