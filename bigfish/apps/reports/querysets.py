from django.db import models


class StudyQuerySet(models.QuerySet):
    def owned_by(self, owner):
        return self.filter(owner=owner)
