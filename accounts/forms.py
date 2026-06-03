from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Usuário',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Digite seu e-mail autorizado',
                'autocomplete': 'username',
            }
        ),
    )
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Digite sua senha',
                'autocomplete': 'current-password',
            }
        ),
    )


class SignupEmailForm(forms.Form):
    email = forms.EmailField(
        label='E-mail autorizado',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'nome@instituicao.br',
                'autocomplete': 'email',
            }
        ),
    )


class SignupCodeForm(forms.Form):
    code = forms.CharField(
        label='Código de verificação',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'placeholder': '000000',
                'inputmode': 'numeric',
                'autocomplete': 'one-time-code',
            }
        ),
    )


class SignupPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Crie uma senha',
                'autocomplete': 'new-password',
            }
        ),
    )
    password2 = forms.CharField(
        label='Confirmar senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Repita a senha',
                'autocomplete': 'new-password',
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas informadas não coincidem.')

        if password1 and len(password1) < 8:
            raise forms.ValidationError('A senha precisa ter pelo menos 8 caracteres.')

        return cleaned_data
