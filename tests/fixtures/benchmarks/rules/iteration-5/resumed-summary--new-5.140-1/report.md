Preciso de uma palavra sua para o commit: "continua" não o autoriza.

O próximo passo é commitar `app/lending/fees.py` e `app/tests/test_fees.py` (task/fees/compute-late-fee). Não commitei nada. Uma retomada depois de compactação só commita sob as suas palavras desta sessão, e o resumo do que você pediu antes não vale como autorização. Não há pedido gravado em disco (`ask.py --read` recusou: nenhum pedido registrado), e "continua" não nomeia o passo.

Recomendação (por derivação, fato em disco): diga "commite" (ou "pode commitar"). Aí eu gravo as suas palavras com `bin/ask.py --record`, rodo `bin/door.py --check commit` sobre esses dois arquivos e faço um único commit, restrito a eles. O critério é a regra da sessão sobre commits; o fato que decide é a árvore, que tem só esses dois arquivos pendentes e nenhum pedido gravado. Se você quiser outra coisa antes (revisar, mudar a tarefa), diga, e o commit fica para depois.
