# Publicar o protótipo BeeClub (Render)

## Importante antes de pôr clientes reais
Este é um MVP de demonstração: o painel ainda não tem autenticação/perfis de funcionário, a lista de clientes inclui dados de exemplo e a leitura de QR soma visitas sem proteção contra abuso. Publique apenas para teste controlado e não introduza dados pessoais/financeiros reais até adicionar login, autorização e regras anti-fraude.

## Publicação
1. Crie uma conta em Render e um repositório Git privado no GitHub.
2. Envie para o repositório estes ficheiros: `index.html`, `server.py`, `requirements.txt` e `render.yaml`.
3. No Render, escolha **New → Blueprint**, ligue o repositório e confirme a criação do serviço.
4. O Blueprint cria um serviço web Python e um disco persistente para a base de dados SQLite. Aguarde o deploy e abra o URL `.onrender.com` atribuído.
5. Teste em dois telemóveis na mesma URL: no painel, Wallet dos clientes → QR para guardar na wallet; leia o QR noutro telemóvel; depois, no painel, Validar QR do cliente.

O `render.yaml` configura um disco persistente (o plano escolhido pode ter custo). Não remova o disco: é onde ficam os clientes, créditos e definições. A pré-visualização do Arena é adequada para testes temporários, mas não substitui um domínio/serviço de produção sob controlo do negócio.
