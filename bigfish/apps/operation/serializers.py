from rest_framework import serializers

from bigfish.apps.operation.models import OperateType, Operation, OperationRecord, ActClick


class OperateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperateType
        fields = '__all__'


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'


class OperationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationRecord
        fields = '__all__'


class ActClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActClick
        fields = "__all__"
