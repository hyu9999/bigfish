from __future__ import unicode_literals

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account import app_settings
from allauth.account.utils import user_email, user_username, user_field
from allauth.utils import import_attribute


class BFAccountAdapter(DefaultAccountAdapter):

    def __init__(self, request=None):
        self.request = request

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """

        data = form.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        realname = data.get('realname')
        username = data.get('username')
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        if realname:
            user_field(user, 'realname', realname)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user


def get_adapter(request=None):
    return import_attribute(app_settings.ADAPTER)(request)
