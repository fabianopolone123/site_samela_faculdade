# Contexto do Projeto

## Identificação

- Nome do repositório: `site_samela_faculdade`
- Base técnica: `Django + Python + SQLite`
- Objetivo atual: portal acadêmico com tela inicial de login e fluxo controlado de criação de conta por e-mail autorizado

## Escopo implementado

- Tela inicial com tema acadêmico moderno
- Login por e-mail e senha
- Cadastro em modal com 3 etapas:
  - validação de e-mail autorizado
  - envio de código curto por e-mail
  - criação e confirmação de senha
- Painel autenticado inicial após login
- Envio real de e-mail configurado localmente por SMTP Gmail via arquivo local não versionado

## Regras de cadastro

- Apenas e-mails autorizados podem criar conta
- A lista de e-mails autorizados fica no backend em `site_samela/settings.py`
- A lista visível de e-mails autorizados foi removida da interface
- O e-mail `fabianopolone@hotmail.com` foi adicionado à whitelist

## Ajustes visuais já feitos

- Página inicial redesenhada com layout mais moderno
- Área institucional centralizada
- Bloco institucional reduzido para dar mais destaque ao login
- Modal de cadastro mantido integrado ao fluxo principal

## Mensagens e comportamento

- Após envio do código, a interface orienta o usuário a verificar também `Spam` e `Lixo eletrônico`
- Após cadastro concluído, o sistema retorna para a tela de login

## Arquivos principais

- `site_samela/settings.py`
- `site_samela/urls.py`
- `accounts/views.py`
- `accounts/forms.py`
- `accounts/models.py`
- `templates/accounts/login.html`
- `templates/accounts/dashboard.html`
- `static/css/app.css`
- `README.md`

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
