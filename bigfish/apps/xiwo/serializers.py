from rest_framework import serializers

from bigfish.apps.xiwo.models import SerialBindingRelation


class SerialBindingRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerialBindingRelation
        fields = '__all__'
