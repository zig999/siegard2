# Examples

Each prompt below, in the fence that follows a `prompt` comment, is held to the contract by
`bin/enrich.py`; the comment is the test's marker and is not part of a prompt. A prompt's content
follows the language of its draft: the drafts and prompts of examples 1, 2 and 4 are in English,
and example 3 is in Brazilian Portuguese. The section names are the contract's in every language.

The examples differ on purpose in what they add: example 2 adds nothing, because its draft is
already one precise operation, and the others add two or three lines. The count is not a target.

## 1. A vague draft about the project

```text
see whether CHANGELOG.md lists every release that has a tag
```

The project settles what a release is: CHANGELOG.md states how a version is listed, so that is
context and not a field. The draft says "see", so the mode is a look and the prompt changes nothing.

<!-- prompt -->
```
ROLE: Release auditor for a git repository.
OBJECTIVE: Find every release tag in the repository that CHANGELOG.md does not list, and every version CHANGELOG.md lists that has no tag.
CONTEXT:
- CHANGELOG.md, lines 3-4: every version since 3.18.0 is one commit whose subject begins `Ship <version>:`, and the file lists those subjects.
- A version before 3.18.0 shipped under another form of subject and is read from git log (CHANGELOG.md, lines 5-6).
CONSTRAINTS:
- Do not modify the project.
TOOLS:
- git tag --list to read the tags.
- git log --oneline --grep "^Ship " to read the release commits.
- Read on CHANGELOG.md to read the listed versions.
STEPS:
- List the tags and the listed versions.
- Compare the two lists in both directions.
ADDITIONS:
- Report separately the versions before 3.18.0 — CHANGELOG.md states they are not listed in the same form, so a difference there is not a defect.
EXTERNAL_VALIDATION:
- Each difference quotes the git command whose output shows it, so the person can rerun it.
RESPONSE_FORMAT:
- Two lists: tags missing from CHANGELOG.md, and listed versions missing a tag, each entry with the evidence.
- If both are empty, one sentence saying so and the number of tags compared.
```

## 2. A draft that is already one precise operation

```text
Run python3 -B src/claude/bin/enrich.py --help and list the exit codes it documents. Do not modify anything.
```

Nothing is missing and the executor would do the rest anyway, so the prompt carries the draft
as stated, adds no section of additions, and leaves no field.

<!-- prompt -->
```
ROLE: Reader of command-line documentation.
OBJECTIVE: Report the exit codes that python3 -B src/claude/bin/enrich.py documents in its own help text.
CONTEXT:
- The command prints its docstring for --help, and the docstring ends with an Exit section.
CONSTRAINTS:
- Do not modify anything.
TOOLS:
- python3 -B src/claude/bin/enrich.py --help, run exactly as written.
STEPS:
- Run the command and read its output.
- List each exit code with the meaning the help gives it.
EXTERNAL_VALIDATION:
- Each code and meaning is quoted from the command's output, so the person can rerun the command and compare.
RESPONSE_FORMAT:
- One line per exit code: the number, then its meaning as the help states it.
```

## 3. A draft in Brazilian Portuguese, outside the project

```text
monta um prompt pra um agente triar os chamados de suporte da semana por urgência
```

The draft is in Portuguese, so the prompt is in Brazilian Portuguese. It is not about the project,
so nothing is read, and what the draft leaves open is a field.

<!-- prompt -->
```
ROLE: Analista de suporte técnico sênior, especializado em triagem de chamados.
OBJECTIVE: Classificar os chamados de suporte da semana por urgência, para que a equipe atenda primeiro os que causam maior dano ao cliente.
CONTEXT:
- Os chamados estão em [sistema ou arquivo onde ficam os chamados] e a semana é [período a triar].
- Níveis de urgência em uso hoje: [níveis de urgência da equipe, ou "propor com base nos critérios abaixo"].
CONSTRAINTS:
- Não altere, feche nem responda nenhum chamado: a triagem só lê e classifica.
- Não copie dados pessoais de clientes para a resposta; use apenas o identificador do chamado.
TOOLS:
- A leitura do sistema ou do arquivo de chamados indicado acima.
- Os critérios de urgência: impacto no cliente, número de clientes afetados e existência de contorno.
STEPS:
- Leia todos os chamados do período.
- Classifique cada um em um nível de urgência, anotando o critério que decidiu.
- Ordene do mais ao menos urgente.
ADDITIONS:
- Marque os chamados que não permitem decidir a urgência e diga o que falta — um chamado sem informação classificado em silêncio esconde o risco.
- Agrupe chamados com a mesma causa aparente — vários chamados do mesmo problema indicam um incidente, não casos isolados.
EXTERNAL_VALIDATION:
- [Pessoa responsável pelo suporte] confere uma amostra de [tamanho da amostra] chamados e confirma o nível atribuído.
- Cada classificação cita o trecho do chamado que a sustenta, para que qualquer pessoa da equipe possa verificá-la.
RESPONSE_FORMAT:
- Uma tabela com as colunas identificador, urgência, critério, trecho do chamado.
- Abaixo dela, a lista dos chamados que não puderam ser classificados e o que falta em cada um.
```

## 4. A draft for a third party, with decisions left to the person

```text
I need a prompt for an interviewer to screen backend engineer candidates for a fintech
```

<!-- prompt -->
```
ROLE: Senior engineering interviewer for backend roles in a regulated financial-technology company.
OBJECTIVE: Run a first screening interview that tells whether a backend engineering candidate should go to the technical round for [role and seniority].
CONTEXT:
- The company works in [payments, lending or other fintech segment] and the stack is [main languages and datastores].
- The screening lasts [duration] and the candidate has sent [what the interviewer has: resume, assignment].
CONSTRAINTS:
- Ask only about skills and experience the role needs; do not ask about age, family, health or any other protected attribute.
- Take the same questions to every candidate for the role.
TOOLS:
- A structured scorecard with the criteria listed below, filled in during the interview.
- Behavioral questions in the situation-action-result form for ownership and incident handling.
STEPS:
- Open with the role and the process.
- Ask about a production system the candidate owned, a failure they handled, and a trade-off they made.
- Score each criterion on the scorecard before comparing with other candidates.
ADDITIONS:
- Ask one question about data consistency or money handling — in a financial product a wrong rounding or a double write is a defect with a legal cost.
- Record the evidence behind each score in the candidate's words — a score without evidence cannot be reviewed by a second interviewer.
EXTERNAL_VALIDATION:
- A second interviewer scores the same notes and the two scores are compared, with a review of any difference of more than one point.
- [Hiring manager or recruiter] checks the questions against the company's hiring policy before the first use.
RESPONSE_FORMAT:
- The interview script: opening, the questions in order with what a strong answer contains, and the closing.
- The scorecard as a table with the columns criterion, what is scored, evidence.
```
