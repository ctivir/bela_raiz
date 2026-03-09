from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.register_page = reverse('register_page')
        self.login_page = reverse('login_page')

    def test_registration_and_login(self):
        data = {
            'username': 'janedoe',
            'email': 'jane@example.com',
            'password': 'Secur3P@ss!',
            'password2': 'Secur3P@ss!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone_number': '+25887654321',
            'role': 'client',
        }
        resp = self.client.post(self.register_url, data)
        self.assertEqual(resp.status_code, 201)
        self.assertIn('token', resp.data)

        # login with the same credentials
        login_resp = self.client.post(self.login_url, {'username': 'janedoe', 'password': 'Secur3P@ss!'})
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('token', login_resp.data)
        self.assertEqual(login_resp.data['email'], 'jane@example.com')

    def test_pages_load(self):
        resp = self.client.get(self.register_page)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(self.login_page)
        self.assertEqual(resp.status_code, 200)

    def test_registration_password_mismatch(self):
        data = {
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'abc12345',
            'password2': 'different',
            'first_name': 'Bob',
            'last_name': 'Builder',
            'phone_number': '+25811122233',
            'role': 'client',
        }
        resp = self.client.post(self.register_url, data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('password', resp.data)
