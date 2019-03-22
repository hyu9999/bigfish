import os

import django


def config_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bigfish.settings.base")
    django.setup()
