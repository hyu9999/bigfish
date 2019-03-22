from django_filters.rest_framework import filters, filterset

from bigfish.apps.textbooks.models import Lesson, Unit


class UnitFilter(filterset.FilterSet):
    active = filters.BooleanFilter(name='is_active')

    class Meta:
        model = Unit
        fields = ('active', 'textbook')


class LessonFilter(filterset.FilterSet):
    active = filters.BooleanFilter(name='is_active')

    class Meta:
        model = Lesson
        fields = ('active', 'unit__id')
