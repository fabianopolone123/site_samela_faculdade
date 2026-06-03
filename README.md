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
- Módulo inicial de orçamento no tópico `5.1`

## Requisitos

- Python 3.10+
- Django 5.2.12

## Instalação

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Acesso

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

## Testes

```powershell
python manage.py test
```
