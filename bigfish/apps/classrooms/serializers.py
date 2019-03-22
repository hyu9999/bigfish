from bigfish.apps.classrooms.models import BlackSetting, Classroom, ActivityDetailReport, BlackSettingReport, Cast, \
    CastReport, ActivityReport, StuActivity
from bigfish.base import serializers


class BlackSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackSetting
        fields = "__all__"


class BlackSettingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackSettingReport
        fields = "__all__"


class CastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cast
        fields = "__all__"


class CastReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CastReport
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = "__all__"


class StuActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StuActivity
        fields = "__all__"


class ActivityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityReport
        fields = "__all__"


class ActivityDetailReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityDetailReport
        fields = "__all__"
