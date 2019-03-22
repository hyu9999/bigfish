from rest_framework import serializers

from bigfish.apps.public.models import Public, AppTable, ATGroup
from bigfish.utils.functions import format_admin_list


class PublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Public
        fields = format_admin_list(Public)


class ATGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATGroup
        fields = format_admin_list(ATGroup)


class AppTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppTable
        fields = format_admin_list(AppTable)
