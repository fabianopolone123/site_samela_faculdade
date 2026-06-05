from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import CostField


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


class TopicForm(forms.Form):
    name = forms.CharField(
        label='Nome do tópico',
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Ex.: Material permanente ou Transporte'}
        ),
    )


class TopicDescriptionForm(forms.Form):
    description = forms.CharField(
        label='Observações / Regras do tópico',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 6,
                'placeholder': 'Descreva regras, limites ou observações relevantes para este tópico...',
            }
        ),
    )


class TopicFieldForm(forms.Form):
    name = forms.CharField(
        label='Nome do campo',
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Ex.: Nome do produto, Link, Preço'}
        ),
    )
    field_type = forms.ChoiceField(
        label='Tipo',
        choices=CostField.TYPE_CHOICES,
    )
    calculation_role = forms.ChoiceField(
        label='Função do campo',
        choices=CostField.CALCULATION_ROLE_CHOICES,
        required=False,
        initial=CostField.ROLE_NONE,
    )
    parent_id = forms.ChoiceField(
        label='Vincular como subcampo de',
        required=False,
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        topic = kwargs.pop('topic', None)
        current_field = kwargs.pop('current_field', None)
        super().__init__(*args, **kwargs)
        self.fields['parent_id'].choices = [('', 'Campo principal')]
        self.current_field = current_field
        if topic is not None:
            excluded_ids = set()
            if current_field is not None:
                excluded_ids.update(self._get_descendant_ids(current_field))
            self.fields['parent_id'].choices += [
                (str(field.id), field.name) for field in topic.fields.all()
                if field.id not in excluded_ids
            ]

    def clean(self):
        cleaned_data = super().clean()
        if self.current_field is not None:
            parent_id = cleaned_data.get('parent_id')
            if parent_id and str(self.current_field.id) == str(parent_id):
                raise forms.ValidationError('Um campo não pode ser vinculado a ele mesmo.')
        return cleaned_data

    def _get_descendant_ids(self, field):
        ids = {field.id}
        children = list(field.children.all())
        for child in children:
            ids.update(self._get_descendant_ids(child))
        return ids


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


class AllowedSignupEmailForm(forms.Form):
    email = forms.EmailField(
        label='Novo e-mail autorizado',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'nome@instituicao.br',
                'autocomplete': 'email',
            }
        ),
    )
