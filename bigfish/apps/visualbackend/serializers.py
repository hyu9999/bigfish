from rest_framework import serializers

from bigfish.apps.visualbackend.models import StageScore, ExaminationCondition


class StageScoreSerializer(serializers.ModelSerializer):
    """
    全量
    """

    class Meta:
        model = StageScore
        fields = '__all__'


class StageScoreDataSerializer(serializers.ModelSerializer):
    """
    个人均值成绩
    """

    class Meta:
        model = StageScore
        fields = ('id', 'term', 'klass_id', 'username', 'score_type', 'score')


class ExaminationConditionSerializer(serializers.ModelSerializer):
    """
    全量 试卷情况
    """

    class Meta:
        model = ExaminationCondition
        fields = '__all__'


class ExaminationConditionDataSerializer(serializers.ModelSerializer):
    """
    试卷情况
    """
    score_type_name = serializers.SerializerMethodField()

    @staticmethod
    def get_score_type_name(obj):
        return "{}、{}".format(obj.order, obj.question)

    class Meta:
        model = ExaminationCondition
        fields = ('id', 'score_type_name', 'difficult')
