from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import BudgetProduct, BudgetSection, SignupCode, User


class SignupFlowTests(TestCase):
    def test_disallowed_email_cannot_start_signup(self):
        response = self.client.post(
            reverse('signup_email'),
            {'email': 'nao-autorizado@example.com'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nao esta autorizado', html=False)
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

    def test_login_with_created_user_redirects_to_dashboard(self):
        user = User.objects.create_user(
            email='samelapolloni@estudante.ufscar.br',
            login_name='samela',
            password='SenhaSegura123',
        )

        response = self.client.post(
            reverse('login'),
            {'username': user.email, 'password': 'SenhaSegura123'},
        )

        self.assertRedirects(response, reverse('dashboard'))


class SeededAccessTests(TestCase):
    def test_seeded_test_user_can_login_with_login_name(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'fabiano', 'password': '123'},
        )

        self.assertRedirects(response, reverse('dashboard'))

    def test_seeded_admin_user_exists(self):
        self.assertTrue(
            User.objects.filter(login_name='adm', is_superuser=True, is_staff=True).exists()
        )


class BudgetFlowTests(TestCase):
    def setUp(self):
        self.client.post(reverse('login'), {'username': 'fabiano', 'password': '123'})

    def test_create_budget_product_and_render_total(self):
        response = self.client.post(
            reverse('budget_product_create'),
            {
                'name': 'Tablet educacional',
                'selected_quote': '2',
                'quote_1_price': '100.00',
                'quote_1_quantity': '1',
                'quote_1_link': 'https://example.com/1',
                'quote_2_price': '200.00',
                'quote_2_quantity': '2',
                'quote_2_link': 'https://example.com/2',
                'quote_3_price': '300.00',
                'quote_3_quantity': '3',
                'quote_3_link': 'https://example.com/3',
            },
        )

        self.assertRedirects(response, reverse('budget_product_create'))
        product = BudgetProduct.objects.get(name='Tablet educacional')
        self.assertEqual(product.section.code, '5.1')
        self.assertEqual(product.quotes.filter(is_selected=True).count(), 1)

        response = self.client.get(reverse('budget_ready'))
        self.assertContains(response, 'Tablet educacional')
        self.assertContains(response, 'R$ 400')

    def test_budget_section_seeded(self):
        self.assertTrue(
            BudgetSection.objects.filter(code='5.1', title__icontains='Custeio').exists()
        )
