# Contexto do Projeto

## Identificação

- Nome do repositório: `site_samela_faculdade`
- Base técnica: `Django + Python + SQLite`
- Objetivo atual: portal acadêmico com autenticação controlada e módulo de orçamento em evolução

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
- O fluxo atual suporta:
  - cadastro de tópicos
  - cadastro de campos
  - cadastro de subcampos
  - formulário de `Novo custo` gerado a partir da estrutura do tópico
  - lista dos registros já salvos no tópico
- Tipos de campo disponíveis:
  - `Texto`
  - `Número`
  - `Link`
  - `Valor`

## Modelos dinâmicos do novo fluxo

- `CostTopic`
  - representa um tópico de orçamento
- `CostField`
  - representa campo ou subcampo de um tópico
- `CostRecord`
  - representa um novo custo salvo em um tópico
- `CostRecordValue`
  - guarda o valor preenchido para cada campo do registro

## Seed padrão dos tópicos

- Os tópicos e campos padrão agora são criados automaticamente por migração de dados
- A migration `accounts/migrations/0007_seed_default_cost_topics.py`:
  - normaliza o tópico antigo de material permanente caso exista com nome incorreto
  - cria os tópicos padrão ausentes
  - cria os campos e subcampos padrão de cada tópico
- Isso evita depender de banco local copiado ou cadastro manual para o módulo `Cadastrar custos`

## Estruturas e tópicos já montados

- `Material permanente adquirido no país e importado`
- `Material de consumo adquirido no país e importado`
- `Serviços de Terceiros contratados no país e no exterior`
- `Despesas de Transporte e Diárias`
- `Bolsas como Item Orçamentário`
- `Bolsas — Iniciação Científica`
- `Bolsas — Mestrado`
- `Bolsas — Doutorado Direto`
- `Bolsas — Doutorado`
- `Bolsas — Pós-Doutorado`
- `Bolsas — Jornalismo Científico (JC)`
- `Bolsas — Treinamento Técnico e Participação em Curso`
- `Bolsas — Ensino Público - Aperfeiçoamento Pedagógico (EP)`
- `Bolsas — EP-1 Aperfeiçoamento Pedagógico`
- `Bolsas — EP-2 Aperfeiçoamento Pedagógico`
- `Bolsas — EP-3 Aperfeiçoamento Pedagógico`
- `Bolsas — EP-4 Aperfeiçoamento Pedagógico`
- `Bolsas — EP-5 Aperfeiçoamento Pedagógico`
- `Bolsas — EP-6 Aperfeiçoamento Pedagógico`

## Regras e comportamento do orçamento dinâmico

- Para materiais permanentes e materiais de consumo:
  - Nome do produto
  - Orçamento 1, 2 e 3
  - campos de preço, link, quantidade e frete
  - campo para selecionar qual orçamento entra na soma
- Para serviços de terceiros:
  - Nome do serviço
  - Orçamento 1, 2 e 3
  - preço, link e frete
- Para transporte e diárias:
  - estrutura própria por tópico
- Para bolsas:
  - valor por estudante
  - quantidade
  - duração em meses
  - campos específicos conforme a modalidade
- No formulário de `Novo custo`, campos raiz que funcionam como agrupadores podem aparecer só como cabeçalho do bloco, sem input redundante
- Existe cálculo de total por registro com base no orçamento selecionado
- Existe exibição de total geral acima da lista de registros do tópico quando aplicável

## Orçamento pronto

- A tela `Orçamento pronto` continua disponível
- Agora ela usa os `CostTopic` e `CostRecord` do construtor dinâmico
- O texto institucional do projeto continua exibido nessa tela
- Cada tópico mostra apenas os cadastros realmente salvos naquele tópico
- O total do tópico e o total geral passam a refletir os registros dinâmicos cadastrados
- Cada cadastro aparece em formato resumido e, ao clicar, abre uma janela suspensa com os detalhes
- Quando um detalhe contém campo do tipo link, a janela suspensa exibe botão para abrir o endereço no navegador
- Cada cadastro pode ser excluído na própria janela de detalhes
- Cada tópico pode ser excluído com confirmação, removendo junto os custos vinculados
- Campos monetários agora aceitam vírgula na digitação e são exibidos em padrão PT-BR

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
  - organização por blocos de campo principal com subcampos agrupados visualmente
- O modal de campos do tópico já foi ampliado para suportar gestão mais direta da estrutura
- A lista de registros em `Cadastrar custos` agora mostra só o nome principal de cada cadastro
- Os detalhes completos de cada cadastro ficam em modal, ao clicar no item salvo

## Preparação para produção

- O projeto foi adaptado para configuração por variáveis de ambiente
- Foi adicionada preparação para subir em subpasta:
  - `https://fabianopolone.com.br/OrcamentoNeevy/`
- O `settings.py` agora suporta:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG`
  - `DJANGO_ALLOWED_HOSTS`
  - `DJANGO_CSRF_TRUSTED_ORIGINS`
  - `DJANGO_FORCE_SCRIPT_NAME`
  - `DJANGO_STATIC_ROOT`
  - `DJANGO_STATIC_URL`
- O projeto passou a incluir `gunicorn` no `requirements.txt`
- Foram criados arquivos de deploy isolado:
  - `deploy/.env.example`
  - `deploy/gunicorn.service`
  - `deploy/nginx-location.conf`
- A estratégia de deploy preparada é isolada:
  - diretório próprio
  - virtualenv próprio
  - serviço `systemd` próprio
  - porta interna exclusiva
  - bloco `location` específico no Nginx

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
- `deploy/.env.example`
- `deploy/gunicorn.service`
- `deploy/nginx-location.conf`

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
- A tela `Cadastrar custos` passou a permitir montar a estrutura e registrar novos custos com base no tópico selecionado

### 2026-06-03

- Tópicos principais de materiais, serviços, transporte, diárias e bolsas foram estruturados
- A área de `Novo custo` foi reorganizada para ficar mais clara, separando cada campo principal em um bloco próprio e mantendo os subcampos logo abaixo
- Campos adicionais como frete, seleção de orçamento e descrições de tópico foram incorporados ao fluxo
- Regras de cálculo por orçamento selecionado passaram a aparecer nos registros do tópico

### 2026-06-04

- O projeto foi preparado para deploy isolado em VPS com Gunicorn e Nginx na rota `/OrcamentoNeevy/`
- Os tópicos e campos padrão de `Cadastrar custos` passaram a nascer automaticamente por seed via migração

### 2026-06-05

- `Orçamento pronto` passou a refletir os tópicos e registros do construtor dinâmico
- Os registros salvos em `Cadastrar custos` passaram a aparecer de forma resumida, com detalhes em janela suspensa
- Foi criada a migration `accounts/migrations/0008_alter_budgetcostentry_selected_quote_number_and_more.py` para sincronizar campos legados do orçamento antigo e eliminar o aviso de migração pendente no deploy
- Foi criada a migration `accounts/migrations/0009_normalize_ptbr_texts.py` para corrigir textos quebrados e normalizar acentuação em tópicos, campos e seções já salvos no banco
- O painel principal passou a exibir o botão `Auditoria` apenas para o login `adm`
- Foi criada a migration `accounts/migrations/0010_auditlog.py` com o modelo `AuditLog`
- A auditoria registra cadastros, alterações e exclusões de tópicos, campos e custos, com usuário responsável e data/hora
- Foi criada a tela `templates/accounts/audit_log.html` para consulta do histórico administrativo
- O cálculo do total do orçamento selecionado passou a considerar `preço × quantidade + frete`
- Campos do tipo `Link` agora só exibem o botão `Abrir link` quando o valor salvo for uma URL válida
- Foi criada a migration `accounts/migrations/0011_allowedsignupemail.py` com o modelo `AllowedSignupEmail`
- O login `adm` ganhou a tela `E-mails autorizados`, com cadastro e remoção de e-mails liberados para inscrição
- O fluxo de inscrição agora aceita a união entre a lista fixa do `settings.py` e os e-mails dinâmicos cadastrados pelo `adm`
- Cadastros e remoções de e-mails autorizados também entram na auditoria administrativa
