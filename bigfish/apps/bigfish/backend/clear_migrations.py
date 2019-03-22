import os

from bigfish.settings.base import BASE_DIR
from bigfish.utils.django.config_settings import config_django

config_django()


def clear_migration():
    for root, dirs, files in os.walk(BASE_DIR):
        folder_name = os.path.basename(root)
        if folder_name != 'migrations':
            continue
        cmd_str = "del {}".format(os.path.join(root, "000*.py"))
        print(cmd_str)
        os.system(cmd_str)


if __name__ == '__main__':
    clear_migration()
