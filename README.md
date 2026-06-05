# SITE-SAMELA

Projeto Django com SQLite para o portal acadêmico NEEVY - UFSCar.

## O que já está pronto

- Tela inicial de login com tema acadêmico moderno
- Cadastro com modal em 3 etapas
- Restrição de cadastro apenas para e-mails autorizados
- Envio de código curto por e-mail
- Criação de senha com confirmação
- E-mail final de confirmação após cadastro
- Painel autenticado após login
- Tela dinâmica de `Cadastrar custos` com:
  - tópicos
  - campos
  - subcampos
  - novo custo baseado na estrutura criada

## Requisitos

- Python 3.10+
- Django 5.2.12
- Gunicorn 23.0.0 para produção

## Instalação local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Acesso local

- Login inicial: `http://127.0.0.1:8000/`
- Admin Django: `http://127.0.0.1:8000/admin/`

## Envio de e-mails

Por padrão, o projeto usa o backend de console do Django. Isso significa que os e-mails aparecem no terminal durante o desenvolvimento.

Se quiser enviar e-mails reais, configure estas variáveis de ambiente antes de subir o servidor:

```powershell
$env:DJANGO_EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:DJANGO_EMAIL_HOST="smtp.seuprovedor.com"
$env:DJANGO_EMAIL_PORT="587"
$env:DJANGO_EMAIL_HOST_USER="seu_usuario"
$env:DJANGO_EMAIL_HOST_PASSWORD="sua_senha"
$env:DJANGO_EMAIL_USE_TLS="true"
$env:DJANGO_DEFAULT_FROM_EMAIL="nao-responda@seudominio.com"
python manage.py runserver
```

## E-mails autorizados para cadastro

- mmello@ufscar.br
- samelapolloni@estudante.ufscar.br
- agarayhj@gmail.com
- ca_zanfelice@yahoo.com.br
- caopavani@gmail.com
- elsieperezserrano@gmail.com
- francielledemattos@gmail.com
- franciscofn@estudante.ufscar.br
- merteles@estudante.ufscar.br
- priscila.mattos@usp.br
- fabianopolone@hotmail.com

## Deploy isolado no VPS

Este projeto foi preparado para rodar de forma independente em:

- `https://fabianopolone.com.br/OrcamentoNeevy/`

Sem impactar outros sistemas já publicados no mesmo VPS.

### Estratégia recomendada

- pasta isolada do projeto
- ambiente virtual isolado
- serviço `systemd` próprio
- Gunicorn em porta interna exclusiva
- Nginx encaminhando apenas `/OrcamentoNeevy/`

### Estrutura sugerida no servidor

```bash
/var/www/site_samela_faculdade
/var/www/site_samela_faculdade/.venv
/var/www/site_samela_faculdade/deploy/.env
```

### 1. Clonar o projeto

```bash
cd /var/www
git clone https://github.com/fabianopolone123/site_samela_faculdade.git
cd site_samela_faculdade
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Criar o arquivo de ambiente

Use `deploy/.env.example` como base e crie:

```bash
/var/www/site_samela_faculdade/deploy/.env
```

Para este cenário, os pontos mais importantes são:

```env
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=fabianopolone.com.br,www.fabianopolone.com.br
DJANGO_CSRF_TRUSTED_ORIGINS=https://fabianopolone.com.br,https://www.fabianopolone.com.br
DJANGO_FORCE_SCRIPT_NAME=/OrcamentoNeevy
DJANGO_STATIC_ROOT=/var/www/site_samela_faculdade/staticfiles
```

### 3. Rodar migrações e coletar estáticos

```bash
cd /var/www/site_samela_faculdade
source .venv/bin/activate
export $(grep -v '^#' deploy/.env | xargs)
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Criar o serviço do Gunicorn

Copie o arquivo:

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/site_samela_orcamento.service
sudo systemctl daemon-reload
sudo systemctl enable site_samela_orcamento.service
sudo systemctl start site_samela_orcamento.service
sudo systemctl status site_samela_orcamento.service
```

Esse serviço usa:

- Gunicorn próprio
- porta interna `127.0.0.1:8101`
- sem conflito com os outros projetos

### 5. Adicionar o bloco no Nginx

No server block já existente de `fabianopolone.com.br`, inclua o conteúdo de:

```bash
deploy/nginx-location.conf
```

Isso cria:

- `location /OrcamentoNeevy/static/`
- `location /OrcamentoNeevy/`

Depois valide e recarregue:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 6. URL final

Depois disso, o sistema deve abrir em:

```text
https://fabianopolone.com.br/OrcamentoNeevy/
```

## Variáveis de ambiente suportadas

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_FORCE_SCRIPT_NAME`
- `DJANGO_STATIC_ROOT`
- `DJANGO_STATIC_URL`
- `DJANGO_DB_ENGINE`
- `DJANGO_DB_NAME`
- `DJANGO_EMAIL_BACKEND`
- `DJANGO_EMAIL_HOST`
- `DJANGO_EMAIL_PORT`
- `DJANGO_EMAIL_HOST_USER`
- `DJANGO_EMAIL_HOST_PASSWORD`
- `DJANGO_EMAIL_USE_TLS`
- `DJANGO_DEFAULT_FROM_EMAIL`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`
- `DJANGO_SECURE_SSL_REDIRECT`

## Testes

```powershell
python manage.py test accounts
python manage.py check
```
