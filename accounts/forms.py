from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Digite seu login ou e-mail',
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


class BudgetProductForm(forms.Form):
    name = forms.CharField(
        label='Nome do produto',
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Ex.: tablet educacional, impressora, câmera'}
        ),
    )
    selected_quote = forms.ChoiceField(
        label='Orçamento selecionado para a soma total',
        choices=[('1', 'Orçamento 1'), ('2', 'Orçamento 2'), ('3', 'Orçamento 3')],
        widget=forms.RadioSelect,
    )

    quote_1_price = forms.DecimalField(label='Preço orçamento 1', decimal_places=2, max_digits=12, min_value=0)
    quote_1_quantity = forms.IntegerField(label='Quantidade orçamento 1', min_value=1)
    quote_1_link = forms.URLField(label='Link orçamento 1')

    quote_2_price = forms.DecimalField(label='Preço orçamento 2', decimal_places=2, max_digits=12, min_value=0)
    quote_2_quantity = forms.IntegerField(label='Quantidade orçamento 2', min_value=1)
    quote_2_link = forms.URLField(label='Link orçamento 2')

    quote_3_price = forms.DecimalField(label='Preço orçamento 3', decimal_places=2, max_digits=12, min_value=0)
    quote_3_quantity = forms.IntegerField(label='Quantidade orçamento 3', min_value=1)
    quote_3_link = forms.URLField(label='Link orçamento 3')


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
