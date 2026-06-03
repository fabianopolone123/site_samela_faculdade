from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import SignupCode, User


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

    def test_login_with_created_user_redirects_to_dashboard(self):
        user = User.objects.create_user(
            email='samelapolloni@estudante.ufscar.br',
            password='SenhaSegura123',
        )

        response = self.client.post(
            reverse('login'),
            {'username': user.email, 'password': 'SenhaSegura123'},
        )

        self.assertRedirects(response, reverse('dashboard'))

# Create your tests here.
