from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('painel/', views.dashboard_view, name='dashboard'),
    path('emails-autorizados/', views.allowed_signup_emails_view, name='allowed_signup_emails'),
    path('emails-autorizados/novo/', views.create_allowed_signup_email_view, name='create_allowed_signup_email'),
    path('emails-autorizados/<int:email_id>/excluir/', views.delete_allowed_signup_email_view, name='delete_allowed_signup_email'),
    path('auditoria/', views.audit_log_view, name='audit_log'),
    path('cadastrar-campos/', views.budget_product_create_view, name='budget_product_create'),
    path('cadastrar-campos/topicos/', views.create_topic_view, name='create_topic'),
    path('cadastrar-campos/topicos/<int:topic_id>/excluir/', views.delete_topic_view, name='delete_topic'),
    path('cadastrar-campos/campos/', views.create_topic_field_view, name='create_topic_field'),
    path('cadastrar-campos/novo-custo/', views.create_topic_record_view, name='create_topic_record'),
    path('cadastrar-campos/custos/<int:record_id>/editar/', views.update_topic_record_view, name='update_topic_record'),
    path('cadastrar-campos/custos/<int:record_id>/excluir/', views.delete_topic_record_view, name='delete_topic_record'),
    path('cadastrar-campos/campos/<int:field_id>/excluir/', views.delete_topic_field_view, name='delete_topic_field'),
    path('cadastrar-campos/campos/<int:field_id>/editar/', views.update_topic_field_view, name='update_topic_field'),
    path('cadastrar-campos/topicos/<int:topic_id>/descricao/', views.update_topic_description_view, name='update_topic_description'),
    path('orcamento-pronto/', views.budget_ready_view, name='budget_ready'),
    path('orcamento-pronto/pdf/', views.budget_ready_pdf_view, name='budget_ready_pdf'),
    path('orcamento-pronto/pdf-selecionados/', views.budget_ready_selected_pdf_view, name='budget_ready_selected_pdf'),
    path('orcamento-pronto/word/', views.budget_ready_docx_view, name='budget_ready_docx'),
    path('cadastro/email/', views.signup_email_view, name='signup_email'),
    path('cadastro/codigo/', views.signup_code_view, name='signup_code'),
    path('cadastro/senha/', views.signup_password_view, name='signup_password'),
    path('cadastro/cancelar/', views.signup_reset_view, name='signup_reset'),
]
