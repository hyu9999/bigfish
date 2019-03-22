from rest_framework import serializers
from bigfish.apps.versionupdate.models import Version


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'
