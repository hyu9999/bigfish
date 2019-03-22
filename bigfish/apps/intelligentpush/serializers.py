from rest_framework import serializers

from bigfish.apps.intelligentpush.models import IntelligentPush
from bigfish.apps.wrongtopic.models import WrongTopic


class WrongTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrongTopic
        fields = '__all__'


class IntelligentPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntelligentPush
        fields = '__all__'
