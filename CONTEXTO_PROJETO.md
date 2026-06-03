# Contexto do Projeto

## Identificação

- Nome do repositório: `site_samela_faculdade`
- Base técnica: `Django + Python + SQLite`
- Objetivo atual: portal acadêmico com autenticação controlada e módulo de orçamento por categorias

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
- Tela inicial autenticada simplificada para exibir apenas um card central com os botões principais

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

## Estrutura atual do orçamento

- O projeto exibido em `Orçamento pronto` é:
  - `INDICADORES E CRITÉRIOS DE AVALIAÇÃO DE DESENVOLVIMENTO CULTURAL DE CRIANÇAS DE PRÉ-ESCOLA NA THC`
- O texto institucional de orçamento já aparece na tela pronta
- O módulo `Cadastrar custos` agora aceita estas categorias:
  - `a) Material permanente adquirido no país ou importado`
  - `b) Material de consumo adquirido no país ou importado`
  - `c) Serviços de terceiros contratados no país ou no exterior`
  - `d.1) Transporte`
  - `d.2) Diárias`
  - `e) Bolsas como item orçamentário`

## Campos e comportamento do orçamento

- Materiais permanentes e de consumo:
  - descrição principal
  - detalhes
  - quantidade
  - 3 orçamentos com valor e link
  - orçamento selecionado para a soma
- Exceção específica para `a) Material permanente`:
  - manter apenas `Nome do produto`
  - em cada um dos 3 orçamentos informar `link`, `preço`, `quantidade` e `frete`
  - total considerado = `(preço × quantidade) + frete` do orçamento selecionado
  - rótulos visuais da categoria `a)` ajustados para remover nomenclatura genérica
- Serviços de terceiros:
  - serviço solicitado
  - justificativa
  - quantidade
  - unidade
  - 3 orçamentos com valor e link
  - orçamento selecionado
- Transporte:
  - meio de transporte
  - origem
  - destino
  - finalidade
  - quantidade de pessoas
  - 3 orçamentos com valor e link
  - orçamento selecionado
- Diárias:
  - tipo de diária
  - localidade
  - quantidade de pessoas
  - número de dias
  - valor unitário
- Bolsas:
  - modalidade
  - quantidade
  - duração em meses quando aplicável
  - valor mensal ou valor do curso
  - justificativa
  - formação exigida e dedicação semanal quando a modalidade for Ensino Público

## Regras de cálculo atuais

- Categorias com 3 orçamentos:
  - o sistema considera o orçamento selecionado
  - o total é calculado com base no valor selecionado e na quantidade
- Diárias:
  - total = quantidade de pessoas × número de dias × valor unitário
- Bolsas:
  - total = quantidade × duração × valor mensal
  - para `Participação em Curso`, total = quantidade × valor do curso
- A tela `Orçamento pronto` mostra:
  - cada seção individual
  - total por seção
  - síntese por categoria
  - total geral do projeto

## Ajustes visuais e textuais

- Página inicial redesenhada com layout mais moderno
- Área institucional centralizada
- Bloco institucional reduzido para dar mais destaque ao login
- Modal de cadastro mantido integrado ao fluxo principal
- Credenciais seeded mantidas apenas no backend, sem exibição visual na tela de login
- Regra definida para manter textos em português sempre com acentuação correta
- Seletor de categorias de `Cadastrar custos` transformado em cards visuais
- Ao selecionar uma categoria, o formulário habilita dinamicamente apenas os campos correspondentes
- O painel lateral de `Cadastrar custos` passou a mostrar os itens já cadastrados da categoria selecionada
- O seletor voltou para lista suspensa estilizada e os campos não relacionados agora ficam invisíveis
- A área de `Orçamento selecionado` foi redesenhada com opções em cards e resumo visual da escolha ativa

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
- `accounts/migrations/0003_budget_cost_entry.py`
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
- Módulo de orçamento expandido para materiais, serviços, transporte, diárias e bolsas
- Tela `Cadastrar custos` refinada com seletor visual e ativação dinâmica dos campos por categoria
- Área lateral da tela de cadastro ajustada para acompanhar a categoria selecionada e listar seus itens salvos
- Campos não relacionados à categoria escolhida passam a ser ocultados completamente
- Categoria `a)` simplificada visualmente para mostrar apenas os campos solicitados
- Bloco de seleção do orçamento destacado visualmente para facilitar a decisão do usuário
- Regra definida para manter mensagens de commit sempre em português
