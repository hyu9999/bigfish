from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from bigfish.apps.users.models import ApplicationSettings
from bigfish.tests import set_credentials

User = get_user_model()


class TestApplicationSettings(APITestCase):
    fixtures = ['test_users']
    create_data = {
        'mother_language': 'en',
        'instruction_language': 'zh',
    }

    def setUp(self):
        self.user = User.objects.get(username='user')
        self.other = User.objects.get(username='other')
        set_credentials(self.client, self.user)

    def test_list_not_available(self):
        resposne = self.client.get(reverse('applicationsettings-list'))
        self.assertEqual(resposne.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create(self):
        set_credentials(self.client, self.other)

        response = self.client.post(
            reverse('applicationsettings-list'),
            self.create_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_already_exists(self):
        """
        Ensure that user can't create application settings for the second time.
        """
        response = self.client.post(
            reverse('applicationsettings-list'),
            self.create_data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['owner'],
            'Application settings for this user already exists.'
        )

    def test_destroy(self):
        response = self.client.delete(
            reverse('applicationsettings-detail', args=(self.user.pk,))
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ApplicationSettings.DoesNotExist):
            ApplicationSettings.objects.get(pk=self.user.pk)

    def test_retrieve(self):
        """Ensure that user can access his settings using user's PK."""
        response = self.client.get(
            reverse('applicationsettings-detail', args=(self.user.pk,))
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        data = self.create_data.copy()
        data['gender'] = ApplicationSettings.FEMALE

        response = self.client.put(
            reverse('applicationsettings-detail', args=(self.user.pk,)),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.application_settings.gender, ApplicationSettings.FEMALE)

    def test_retrieve_by_other_user(self):
        """Ensure that user can't access other user's settings."""
        set_credentials(self.client, self.other)

        response = self.client.get(
            reverse('applicationsettings-detail', args=(self.user.pk,))
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
