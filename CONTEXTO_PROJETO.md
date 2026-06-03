# Contexto do Projeto

## Identificação

- Nome do repositório: `site_samela_faculdade`
- Base técnica: `Django + Python + SQLite`
- Objetivo atual: portal acadêmico com autenticação controlada e módulo inicial de orçamento

## Escopo implementado

- Tela inicial com tema acadêmico moderno
- Login por login ou e-mail e senha
- Cadastro em modal com 3 etapas:
  - validação de e-mail autorizado
  - envio de código curto por e-mail
  - criação e confirmação de senha
- Painel autenticado com dois acessos principais:
  - `Cadastrar campos`
  - `Acessar orçamento pronto`
- Módulo inicial do tópico `5.1. Custeio do projeto de pesquisa`
- Cadastro de produto com exatamente 3 orçamentos
- Cada orçamento possui:
  - preço
  - quantidade
  - link
- Um dos 3 orçamentos pode ser marcado para entrar na soma total
- Tela `Orçamento pronto` alimentada pelos dados cadastrados

## Logins de acesso seeded

- Login ADM: `adm`
- Senha ADM: `123`
- Login teste: `fabiano`
- Senha teste: `123`

## Regras de cadastro

- Apenas e-mails autorizados podem criar conta
- A lista de e-mails autorizados fica no backend em `site_samela/settings.py`
- A lista visível de e-mails autorizados foi removida da interface
- O e-mail `fabianopolone@hotmail.com` foi adicionado à whitelist

## Regras do orçamento atual

- O projeto exibido em `Orçamento pronto` é:
  - `INDICADORES E CRITÉRIOS DE AVALIAÇÃO DE DESENVOLVIMENTO CULTURAL DE CRIANÇAS DE PRÉ-ESCOLA NA THC`
- O texto institucional de orçamento já aparece na tela pronta
- O primeiro tópico ativo é `5.1`
- Os próximos tópicos ainda serão adicionados depois

## Ajustes visuais e textuais

- Página inicial redesenhada com layout mais moderno
- Área institucional centralizada
- Bloco institucional reduzido para dar mais destaque ao login
- Modal de cadastro mantido integrado ao fluxo principal
- Credenciais seeded mantidas apenas no backend, sem exibição visual na tela de login
- Regra definida para manter textos em português sempre com acentuação correta

## Mensagens e comportamento

- Após envio do código, a interface orienta o usuário a verificar também `Spam` e `Lixo eletrônico`
- O mesmo aviso aparece dentro da etapa de digitação do código
- Após cadastro concluído, o sistema retorna para a tela de login

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

- Sempre que houver alteração no projeto:
  - atualizar este documento com o novo contexto
  - criar um novo commit
  - enviar `push` para o GitHub

## Histórico de contexto

### 2026-06-02

- Projeto Django criado do zero
- Fluxo de autenticação e cadastro implementado
- SMTP com Hotmail testado e descartado por bloqueio de autenticação básica
- SMTP com Gmail configurado localmente e validado com sucesso
- Interface inicial refinada visualmente
- Lista visível de e-mails autorizados removida da tela de cadastro
- Regra definida para manter este documento atualizado a cada alteração e sempre versionar com commit e push
- Título institucional restaurado para `Orçamento - FAPESP - Fundação Bracell Fundação Itaú`
- Etapa de digitação do código atualizada para exibir também o aviso sobre verificar Spam e Lixo eletrônico
- Autenticação ampliada para aceitar login por alias ou e-mail
- Contas seeded criadas para `adm / 123` e `fabiano / 123`
- Painel pós-login criado com botões para `Cadastrar campos` e `Acessar orçamento pronto`
- Tópico `5.1. Custeio do projeto de pesquisa` implementado com cadastro de produto, 3 orçamentos e seleção para soma total
