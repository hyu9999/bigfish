from django.db.models import F
from rest_framework import serializers

from bigfish.apps.contents.models import Article, Sentence, WordType, TextbookWord
from bigfish.apps.resources.serializers import RoleRuleSerializer, AudioSerializer, AudioRuleSerializer, \
    VideoRuleSerializer, ImageRuleSerializer
from bigfish.utils.functions import generate_fields


class ArticleSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    @staticmethod
    def get_video_url(obj):
        try:
            video_url = obj.video.res.url
        except Exception as e:
            video_url = ""
        return video_url

    class Meta:
        model = Article
        fields = generate_fields(Article, add=['video_url'])


class SentenceRuleSerializer(serializers.ModelSerializer):
    """

            "title": "Hello, Li Yan!",
            "en_title": "你好，Li Yan!",
            "content": "",
            "start_timestamp": 12850,
            "end_timestamp": 14850,
            "duration": 2000,
            "role_icon": "/media/res/ProRes/image/ui/4-changgehuodong.png",
            "role_name": "boy_1",
            "order": 1,
            "audio_url": "/media/res/ProRes/audio/sysAudio/talk1_01.mp3"

    """
    role = RoleRuleSerializer()
    audio = AudioRuleSerializer()

    class Meta:
        model = Sentence
        fields = ('id', 'title', 'en_title', 'content', 'start_timestamp', 'end_timestamp', 'duration', 'order',
                  'role', 'audio')


class ArticleRuleSerializer(serializers.ModelSerializer):
    sentence = SentenceRuleSerializer(many=True, read_only=True)
    video = VideoRuleSerializer()
    audio = AudioRuleSerializer()
    role_list = serializers.SerializerMethodField()

    @staticmethod
    def get_role_list(obj):
        role_list = Sentence.objects.filter(article=obj).order_by('role_id').distinct().annotate(
            role_name=F('role__title'), role_img=F('role__res')).values('role_id', 'role_name', 'role_img')

        return role_list

    class Meta:
        model = Article
        fields = ('id', 'title', 'en_title', 'audio', 'video', 'sentence', 'role_list')


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = generate_fields(Sentence)


class WordTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordType
        fields = generate_fields(WordType)


class TextbookWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextbookWord
        fields = generate_fields(TextbookWord)


class TextbookWordRuleSerializer(serializers.ModelSerializer):
    microtext = ArticleRuleSerializer()
    audio = AudioRuleSerializer()
    image = ImageRuleSerializer(many=True, read_only=True)

    class Meta:
        model = TextbookWord
        fields = ('id', 'title', 'en_title', 'audio', 'image', 'sentence', 'sentence_highlight', 'sentence_explain',
                  'microtext')


class ActSentenceSerializer(serializers.ModelSerializer):
    """
    活动中返回文章信息
    """
    role_icon = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()

    def get_role_icon(self, obj):
        return obj.role.res.url

    def get_role_name(self, obj):
        return obj.role.title

    def get_audio_url(self, obj):
        return obj.audio.res.url

    class Meta:
        model = Sentence
        fields = ('title', 'en_title', 'content', 'start_timestamp', 'end_timestamp', 'duration', 'role_icon',
                  'role_name', 'order', 'audio_url')
