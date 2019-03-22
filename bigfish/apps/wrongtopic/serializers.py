from rest_framework import serializers

from bigfish.apps.wrongtopic.models import WrongTopic, WrongTopicHis


class WrongTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrongTopic
        fields = '__all__'


class WrongTopicHisSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrongTopicHis
        fields = '__all__'
