# Contexto do Projeto

## Identificacao

- Nome do repositorio: `site_samela_faculdade`
- Base tecnica: `Django + Python + SQLite`
- Objetivo atual: portal academico com autenticacao controlada e modulo inicial de orcamento

## Escopo implementado

- Tela inicial com tema academico moderno
- Login por login ou e-mail e senha
- Cadastro em modal com 3 etapas:
  - validacao de e-mail autorizado
  - envio de codigo curto por e-mail
  - criacao e confirmacao de senha
- Painel autenticado com dois acessos principais:
  - `Cadastrar campos`
  - `Acessar orcamento pronto`
- Modulo inicial do topico `5.1. Custeio do projeto de pesquisa`
- Cadastro de produto com exatamente 3 orcamentos
- Cada orcamento possui:
  - preco
  - quantidade
  - link
- Um dos 3 orcamentos pode ser marcado para entrar na soma total
- Tela `Orcamento pronto` alimentada pelos dados cadastrados

## Logins de acesso seeded

- Login ADM: `adm`
- Senha ADM: `123`
- Login teste: `fabiano`
- Senha teste: `123`

## Regras de cadastro

- Apenas e-mails autorizados podem criar conta
- A lista de e-mails autorizados fica no backend em `site_samela/settings.py`
- A lista visivel de e-mails autorizados foi removida da interface
- O e-mail `fabianopolone@hotmail.com` foi adicionado a whitelist

## Regras do orcamento atual

- O projeto exibido em `Orcamento pronto` e:
  - `INDICADORES E CRITERIOS DE AVALIACAO DE DESENVOLVIMENTO CULTURAL DE CRIANCAS DE PRE-ESCOLA NA THC`
- O texto institucional de orcamento ja aparece na tela pronta
- O primeiro topico ativo e `5.1`
- Os proximos topicos ainda serao adicionados depois

## Ajustes visuais ja feitos

- Pagina inicial redesenhada com layout mais moderno
- Area institucional centralizada
- Bloco institucional reduzido para dar mais destaque ao login
- Modal de cadastro mantido integrado ao fluxo principal

## Mensagens e comportamento

- Apos envio do codigo, a interface orienta o usuario a verificar tambem `Spam` e `Lixo eletronico`
- O mesmo aviso aparece dentro da etapa de digitacao do codigo
- Apos cadastro concluido, o sistema retorna para a tela de login

## Arquivos principais

- `site_samela/settings.py`
- `accounts/auth_backends.py`
- `accounts/views.py`
- `accounts/forms.py`
- `accounts/models.py`
- `accounts/migrations/0002_budget_and_login_name.py`
- `templates/accounts/login.html`
- `templates/accounts/dashboard.html`
- `templates/accounts/budget_product_form.html`
- `templates/accounts/budget_ready.html`
- `static/css/app.css`

## Git e fluxo de trabalho

- Sempre que houver alteracao no projeto:
  - atualizar este documento com o novo contexto
  - criar um novo commit
  - enviar `push` para o GitHub

## Historico de contexto

### 2026-06-02

- Projeto Django criado do zero
- Fluxo de autenticacao e cadastro implementado
- SMTP com Hotmail testado e descartado por bloqueio de autenticacao basica
- SMTP com Gmail configurado localmente e validado com sucesso
- Interface inicial refinada visualmente
- Lista visivel de e-mails autorizados removida da tela de cadastro
- Regra definida para manter este documento atualizado a cada alteracao e sempre versionar com commit e push
- Titulo institucional restaurado para `Orcamento - FAPESP - Fundacao Bracell Fundacao Itau`
- Etapa de digitacao do codigo atualizada para exibir tambem o aviso sobre verificar Spam e Lixo eletronico
- Autenticacao ampliada para aceitar login por alias ou e-mail
- Contas seeded criadas para `adm / 123` e `fabiano / 123`
- Credenciais seeded mantidas apenas no backend, sem exibicao visual na tela de login
- Painel pos-login criado com botoes para `Cadastrar campos` e `Acessar orcamento pronto`
- Topico `5.1. Custeio do projeto de pesquisa` implementado com cadastro de produto, 3 orcamentos e selecao para soma total
- Texto do selo principal da home simplificado de `Portal Academico` para `Portal`
