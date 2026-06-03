from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('painel/', views.dashboard_view, name='dashboard'),
    path('cadastro/email/', views.signup_email_view, name='signup_email'),
    path('cadastro/codigo/', views.signup_code_view, name='signup_code'),
    path('cadastro/senha/', views.signup_password_view, name='signup_password'),
    path('cadastro/cancelar/', views.signup_reset_view, name='signup_reset'),
]
