from rest_framework import serializers
from bigfish.apps.homework.models import Homework, PushRecord


class HomeWorkSerializers(serializers.ModelSerializer):

    class Meta:
        model = Homework
        fields = '__all__'


class PushRecordSerializers(serializers.ModelSerializer):
    class Meta:
        model = PushRecord
        fields = '__all__'