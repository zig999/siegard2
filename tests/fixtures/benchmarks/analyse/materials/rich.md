Precisamos criar cadastro de clientes.

Customer é um Aggregate Root.

Customer possui:
- CustomerId
- Name
- Document
- Email

Document é um Value Object que aceita CPF ou CNPJ.

Email é opcional.

Clientes podem ser Active ou Inactive.

CPF/CNPJ deve ser único.
