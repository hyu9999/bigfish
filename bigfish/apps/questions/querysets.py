from django.db import models


class WordQuerySet(models.QuerySet):
    def randoms(self):
        return self.order_by('?').all()
