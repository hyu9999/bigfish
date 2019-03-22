from rest_framework import serializers

from bigfish.apps.knowledgepoint.models import KnowledgePoint


class KnowledgePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgePoint
        fields = '__all__'
