from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

Users = get_user_model()


def set_credentials(api_client, user, autocreate=True):
    """
    Set authentication token for given APIClient instance and user.
    """
    if isinstance(user, str):
        user = Users.objects.get(username=user)

    if autocreate:
        token, _ = Token.objects.get_or_create(user=user)
    else:
        token = Token.objects.get(user=user)

    api_client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))
    return token


def unset_credentials(api_client):
    api_client.credentials()
