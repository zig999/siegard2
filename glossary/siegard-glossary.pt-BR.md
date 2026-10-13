# Glossário do Siegard (pt-BR) — guia explicativo para quem está começando

Este documento explica, em linguagem acessível e com o máximo de detalhe possível, cada palavra,
arquivo, comando e procedimento do Siegard. Foi escrito para um leitor que **nunca viu o
Siegard**: nenhum conhecimento prévio do framework é pressuposto. Cada verbete diz o que o termo
significa, por que ele existe, em que momento do trabalho aparece, como funciona passo a passo e,
sempre que possível, traz um exemplo.

**Versão descrita.** Esta edição descreve o Siegard **5.19.0**. Ela amplia a tradução de
`glossary/siegard-glossary.md`, que ainda descreve a 4.21.3; os verbetes sobre levantamento
(`/survey`), material de intenção, ledger, `/adopt-scope`, `/clarify-request`, o campo `tests`, as
ondas de delegação e os agentes `domain-surveyor` e `test-intent-reader` ainda não têm par na
versão inglesa. Onde as duas
versões divergirem, vale a inglesa, conforme a regra do repositório para traduções.

**Precedência.** Este glossário explica; ele não governa. Onde ele divergir do `SKILL.md` de uma
skill, do `--help` de um script ou de um schema em `schemas/`, valem esses arquivos, porque são
eles que efetivamente rodam.

**Termos em inglês.** Nomes de campos, flags, comandos, skills, agentes, classes, valores
enumerados e nomes de arquivos e pastas (`--stage`, `held_at`, `contradicts`, `orphaned`…)
permanecem em inglês, exatamente como o framework os escreve, porque é isso que você digita ou lê
nos arquivos. Saídas reais de scripts também permanecem em inglês. Quando um termo tem uma
tradução usual em português, ela aparece entre parênteses na primeira ocorrência.

---

## Sumário

- **Parte I — Antes de começar**
  - 0. [Como ler este glossário](siegard-glossary.pt-BR/00-como-ler-este-glossario.md)
  - 1. [Conceitos prévios](siegard-glossary.pt-BR/01-conceitos-previos.md)
  - 2. [O panorama: que problema o Siegard resolve](siegard-glossary.pt-BR/02-o-panorama-que-problema-o-siegard.md)
  - 3. [A jornada completa de uma mudança, contada do começo ao fim](siegard-glossary.pt-BR/03-a-jornada-completa-de-uma-mudanca.md)
- **Parte II — Os verbetes**
  - 4. [Configurando um projeto](siegard-glossary.pt-BR/04-configurando-um-projeto.md)
  - 5. [A especificação (`/analyse`)](siegard-glossary.pt-BR/05-a-especificacao.md)
  - 6. [Planejamento (`/plan-work`)](siegard-glossary.pt-BR/06-planejamento.md)
  - 7. [Entrega (`/implement-task`, `/deliver-scope`)](siegard-glossary.pt-BR/07-entrega.md)
  - 8. [Revisão (`/review-change`)](siegard-glossary.pt-BR/08-revisao.md)
  - 9. [O trace](siegard-glossary.pt-BR/09-o-trace.md)
  - 10. [Reconciliação (`/reconcile`)](siegard-glossary.pt-BR/10-reconciliacao.md)
  - 11. [Adoção e levantamento (`/survey`)](siegard-glossary.pt-BR/11-adocao-e-levantamento.md)
  - 12. [As demais skills e os scripts auxiliares](siegard-glossary.pt-BR/12-as-demais-skills-e-os-scripts.md)
  - 13. [Os agentes](siegard-glossary.pt-BR/13-os-agentes.md)
- **Parte III — Consulta**
  - 14. [Palavras informais e seus termos oficiais](siegard-glossary.pt-BR/14-palavras-informais-e-seus-termos-oficiais.md)
  - 15. [Exemplo completo 1: uma correção feita à mão](siegard-glossary.pt-BR/15-exemplo-completo-1-uma-correcao-feita.md)
  - 16. [Exemplo completo 2: adotando o Siegard num sistema existente](siegard-glossary.pt-BR/16-exemplo-completo-2-adotando-o-siegard.md)
  - 17. [Perguntas frequentes](siegard-glossary.pt-BR/17-perguntas-frequentes.md)
  - 18. [Índice alfabético](siegard-glossary.pt-BR/18-indice-alfabetico.md)

Cada capítulo é um arquivo em `glossary/siegard-glossary.pt-BR/`. Os números das seções (§) citados no texto são os dos capítulos.
