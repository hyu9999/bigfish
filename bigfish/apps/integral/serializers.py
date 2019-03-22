from rest_framework import serializers

from bigfish.apps.integral.models import UserIntegral, IntegralReport


class UserIntegralSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserIntegral
        fields = "__all__"


class IntegralReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegralReport
        fields = "__all__"
