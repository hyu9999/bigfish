import json
from rest_framework import serializers

from bigfish.apps.textbooks.models import Unit, Lesson, Textbook, PublishVersion, Activity, ActTab, \
    ActType, PrepareAdvise
from bigfish.utils.functions import generate_fields, format_admin_list


class PublishVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishVersion
        fields = '__all__'


class TextbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Textbook
        fields = '__all__'


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'textbook', 'title', 'subtitle', 'is_active', 'order')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LessonDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'description')


class LessonCascadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'en_title')


class UnitCascadeSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField()

    @staticmethod
    def get_lesson(obj):
        lesson = Lesson.objects.filter(unit=obj, is_active=True)
        data = LessonCascadeSerializer(lesson, many=True).data
        return data

    class Meta:
        model = Unit
        fields = ('id', 'en_title', 'lesson')


class TextbookCascadeSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()

    @staticmethod
    def get_unit(obj):
        unit = Unit.objects.filter(textbook=obj, is_active=True)
        data = UnitCascadeSerializer(unit, many=True).data
        return data

    class Meta:
        model = Textbook
        fields = ('id', 'short_name', 'unit')


class ActTabSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActTab
        fields = "__all__"


class ActTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActType
        fields = "__all__"


class PrepareAdviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepareAdvise
        fields = "__all__"


class PrepareAdviseMinSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    @staticmethod
    def get_video_url(obj):
        try:
            data = obj.video.res.url
        except Exception as e:
            return ""
        else:
            return data

    class Meta:
        model = PrepareAdvise
        fields = ("id", "purpose", "step", "statement", "task", "video_url")


class ActivitySerializer(serializers.ModelSerializer):
    """
    返回Activity中的全部字段
    """

    progress = serializers.IntegerField(default=0)

    # video_url = serializers.SerializerMethodField()
    #
    # def get_video_url(self, obj):
    #     VIDEO_MEDIA_PREFIX = 'class'
    #     lesson = obj.lesson.order
    #     unit = obj.lesson.unit.unit_num
    #     text_grade = obj.lesson.unit.textbook.grade
    #     text_term = obj.lesson.unit.textbook.get_term_num_display()
    #     text_term_lower = text_term.lower()
    #     video_url = VIDEO_MEDIA_PREFIX + '/' + str(text_grade) + str(text_term_lower) + str(unit) + '/warmup_c' + str(lesson) + '.mp4'
    #     return  video_url

    # class Meta:
    #     model = Activity
    #     fields = (
    #         'id', 'title', 'en_title', 'icon', 'is_active', 'order', 'pointer', 'desc', 'en_desc',
    #         'lesson', 'progress', 'suggested_time', 'substance', 'question_ids', 'integral', 'video_url')

    class Meta:
        model = Activity
        fields = generate_fields(Activity, add=['id', 'progress'])
