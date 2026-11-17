# Parte I — Antes de começar

> [← Glossário](../siegard-glossary.pt-BR.md) · Próximo: [Conceitos prévios](01-conceitos-previos.md)

## 0. Como ler este glossário

Os verbetes seguem, na medida do possível, a mesma estrutura:

| Rótulo | O que responde |
|---|---|
| **O que é** | A definição, em uma ou duas frases. |
| **Por que existe** | O problema que o conceito resolve. Sem isso, a definição parece arbitrária. |
| **Quando aparece** | Em que etapa do trabalho, e em qual skill ou comando, você o encontra. |
| **Como funciona** | O procedimento, passo a passo. |
| **Exemplo** | Um trecho real de arquivo ou de saída de comando. |
| **Não confundir com** | Termos parecidos que significam outra coisa. |

Verbetes curtos omitem os rótulos que não se aplicam.

**Sugestão de leitura.** Na primeira vez, leia as seções 1, 2 e 3 inteiras: elas dão o contexto
sem o qual os verbetes ficam soltos. Depois, use a Parte II como referência, voltando a ela
quando encontrar um termo desconhecido. A seção 10 (reconciliação) concentra os termos mais
difíceis e deve ser lida em ordem.

**Convenção para comandos.** As skills executam os scripts assim:

```sh
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/<script>.py ...
```

- `python3 -B` executa o script com Python 3 sem gravar arquivos de cache (`__pycache__`).
- `${CLAUDE_PLUGIN_ROOT}` é a pasta onde o plugin do Siegard está instalado. Ela contém as
  subpastas `bin/` (scripts), `schemas/` (contratos), `skills/`, `agents/` e `hooks/`.

Para encurtar, este glossário escreve `trace.py ...` onde a forma completa é
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py ...`.

**Convenção para caminhos.** Nos exemplos, `backend` é o nome de um target (uma base de código,
ver §4), `specification` é a pasta da especificação e `src/...` são arquivos de código.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Próximo: [Conceitos prévios](01-conceitos-previos.md)
