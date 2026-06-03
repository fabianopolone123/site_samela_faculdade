from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import BudgetCostEntry, BudgetSection, SignupCode, User


class SignupFlowTests(TestCase):
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


class BudgetFlowTests(TestCase):
    def setUp(self):
        self.client.post(reverse('login'), {'username': 'fabiano', 'password': '123'})

    def test_sections_seeded(self):
        self.assertTrue(BudgetSection.objects.filter(code='a').exists())
        self.assertTrue(BudgetSection.objects.filter(code='d.1').exists())
        self.assertTrue(BudgetSection.objects.filter(code='e').exists())

    def test_create_material_cost_entry(self):
        response = self.client.post(
            reverse('budget_product_create'),
            {
                'section_code': 'a',
                'title': 'Notebook',
                'details': 'Equipamento para coleta de dados',
                'quantity': '2',
                'selected_quote': '2',
                'quote_1_amount': '1000.00',
                'quote_1_link': 'https://example.com/1',
                'quote_2_amount': '1200.00',
                'quote_2_link': 'https://example.com/2',
                'quote_3_amount': '1300.00',
                'quote_3_link': 'https://example.com/3',
            },
        )

        self.assertRedirects(response, reverse('budget_product_create'))
        entry = BudgetCostEntry.objects.get(title='Notebook')
        self.assertEqual(entry.section.code, 'a')
        self.assertEqual(entry.total_considered, 2400)

        ready = self.client.get(reverse('budget_ready'))
        self.assertContains(ready, 'Notebook')
        self.assertContains(ready, 'R$ 2400')

    def test_create_daily_entry(self):
        response = self.client.post(
            reverse('budget_product_create'),
            {
                'section_code': 'd.2',
                'title': 'Diária para campo',
                'daily_type': 'Diária no país',
                'location': 'Campinas',
                'people_count': '2',
                'days_count': '3',
                'unit_value': '150.00',
            },
        )

        self.assertRedirects(response, reverse('budget_product_create'))
        entry = BudgetCostEntry.objects.get(title='Diária para campo')
        self.assertEqual(entry.total_considered, 900)
