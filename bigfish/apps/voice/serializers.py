from rest_framework import serializers

from bigfish.apps.voice.models import SpeechEvaluation, SpeechEvaluationReport


class SpeechEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechEvaluation
        fields = "__all__"


class SpeechEvaluationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechEvaluationReport
        fields = "__all__"
