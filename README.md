# BeeClub no Cloudflare (plano gratuito para protótipo)

Este projeto migra o protótipo para **Cloudflare Workers + D1**. D1 é SQLite gerido pela Cloudflare; a aplicação não depende de um servidor Python permanente nem de uma base SQLite local. O plano gratuito publicado pela Cloudflare inclui quotas diárias de leitura/escrita e armazenamento; consulte os limites atuais antes de produção.

## 1. Importar o projeto para GitHub
Carregue o conteúdo desta pasta para a raiz de um repositório GitHub. O `index.html` está em `public/`; a API e as rotas do passe estão em `src/worker.js`.

## 2. Criar a base D1 e publicar
Instale Node.js. No terminal, na pasta do projeto:

```sh
npm install
npx wrangler login
npx wrangler d1 create beeclub-data
```

O comando mostra um `database_id`. Abra `wrangler.jsonc` e substitua `local-d1-database-id` por esse ID real. Depois inicialize a base e publique:

```sh
npm run db:init:remote
npm run deploy
```

O primeiro deploy publica Workers e os recursos estáticos no mesmo domínio `workers.dev`; o Worker atende API, gera o passe e entrega o frontend.

## 3. Desenvolvimento local

```sh
npm run db:init:local
npm run dev
```

## Fluxo de teste
1. Abra o URL `workers.dev` que o deploy informar.
2. No painel, abra **Wallet dos clientes → QR para guardar na wallet**.
3. Leia o QR de adesão com outro telemóvel; o passe abre no navegador, sem instalar app.
4. No painel, escolha **Validar QR do cliente** e use a leitura pela câmara ou o código impresso no passe.
5. Com o painel ainda aberto, deverá surgir o aviso da visita em alguns segundos.

O leitor QR está incluído localmente no projeto e pede acesso à câmara. Permita-o no navegador e use o domínio HTTPS publicado.

## Importante
- Esta é ainda uma versão de protótipo: **não tem login/admin, proteção contra fraude nem integrações nativas Apple Wallet/Google Wallet**. Não use com clientes reais nem dados sensíveis até adicionar essas proteções.
- O passe é uma página web responsiva; funciona em vários dispositivos e não requer instalação.
- O botão de notificações usa aviso do painel enquanto aberto. Push com a página fechada requer configuração adicional.
- Quotas gratuitas podem mudar; verifique a página oficial do D1: https://developers.cloudflare.com/d1/platform/pricing/
- O código de leitura QR `html5-qrcode` é Apache-2.0; `qrcode-generator` é MIT. Avisos estão em `licenses/`.
