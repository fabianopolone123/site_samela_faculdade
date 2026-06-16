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
                if field.id not in excluded_ids and field.is_active
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


class FieldMigrationForm(forms.Form):
    source_field_ids = forms.MultipleChoiceField(
        label='Campos antigos que serão unidos',
        choices=[],
        widget=forms.SelectMultiple(attrs={'size': 8}),
    )
    target_field_id = forms.ChoiceField(
        label='Campo novo de destino',
        choices=[],
    )
    record_id = forms.ChoiceField(
        label='Custo para teste',
        required=False,
        choices=[],
    )
    archive_source_fields = forms.BooleanField(
        label='Arquivar os campos antigos ao aplicar em todos',
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        topic = kwargs.pop('topic', None)
        record_choices = kwargs.pop('record_choices', None)
        super().__init__(*args, **kwargs)
        self.fields['record_id'].choices = [('', 'Selecione um custo para testar')]
        if record_choices:
            self.fields['record_id'].choices += record_choices

        if topic is not None:
            active_fields = [
                field for field in topic.fields.all()
                if field.is_active
            ]
            source_grouped_choices = self._build_grouped_field_choices(active_fields)
            new_target_fields = [
                field for field in active_fields
                if not field.record_values.exists()
            ]
            target_grouped_choices = self._build_grouped_field_choices(new_target_fields)
            self.fields['source_field_ids'].choices = source_grouped_choices
            self.fields['target_field_id'].choices = [('', 'Selecione o campo novo')] + target_grouped_choices

    def _build_grouped_field_choices(self, fields):
        children_map = {}
        for field in fields:
            children_map.setdefault(field.parent_id, []).append(field)

        def build_option_label(field):
            if field.parent_id is None:
                return 'Campo principal'
            path = []
            current = field
            while current is not None and current.parent_id is not None:
                path.append(current.name)
                current = current.parent
            return ' / '.join(reversed(path))

        grouped_choices = []

        def append_descendants(options, parent):
            for child in children_map.get(parent.id, []):
                options.append((str(child.id), build_option_label(child)))
                append_descendants(options, child)

        for root in children_map.get(None, []):
            options = [(str(root.id), build_option_label(root))]
            append_descendants(options, root)
            grouped_choices.append((root.name, options))

        return grouped_choices
