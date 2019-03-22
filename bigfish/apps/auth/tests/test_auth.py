from django.contrib.auth import get_user_model
from django.urls import reverse
from bigfish.base import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from bigfish.tests import set_credentials

Users = get_user_model()


class TestAuth(APITestCase):
    fixtures = ['test_auth']

    def test_register_user(self):
        response = self.client.post(
            reverse('rest_register'),
            {
                'username': 'test',
                'password1': 'password',
                'password2': 'password',
                'email': 'test@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = Users.objects.get(username='test')
        self.assertTrue(new_user.is_active)
        self.assertTrue(
            Token.objects.filter(key=response.json()['key']).exists()
        )

    def test_register_names_options(self):
        """Ensure that first_name and last_name are optional."""
        response = self.client.post(
            reverse('rest_register'),
            {
                'username': 'test',
                'password1': 'password',
                'password2': 'password',
                'email': 'test@example.com',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('key', response.json())

    def test_login_with_username(self):
        response = self.client.post(
            reverse('rest_login'),
            {
                'username': 'normal_user',
                'password': 'test',
            }
        )

        self.assert_login_success(response, 'normal_user')

    def test_login_with_email(self):
        response = self.client.post(
            reverse('rest_login'),
            {
                'email': 'normal_user@example.com',
                'password': 'test',
            }
        )

        self.assert_login_success(response, 'normal_user')

    def assert_login_success(self, response, username):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        key = Token.objects.get(user__username=username).key
        self.assertEqual(response.json()['key'], key)

    def test_authorization_with_auth_token(self):
        set_credentials(self.client, user='normal_user')

        response = self.client.get(reverse('rest_user_details'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'normal_user')

    def test_logout(self):
        token = set_credentials(self.client, user='normal_user')

        response = self.client.post(reverse('rest_logout'), {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(pk=token.pk)
