from django import forms
from django.contrib.auth.forms import AuthenticationForm


SECTION_CHOICES = [
    ('a', 'a) Material permanente adquirido no país ou importado'),
    ('b', 'b) Material de consumo adquirido no país ou importado'),
    ('c', 'c) Serviços de terceiros contratados no país ou no exterior'),
    ('d.1', 'd.1) Transporte'),
    ('d.2', 'd.2) Diárias'),
    ('e', 'e) Bolsas como item orçamentário'),
]

TRANSPORT_CHOICES = [
    ('Passagem aérea', 'Passagem aérea'),
    ('Passagem de ônibus', 'Passagem de ônibus'),
    ('Táxi/transporte por aplicativo', 'Táxi/transporte por aplicativo'),
    ('Combustível/pedágio', 'Combustível/pedágio'),
    ('Outro', 'Outro'),
]

DAILY_CHOICES = [
    ('Diária no país', 'Diária no país'),
    ('Diária no exterior', 'Diária no exterior'),
]

SCHOLARSHIP_CHOICES = [
    ('Iniciação Científica', 'Iniciação Científica'),
    ('Mestrado', 'Mestrado'),
    ('Doutorado Direto', 'Doutorado Direto'),
    ('Doutorado', 'Doutorado'),
    ('Pós-Doutorado', 'Pós-Doutorado'),
    ('Jornalismo Científico', 'Jornalismo Científico'),
    ('Treinamento Técnico', 'Treinamento Técnico'),
    ('Participação em Curso', 'Participação em Curso'),
    ('Ensino Público — Aperfeiçoamento Pedagógico', 'Ensino Público — Aperfeiçoamento Pedagógico'),
]

EDUCATION_CHOICES = [
    ('', 'Selecione'),
    ('Nível superior concluído', 'Nível superior concluído'),
    ('Mestrado concluído', 'Mestrado concluído'),
    ('Doutorado concluído', 'Doutorado concluído'),
]

WEEKLY_DEDICATION_CHOICES = [
    ('', 'Selecione'),
    ('4 horas', '4 horas'),
    ('8 horas', '8 horas'),
]


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


class BudgetCostForm(forms.Form):
    section_code = forms.ChoiceField(label='Categoria', choices=SECTION_CHOICES)
    title = forms.CharField(
        label='Descrição principal',
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Nome do produto, material, serviço ou item'}
        ),
    )
    details = forms.CharField(
        label='Detalhes',
        required=False,
        widget=forms.Textarea(
            attrs={'rows': 3, 'placeholder': 'Detalhes complementares do item'}
        ),
    )
    justification = forms.CharField(
        label='Justificativa',
        required=False,
        widget=forms.Textarea(
            attrs={'rows': 3, 'placeholder': 'Justificativa do item no projeto'}
        ),
    )
    quantity = forms.IntegerField(label='Quantidade', required=False, min_value=1)
    unit = forms.CharField(label='Unidade', required=False, max_length=100)
    selected_quote = forms.ChoiceField(
        label='Orçamento selecionado',
        required=False,
        choices=[('1', 'Orçamento 1'), ('2', 'Orçamento 2'), ('3', 'Orçamento 3')],
        widget=forms.RadioSelect,
    )

    quote_1_amount = forms.DecimalField(label='Valor orçamento 1', required=False, decimal_places=2, max_digits=12, min_value=0)
    quote_1_quantity = forms.IntegerField(label='Quantidade orçamento 1', required=False, min_value=1)
    quote_1_freight = forms.DecimalField(label='Frete orçamento 1', required=False, decimal_places=2, max_digits=12, min_value=0)
    quote_1_link = forms.URLField(label='Link orçamento 1', required=False)
    quote_2_amount = forms.DecimalField(label='Valor orçamento 2', required=False, decimal_places=2, max_digits=12, min_value=0)
    quote_2_quantity = forms.IntegerField(label='Quantidade orçamento 2', required=False, min_value=1)
    quote_2_freight = forms.DecimalField(label='Frete orçamento 2', required=False, decimal_places=2, max_digits=12, min_value=0)
    quote_2_link = forms.URLField(label='Link orçamento 2', required=False)
    quote_3_amount = forms.DecimalField(label='Valor orçamento 3', required=False, decimal_places=2, max_digits=12, min_value=0)
    quote_3_quantity = forms.IntegerField(label='Quantidade orçamento 3', required=False, min_value=1)
    quote_3_freight = forms.DecimalField(label='Frete orçamento 3', required=False, decimal_places=2, max_digits=12, min_value=0)
    quote_3_link = forms.URLField(label='Link orçamento 3', required=False)

    transport_mode = forms.ChoiceField(label='Meio de transporte', choices=TRANSPORT_CHOICES, required=False)
    origin = forms.CharField(label='Origem', required=False, max_length=255)
    destination = forms.CharField(label='Destino', required=False, max_length=255)
    purpose = forms.CharField(label='Finalidade', required=False, max_length=255)
    people_count = forms.IntegerField(label='Quantidade de pessoas', required=False, min_value=1)
    period = forms.CharField(label='Período previsto', required=False, max_length=255)

    daily_type = forms.ChoiceField(label='Tipo de diária', choices=DAILY_CHOICES, required=False)
    location = forms.CharField(label='Localidade', required=False, max_length=255)
    days_count = forms.IntegerField(label='Número de dias', required=False, min_value=1)
    unit_value = forms.DecimalField(label='Valor unitário', required=False, decimal_places=2, max_digits=12, min_value=0)

    scholarship_modality = forms.ChoiceField(label='Modalidade de bolsa', choices=SCHOLARSHIP_CHOICES, required=False)
    duration_months = forms.IntegerField(label='Duração prevista em meses', required=False, min_value=1)
    monthly_value = forms.DecimalField(label='Valor mensal ou do curso', required=False, decimal_places=2, max_digits=12, min_value=0)
    education_level = forms.ChoiceField(label='Formação exigida', choices=EDUCATION_CHOICES, required=False)
    weekly_dedication = forms.ChoiceField(label='Dedicação semanal', choices=WEEKLY_DEDICATION_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('section_code')

        if code == 'a':
            self._require_fields(cleaned_data, ['title', 'selected_quote'])
            self._require_quote_fields(cleaned_data, require_quantity=True, require_freight=True)
        elif code == 'b':
            self._require_fields(cleaned_data, ['title', 'quantity', 'selected_quote'])
            self._require_quote_fields(cleaned_data)
        elif code == 'c':
            self._require_fields(cleaned_data, ['title', 'justification', 'quantity', 'unit', 'selected_quote'])
            self._require_quote_fields(cleaned_data)
        elif code == 'd.1':
            self._require_fields(cleaned_data, ['transport_mode', 'origin', 'destination', 'purpose', 'people_count', 'selected_quote'])
            self._require_quote_fields(cleaned_data)
        elif code == 'd.2':
            self._require_fields(cleaned_data, ['daily_type', 'location', 'people_count', 'days_count', 'unit_value'])
        elif code == 'e':
            self._require_fields(cleaned_data, ['scholarship_modality', 'quantity', 'monthly_value', 'justification'])
            if cleaned_data.get('scholarship_modality') != 'Participação em Curso':
                self._require_fields(cleaned_data, ['duration_months'])
            if cleaned_data.get('scholarship_modality') == 'Ensino Público — Aperfeiçoamento Pedagógico':
                self._require_fields(cleaned_data, ['education_level', 'weekly_dedication'])

        return cleaned_data

    def _require_fields(self, cleaned_data, field_names):
        for field_name in field_names:
            value = cleaned_data.get(field_name)
            if value in [None, '', []]:
                self.add_error(field_name, 'Este campo é obrigatório para a categoria selecionada.')

    def _require_quote_fields(self, cleaned_data, require_quantity=False, require_freight=False):
        for quote_number in range(1, 4):
            amount = cleaned_data.get(f'quote_{quote_number}_amount')
            quantity = cleaned_data.get(f'quote_{quote_number}_quantity')
            freight = cleaned_data.get(f'quote_{quote_number}_freight')
            link = cleaned_data.get(f'quote_{quote_number}_link')
            if amount in [None, '']:
                self.add_error(f'quote_{quote_number}_amount', 'Informe o valor deste orçamento.')
            if require_quantity and quantity in [None, '']:
                self.add_error(f'quote_{quote_number}_quantity', 'Informe a quantidade deste orçamento.')
            if require_freight and freight in [None, '']:
                self.add_error(f'quote_{quote_number}_freight', 'Informe o frete deste orçamento.')
            if link in [None, '']:
                self.add_error(f'quote_{quote_number}_link', 'Informe o link deste orçamento.')


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
