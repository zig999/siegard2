> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [O panorama: que problema o Siegard resolve](02-o-panorama-que-problema-o-siegard.md) · Próximo: [Configurando um projeto](04-configurando-um-projeto.md)

## 3. A jornada completa de uma mudança, contada do começo ao fim

Esta seção narra, em alto nível, o percurso típico de um projeto. Cada termo em negrito tem um
verbete próprio na Parte II.

**Etapa 1 — Configuração.** A pessoa roda `/siegard-config`, que escreve o **`siegard.json`**: o
arquivo que declara onde ficam a especificação, os planos, os registros de entrega e as bases de
código (os **targets**). Opcionalmente, roda `/siegard-standard`, que redige o **standard** — as
regras do próprio projeto sobre como o código deve ser organizado e quais comandos o compilam e
testam.

**Etapa 2 — Especificação.** A pessoa entrega à skill `/analyse` um **material** (um documento, uma
transcrição de reunião, um ticket). A skill transforma esse material em **nós** da especificação —
elementos do domínio, regras, cenários, contratos, restrições de arquitetura — e valida tudo com o
`spec.py`. O que o material não dizia e precisava ser decidido é decidido e registrado no
**decision log**. A pessoa revisa o `git diff` e commita.

**Etapa 3 — Planejamento.** A pessoa descreve o que quer construir (o **escopo**) e roda
`/plan-work`. A skill levanta o código existente (**inventário**), recorta o escopo em **épicos**
e **tarefas**, e um agente separado (o **binder**) decide, para cada tarefa, quais nós da
especificação ela implementa. Divergências entre a tarefa e a especificação voltam como **notas**
classificadas. O resultado é validado pelo `plan.py`, que gera o `plan.json`.

**Etapa 4 — Entrega.** Para cada tarefa, a pessoa roda `/implement-task`. Um agente escreve o
código (`task-implementer`), outro escreve os testes (`test-author`), os comandos do projeto
rodam por meio do `run.py` (que guarda tudo o que foi impresso), e dois **registros de entrega**
são gravados: o de **implementação** e o de **prova**. Por fim, a skill **vincula** (bind) no
**trace** cada nó ao arquivo que agora contém o seu fato.

**Etapa 5 — Revisão.** A pessoa roda `/review-change`. Quatro julgamentos independentes (os
**passes**) examinam a mudança: se os testes provam os critérios, se o código afirma só o que a
especificação contém, se o código segue o standard, e por que alguma execução falhou. O resultado
é um **registro de revisão** com **findings**.

*(As etapas 3 a 5 podem ser executadas de ponta a ponta por `/deliver-scope`, que também faz os
commits entre elas e, ao final, mede o custo da execução.)*

**Etapa 6 — Semanas depois: uma edição fora do fluxo.** Durante um incidente, alguém corrige um
arquivo diretamente e commita. O trace continua afirmando o digest antigo daquele arquivo. Quando
alguém roda `trace.py --check`, o Siegard aponta **drift** (divergência) da classe `code`.

**Etapa 7 — Reconciliação.** A pessoa roda `/reconcile` sobre o arquivo alterado. A skill prepara
o material dos juízes (**stage**), dispara um juiz por arquivo, salva os retornos literalmente,
**dobra** (fold) os retornos num **registro de reconciliação** e **revincula** no trace apenas os
nós que os juízes liberaram. Para os demais, entrega as duas portas: corrigir a especificação
(`/analyse`) ou corrigir o código (incremento corretivo do `/plan-work`).

**Caminho alternativo — adoção.** Se o projeto já tinha código antes do Siegard, o percurso começa
por `/survey` (levantamento do código existente), segue para `/analyse` (que escreve a
especificação a partir do levantamento e um **ledger**) e termina num `/reconcile` em modo
**adoção**, que cria o primeiro trace. O `/adopt-scope` executa esses três passos de ponta a
ponta, um contexto por vez. Ver §11 e §16.

---
> [← Glossário](../siegard-glossary.pt-BR.md) · Anterior: [O panorama: que problema o Siegard resolve](02-o-panorama-que-problema-o-siegard.md) · Próximo: [Configurando um projeto](04-configurando-um-projeto.md)
