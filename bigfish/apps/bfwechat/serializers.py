from rest_framework import serializers

from bigfish.apps.bfwechat.models import KeyWord, ActiveToken, SendMsg, MediaSource, \
    TemplateMsgRecord, TemplateMsg, WxUser, Feedback, WxArticleMsgRecord, WxArticleMsg, WxUserRelationship


class ActiveTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveToken
        fields = '__all__'


class MediaSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaSource
        fields = '__all__'


class KeyWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyWord
        fields = '__all__'


class SendMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendMsg
        fields = '__all__'


class TemplateMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMsg
        fields = '__all__'


class TemplateMsgRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMsgRecord
        fields = '__all__'


class WxArticleMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = WxArticleMsg
        fields = '__all__'


class WxArticleMsgRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WxArticleMsgRecord
        fields = '__all__'


class WxUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WxUser
        fields = '__all__'


class WxUserRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = WxUserRelationship
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
