from rest_framework import serializers

from bigfish.apps.reports.models import ExaminationReport, RatingReport, \
    PracticalCourseRecord
from bigfish.utils.functions import generate_fields


class ExaminationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExaminationReport
        fields = '__all__'


class RatingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingReport
        fields = '__all__'


class PracticalCourseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticalCourseRecord
        fields = '__all__'
