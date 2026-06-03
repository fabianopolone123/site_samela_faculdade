# Contexto do Projeto

## Identificação

- Nome do repositório: `site_samela_faculdade`
- Base técnica: `Django + Python + SQLite`
- Objetivo atual: portal acadêmico com autenticação controlada e módulo de orçamento em construção

## Escopo implementado

- Tela inicial com tema acadêmico moderno
- Login por login ou e-mail e senha
- Cadastro em modal com 3 etapas:
  - validação de e-mail autorizado
  - envio de código curto por e-mail
  - criação e confirmação de senha
- Painel autenticado com dois acessos principais:
  - `Cadastrar custos`
  - `Acessar orçamento pronto`

## Logins seeded

- Login ADM: `adm`
- Senha ADM: `123`
- Login teste: `fabiano`
- Senha teste: `123`

## Regras de cadastro

- Apenas e-mails autorizados podem criar conta
- A lista de e-mails autorizados fica no backend em `site_samela/settings.py`
- A lista visível de e-mails autorizados foi removida da interface
- O e-mail `fabianopolone@hotmail.com` está liberado para cadastro

## Módulo Cadastrar Custos

- A rota `http://127.0.0.1:8000/cadastrar-campos/` foi refeita para um modelo dinâmico
- O fluxo atual funciona assim:
  - botão `Cadastrar tópico`
  - modal para informar o nome do tópico
  - o tópico salvo aparece na lista lateral
  - ao abrir um tópico, existe a opção `Criar campos`
  - cada campo pode ter:
    - nome
    - tipo
    - vínculo opcional com campo pai para virar subcampo
  - tipos disponíveis:
    - `Texto`
    - `Número`
    - `Link`
    - `Valor`
  - os subcampos usam os mesmos tipos dos campos principais
  - a seção `Novo custo` renderiza automaticamente os campos e subcampos do tópico selecionado
  - a seção `Custos já registrados` mostra os registros salvos no tópico atual

## Modelos dinâmicos do novo fluxo

- `CostTopic`
  - representa um tópico de orçamento
- `CostField`
  - representa campo ou subcampo de um tópico
- `CostRecord`
  - representa um novo custo salvo em um tópico
- `CostRecordValue`
  - guarda o valor preenchido para cada campo do registro

## Orçamento pronto

- A tela `Orçamento pronto` continua disponível
- Ela ainda usa a estrutura anterior de seções e itens de orçamento
- O texto institucional do projeto continua exibido nessa tela
- A integração completa entre o construtor dinâmico de tópicos e a tela `Orçamento pronto` ainda não foi iniciada

## Ajustes visuais e textuais

- Página inicial refinada com visual acadêmico moderno
- Área institucional centralizada e reduzida para dar destaque ao login
- Credenciais seeded ficam apenas no backend, sem exibição visual
- Regra definida para manter textos em português com acentuação correta
- A tela `Cadastrar custos` agora usa:
  - cabeçalho mais forte
  - lista lateral de tópicos
  - cards de estrutura do tópico
  - formulário dinâmico para novo custo
  - cards de registros salvos

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
- `accounts/admin.py`
- `accounts/tests.py`
- `accounts/migrations/0005_dynamic_topics_fields.py`
- `templates/accounts/login.html`
- `templates/accounts/dashboard.html`
- `templates/accounts/budget_product_form.html`
- `templates/accounts/budget_ready.html`
- `static/css/app.css`

## Git e fluxo de trabalho

- Sempre que houver alteração no projeto:
  - atualizar este documento com o novo contexto
  - criar um novo commit com mensagem em português
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
- Painel pós-login simplificado para exibir apenas os botões principais
- O fluxo antigo de categorias em `Cadastrar custos` foi substituído por um construtor dinâmico de tópicos, campos e subcampos
- A tela `Cadastrar custos` agora permite montar a estrutura e registrar novos custos com base no tópico selecionado
