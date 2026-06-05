from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import AllowedSignupEmail, AuditLog, CostField, CostRecord, CostRecordValue, CostTopic, SignupCode, User


class SignupFlowTests(TestCase):
    def test_login_page_displays_ptbr_texts_correctly(self):
        response = self.client.get(reverse('login'))

        self.assertContains(response, 'Instituição')
        self.assertContains(response, 'Código')
        self.assertNotContains(response, 'InstituiÃ§Ã£o', html=False)
        self.assertNotContains(response, 'CÃ³digo', html=False)

    def test_disallowed_email_cannot_start_signup(self):
        response = self.client.post(
            reverse('signup_email'),
            {'email': 'nao-autorizado@example.com'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'não está autorizado', html=False)
        self.assertEqual(SignupCode.objects.count(), 0)

    def test_full_signup_flow_creates_user_and_sends_emails(self):
        email = next(iter(settings.ALLOWED_SIGNUP_EMAILS))

        response = self.client.post(reverse('signup_email'), {'email': email})
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(len(mail.outbox), 1)

        code = SignupCode.objects.get(email=email)
        response = self.client.post(reverse('signup_code'), {'code': code.code})
        self.assertRedirects(response, reverse('login'))

        response = self.client.post(
            reverse('signup_password'),
            {'password1': 'SenhaSegura123', 'password2': 'SenhaSegura123'},
        )
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(email=email).exists())
        self.assertEqual(len(mail.outbox), 2)


class SeededAccessTests(TestCase):
    def test_seeded_test_user_can_login_with_login_name(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'fabiano', 'password': '123'},
        )

        self.assertRedirects(response, reverse('dashboard'))


class DynamicTopicBudgetTests(TestCase):
    def setUp(self):
        self.client.post(reverse('login'), {'username': 'fabiano', 'password': '123'})

    def test_default_topics_and_fields_are_seeded(self):
        self.assertTrue(
            CostTopic.objects.filter(
                name='Material permanente adquirido no país e importado'
            ).exists()
        )
        self.assertTrue(
            CostTopic.objects.filter(
                name='Material de consumo adquirido no país e importado'
            ).exists()
        )
        topic = CostTopic.objects.get(name='Material permanente adquirido no país e importado')
        self.assertTrue(topic.fields.filter(name='Nome do produto', parent__isnull=True).exists())
        budget_1 = topic.fields.get(name='Orçamento 1', parent__isnull=True)
        self.assertTrue(topic.fields.filter(parent=budget_1, name='Preço').exists())
        self.assertTrue(topic.fields.filter(parent=budget_1, name='Frete').exists())

    def test_can_create_topic(self):
        response = self.client.post(
            reverse('create_topic'),
            {'name': 'Material permanente'},
        )

        topic = CostTopic.objects.get(name='Material permanente')
        self.assertRedirects(
            response,
            f"{reverse('budget_product_create')}?topic={topic.id}",
        )

    def test_can_create_field_and_subfield(self):
        topic = CostTopic.objects.create(name='Transporte')

        response = self.client.post(
            reverse('create_topic_field'),
            {
                'topic_id': topic.id,
                'name': 'Destino',
                'field_type': 'texto',
                'parent_id': '',
            },
        )
        self.assertRedirects(
            response,
            f"{reverse('budget_product_create')}?topic={topic.id}&open=campos",
        )

        parent = CostField.objects.get(topic=topic, name='Destino')
        response = self.client.post(
            reverse('create_topic_field'),
            {
                'topic_id': topic.id,
                'name': 'Link da passagem',
                'field_type': 'link',
                'parent_id': parent.id,
            },
        )
        self.assertRedirects(
            response,
            f"{reverse('budget_product_create')}?topic={topic.id}&open=campos",
        )

        child = CostField.objects.get(topic=topic, name='Link da passagem')
        self.assertEqual(child.parent, parent)

    def test_can_create_dynamic_cost_record(self):
        topic = CostTopic.objects.create(name='Material permanente')
        product = CostField.objects.create(topic=topic, name='Nome do produto', field_type='texto')
        quote = CostField.objects.create(topic=topic, name='Orçamento 1', field_type='valor')
        link = CostField.objects.create(
            topic=topic,
            parent=quote,
            name='Link do orçamento',
            field_type='link',
        )

        response = self.client.post(
            reverse('create_topic_record'),
            {
                'topic_id': topic.id,
                f'field_{product.id}': 'Notebook Dell',
                f'field_{quote.id}': '4.500,90',
                f'field_{link.id}': 'https://example.com/notebook',
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('budget_product_create')}?topic={topic.id}",
        )
        record = CostRecord.objects.get(topic=topic)
        self.assertEqual(record.values.count(), 3)
        self.assertTrue(
            CostRecordValue.objects.filter(
                record=record,
                field=product,
                value='Notebook Dell',
            ).exists()
        )
        self.assertTrue(
            CostRecordValue.objects.filter(
                record=record,
                field=quote,
                value='4.500,90',
            ).exists()
        )

    def test_budget_page_shows_dynamic_builder(self):
        topic = CostTopic.objects.create(name='Bolsas')
        CostField.objects.create(topic=topic, name='Modalidade', field_type='texto')

        response = self.client.get(
            reverse('budget_product_create'),
            {'topic': topic.id},
        )

        self.assertContains(response, 'Monte os tópicos e registre os custos do orçamento')
        self.assertContains(response, 'Bolsas')
        self.assertContains(response, 'Modalidade')
        self.assertNotContains(response, 'tÃ³picos', html=False)
        self.assertNotContains(response, 'orÃ§amento', html=False)

    def test_budget_ready_reflects_dynamic_topics_and_records(self):
        topic = CostTopic.objects.create(
            name='Serviços de Terceiros contratados no país e no exterior',
            description='Resumo dinâmico do tópico.',
        )
        service_name = CostField.objects.create(
            topic=topic,
            name='Nome do serviço',
            field_type='texto',
        )
        selector = CostField.objects.create(
            topic=topic,
            name='Selecionar para orçar',
            field_type='numero',
        )
        quote_1 = CostField.objects.create(
            topic=topic,
            name='Orçamento 1',
            field_type='texto',
        )
        quote_price = CostField.objects.create(
            topic=topic,
            parent=quote_1,
            name='Preço',
            field_type='valor',
        )
        quote_freight = CostField.objects.create(
            topic=topic,
            parent=quote_1,
            name='Frete',
            field_type='valor',
        )
        quote_link = CostField.objects.create(
            topic=topic,
            parent=quote_1,
            name='Link',
            field_type='link',
        )

        record = CostRecord.objects.create(topic=topic)
        CostRecordValue.objects.create(record=record, field=service_name, value='Transcrição de entrevistas')
        CostRecordValue.objects.create(record=record, field=selector, value='1')
        CostRecordValue.objects.create(record=record, field=quote_price, value='120.00')
        CostRecordValue.objects.create(record=record, field=quote_freight, value='30.00')
        CostRecordValue.objects.create(record=record, field=quote_link, value='https://example.com/orcamento')

        response = self.client.get(reverse('budget_ready'))

        self.assertContains(response, 'Serviços de Terceiros contratados no país e no exterior')
        self.assertContains(response, 'Transcrição de entrevistas')
        self.assertContains(response, 'Resumo dinâmico do tópico.')
        self.assertContains(response, 'R$ 150,00', html=False)
        self.assertContains(response, 'Abrir link')
        self.assertContains(response, 'https://example.com/orcamento')
        self.assertContains(response, '120,00')

    def test_budget_totals_use_ptbr_thousands_separator(self):
        topic = CostTopic.objects.create(name='Material permanente')
        selector = CostField.objects.create(topic=topic, name='Selecionar para orçar', field_type='numero')
        quote_1 = CostField.objects.create(topic=topic, name='Orçamento 1', field_type='texto')
        quote_price = CostField.objects.create(topic=topic, parent=quote_1, name='Preço', field_type='valor')

        record = CostRecord.objects.create(topic=topic)
        CostRecordValue.objects.create(record=record, field=selector, value='1')
        CostRecordValue.objects.create(record=record, field=quote_price, value='70306270,00')

        response = self.client.get(reverse('budget_product_create'), {'topic': topic.id})

        self.assertContains(response, 'R$&nbsp;70.306.270,00', html=True)

    def test_can_delete_dynamic_cost_record(self):
        topic = CostTopic.objects.create(name='Material permanente')
        field = CostField.objects.create(topic=topic, name='Nome do produto', field_type='texto')
        record = CostRecord.objects.create(topic=topic)
        CostRecordValue.objects.create(record=record, field=field, value='Projetor')

        response = self.client.post(
            reverse('delete_topic_record', args=[record.id]),
            {'next': f"{reverse('budget_product_create')}?topic={topic.id}"},
        )

        self.assertRedirects(
            response,
            f"{reverse('budget_product_create')}?topic={topic.id}",
        )
        self.assertFalse(CostRecord.objects.filter(id=record.id).exists())

    def test_can_delete_topic_with_records(self):
        topic = CostTopic.objects.create(name='Transporte')
        field = CostField.objects.create(topic=topic, name='Destino', field_type='texto')
        record = CostRecord.objects.create(topic=topic)
        CostRecordValue.objects.create(record=record, field=field, value='São Paulo')

        response = self.client.post(reverse('delete_topic', args=[topic.id]))

        self.assertRedirects(response, reverse('budget_product_create'))
        self.assertFalse(CostTopic.objects.filter(id=topic.id).exists())
        self.assertFalse(CostRecord.objects.filter(id=record.id).exists())


class AuditLogTests(TestCase):
    def test_admin_dashboard_shows_audit_button(self):
        self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})

        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'Auditoria')

    def test_non_admin_cannot_access_audit_page(self):
        self.client.post(reverse('login'), {'username': 'fabiano', 'password': '123'})

        response = self.client.get(reverse('audit_log'))

        self.assertRedirects(response, reverse('dashboard'))

    def test_creating_topic_generates_audit_log(self):
        self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})

        response = self.client.post(reverse('create_topic'), {'name': 'Tópico auditado'})

        topic = CostTopic.objects.get(name='Tópico auditado')
        self.assertRedirects(
            response,
            f"{reverse('budget_product_create')}?topic={topic.id}",
        )
        audit_log = AuditLog.objects.get(
            action=AuditLog.ACTION_CREATE,
            target_type='Tópico',
            target_name='Tópico auditado',
        )
        self.assertEqual(audit_log.user.login_name, 'adm')

    def test_audit_page_lists_registered_actions(self):
        admin_user = User.objects.get(login_name='adm')
        AuditLog.objects.create(
            user=admin_user,
            action=AuditLog.ACTION_DELETE,
            target_type='Custo',
            target_name='Notebook',
            description='Exclusão de custo no tópico Material permanente.',
        )
        self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})

        response = self.client.get(reverse('audit_log'))

        self.assertContains(response, 'Notebook')
        self.assertContains(response, 'Exclusão')
        self.assertContains(response, 'adm')


class AllowedSignupEmailTests(TestCase):
    def test_admin_can_view_allowed_signup_emails_page(self):
        self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})

        response = self.client.get(reverse('allowed_signup_emails'))

        self.assertContains(response, 'E-mails autorizados para cadastro')

    def test_admin_can_add_dynamic_signup_email(self):
        self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})

        response = self.client.post(
            reverse('create_allowed_signup_email'),
            {'email': 'novo.email@example.com'},
        )

        self.assertRedirects(response, reverse('allowed_signup_emails'))
        self.assertTrue(AllowedSignupEmail.objects.filter(email='novo.email@example.com').exists())
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.ACTION_CREATE,
                target_type='E-mail autorizado',
                target_name='novo.email@example.com',
            ).exists()
        )

    def test_admin_can_remove_dynamic_signup_email(self):
        self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})
        allowed_email = AllowedSignupEmail.objects.create(email='remover@example.com')

        response = self.client.post(reverse('delete_allowed_signup_email', args=[allowed_email.id]))

        self.assertRedirects(response, reverse('allowed_signup_emails'))
        self.assertFalse(AllowedSignupEmail.objects.filter(email='remover@example.com').exists())

    def test_dynamic_signup_email_is_accepted_in_signup_flow(self):
        AllowedSignupEmail.objects.create(email='liberado@example.com')

        response = self.client.post(reverse('signup_email'), {'email': 'liberado@example.com'})

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(SignupCode.objects.filter(email='liberado@example.com').count(), 1)
