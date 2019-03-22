from rest_framework import serializers

from bigfish.utils.functions import format_admin_list
from .models import Question, QuestionKPRelationship


class QuestionKPRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionKPRelationship
        fields = format_admin_list(QuestionKPRelationship)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = format_admin_list(Question, remove=['is_push'])


class QuestionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = format_admin_list(Question, remove=['is_push'])
