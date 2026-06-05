from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import CostField, CostRecord, CostRecordValue, CostTopic, SignupCode, User


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
                f'field_{quote.id}': '4500.90',
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
