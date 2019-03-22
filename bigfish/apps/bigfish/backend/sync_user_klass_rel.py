import csv
import sys

from bigfish.utils.django.config_settings import config_django

config_django()
from django.db import transaction
from bigfish.apps.users.models import UserKlassRelationship


with open('users_userprofile_attend_class.csv') as f:
    f_csv = csv.DictReader(f)
    print(f_csv)
    for row in f_csv:
        print(row)
        kwargs = {"user_id": row.get("userprofile_id"), "klass_id": row.get("klass_id")}
        try:
            UserKlassRelationship.objects.get_or_create(defaults={"study_progress": 0}, **kwargs)
        except Exception as e:
            continue
with transaction.atomic():
    with open('default_klass.csv') as f:
        f_csv = csv.DictReader(f)
        print(f_csv)
        for row in f_csv:
            print(row)
            kwargs = {"user_id": row.get("userprofile_id"), "klass_id": row.get("klass_id")}
            try:
                ukr = UserKlassRelationship.objects.get(**kwargs)
            except Exception as e:
                sys.exit(-1)
            else:
                ukr.is_default = True
                ukr.save()
