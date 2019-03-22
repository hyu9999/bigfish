from rest_framework import serializers

from .models import PrepareLesson, PrepareLessonReply, PrepareLessonWatch, TeachingLog, TeachingLogReply, \
    TeachingLogWatch, ResearchActivity, ResearchActivityReply, ResearchActivityWatch, TeacherSchedule
from bigfish.apps.schools.models import SchoolWeek, Term, TermWeek


class PrepareLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepareLesson
        fields = '__all__'


class PrepareLessonReplySerializer(serializers.ModelSerializer):
    nick_name = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    class Meta:
        model = PrepareLessonReply
        fields = '__all__'

    def get_nick_name(self, obj):
        nick_name = obj.user.profile.realname
        return nick_name

    def get_identity(self, obj):
        identity = obj.user.profile.identity
        return identity


class PrepareLessonWatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepareLessonWatch
        fields = '__all__'


class TeachingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachingLog
        fields = '__all__'


class TeachingLogReplySerializer(serializers.ModelSerializer):
    nick_name = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    class Meta:
        model = TeachingLogReply
        fields = '__all__'

    def get_nick_name(self, obj):
        nick_name = obj.user.profile.realname
        return nick_name

    def get_identity(self, obj):
        identity = obj.user.profile.identity
        return identity


class TeachingLogWatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachingLogWatch
        fields = '__all__'


class ResearchActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchActivity
        fields = '__all__'


class ResearchActivityReplySerializer(serializers.ModelSerializer):
    nick_name = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()

    class Meta:
        model = ResearchActivityReply
        fields = '__all__'

    def get_nick_name(self, obj):
        nick_name = obj.user.profile.realname
        return nick_name

    def get_identity(self, obj):
        identity = obj.user.profile.identity
        return identity


class ResearchActivityWatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchActivityWatch
        fields = '__all__'


class TeacherScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSchedule
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'


class TermWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermWeek
        fields = '__all__'


# class TermScheduleFmtSerializer(serializers.ModelSerializer):
#     """
#
#     """
#     academic_year = serializers.SerializerMethodField()
#
#     @staticmethod
#     def get_academic_year(obj):
#         academic_year = obj.term.academic_year
#         return academic_year
#
#     class Meta:
#         model = TermSchedule
#         fields = ('id', 'term_id', 'academic_year', 'schools', 'start_date', 'finish_date')
#
#
# class TermScheduleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TermSchedule
#         fields = '__all__'


class SchoolWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolWeek
        fields = '__all__'
