from django.db import models


class TaskCastQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True).order_by("title")
