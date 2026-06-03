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
  - seção `Novo custo` organizada por blocos de campo principal, com subcampos agrupados visualmente no mesmo bloco

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
- A área de `Novo custo` foi reorganizada para ficar mais clara, separando cada campo principal em um bloco próprio e mantendo os subcampos logo abaixo

### 2026-06-03

- Tópico `Material permanente adquirido no país e importado` criado via Django shell com campos: Nome do produto, Orçamento 1/2/3 (Preço, Link, Quantidade), Selecionar para orçar
- Interface de `Cadastrar custos` reestruturada: ao selecionar um tópico, a área principal exibe apenas dois botões de ação e a lista de registros
- Botão `Campos do tópico` abre modal com a estrutura de campos cadastrados (com botão de exclusão por campo/subcampo) e formulário de adição inline
- Botão `Novo custo` abre modal com o formulário dinâmico de preenchimento
- Após adicionar ou excluir campo, o modal `Campos do tópico` reabre automaticamente via parâmetro `?open=campos` na URL
- Adicionada view `delete_topic_field_view` e rota `cadastrar-campos/campos/<id>/excluir/` para exclusão de campos
- Botão `Novo custo` fica desabilitado enquanto não houver campos cadastrados no tópico
- Novos estilos CSS: `.modal-content--wide`, `.topic-action-header`, `.campos-modal-body`, `.campos-add-grid`, `.icon-button--danger`, `.action-badge`, entre outros
- No formulário "Novo custo", campos raiz que possuem subcampos são renderizados apenas como cabeçalho de grupo, sem input de texto — evita campo redundante nos agrupadores como "Orçamento 1", "Orçamento 2", "Orçamento 3"
- Campo "Frete" (tipo valor) adicionado como subcampo de Orçamento 1, 2 e 3 no tópico "Material permanente"
- No modal "Novo custo", o campo Preço e o campo Frete de cada orçamento calculam ao vivo o Total (Preço + Frete) via JavaScript
- Lógica de cálculo de total por registro: a view identifica o campo "Selecionar para orçar", localiza o grupo "Orçamento N" correspondente e soma Preço + Frete
- Card de total geral exibido acima da lista de registros, mostrando a soma dos orçamentos selecionados em todos os registros
- Cada registro na lista exibe o total do orçamento selecionado
- `get_selected_total_for_record()` adicionado ao views.py para cálculo por registro
- `build_record_cards()` atualizado para retornar tupla `(records, grand_total)`
- `build_topic_groups()` atualizado para incluir `field_role` (preco/frete) e `has_price_calc` por grupo
- Tópico `Material de consumo adquirido no país e importado` criado com estrutura idêntica ao de Material permanente: Nome do produto, Orçamento 1/2/3 (Preço, Link, Quantidade, Frete), Selecionar para orçar
- Tópico `Serviços de Terceiros contratados no país e no exterior` criado: Nome do serviço, Orçamento 1/2/3 (Preço, Link, Frete — sem Quantidade), Selecionar para orçar
- Campo `description` (TextField) adicionado ao modelo `CostTopic` via migration 0006
- Caixa de observação exibida na área principal de cada tópico; botão "✎" abre modal para editar
- Tópicos sem descrição exibem link "+ Adicionar observação ao tópico"
- Descrições pre-populadas para Material permanente e Serviços de Terceiros
- Tópico `Despesas de Transporte e Diárias` criado: Nome do meio de transporte, Origem, Destino, Orçamento 1/2/3 (Preço, Link — sem Frete/Quantidade), Selecionar para orçar
- Tópico `Bolsas como Item Orçamentário` criado: Modalidade da bolsa, Valor orçamentário (por estudante), Quantidade de estudantes, Duração em meses — sem orçamentos comparativos pois valor é tabelado pela FAPESP
- Tópico `Bolsas — Iniciação Científica` criado: Valor orçamentário (por estudante), Quantidade de estudantes, Duração em meses; descrição específica da modalidade IC
- Tópico `Bolsas — Mestrado` criado: mesmos campos; descrição específica da modalidade Mestrado
- Tópico `Bolsas — Doutorado Direto` criado: mesmos campos; mesma descrição do Mestrado
- Tópico `Bolsas — Doutorado` criado: mesmos campos; mesma descrição do Mestrado
- Tópico `Bolsas — Pós-Doutorado` criado: mesmos campos; descrição específica com exigência de processo seletivo internacional
- Tópico `Bolsas — Jornalismo Científico (JC)` criado: mesmos campos; descrição padrão fapesp.br/bco
- Tópico `Bolsas — Treinamento Técnico e Participação em Curso` criado: mesmos campos
- Tópico `Bolsas — Ensino Público - Aperfeiçoamento Pedagógico (EP)` criado: Valor orçamentário (por candidato), Quantidade de candidatos, Duração em meses
- Tópico `Bolsas — EP-1 Aperfeiçoamento Pedagógico` criado: mesmos campos; para candidatos com nível superior, dedicação de 4h semanais
- Tópico `Bolsas — EP-2 Aperfeiçoamento Pedagógico` criado: mesmos campos; para candidatos com nível superior, dedicação de 8h semanais
- Tópico `Bolsas — EP-3 Aperfeiçoamento Pedagógico` criado: mesmos campos; para candidatos com Mestrado concluído, dedicação de 4h semanais
- Tópico `Bolsas — EP-4 Aperfeiçoamento Pedagógico` criado: mesmos campos; para candidatos com Mestrado concluído, dedicação de 8h semanais
- Tópico `Bolsas — EP-5 Aperfeiçoamento Pedagógico` criado: mesmos campos; para candidatos com Doutorado concluído, dedicação de 4h semanais
