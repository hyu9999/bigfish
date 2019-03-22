from rest_framework import serializers

from bigfish.apps.attention.models import AttentionCircle


class AttentionCircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttentionCircle
        fields = '__all__'


class ACFocusSerializer(serializers.ModelSerializer):
    """
    关注数
    """
    realname = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    @staticmethod
    def get_realname(obj):
        try:
            data = obj.user.realname
        except Exception as e:
            data = ""
        return data

    @staticmethod
    def get_icon(obj):
        try:
            data = obj.user.icon.image.res
        except Exception as e:
            data = ""
        return data

    class Meta:
        model = AttentionCircle
        fields = ('id', 'realname', 'icon', 'each_other')


class ACFansSerializer(serializers.ModelSerializer):
    """
    粉丝数
    """
    realname = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    @staticmethod
    def get_realname(obj):
        try:
            data = obj.fans.realname
        except Exception as e:
            data = ""
        return data

    @staticmethod
    def get_icon(obj):
        try:
            data = obj.fans.icon.image.res
        except Exception as e:
            data = ""
        return data

    class Meta:
        model = AttentionCircle
        fields = ('id', 'realname', 'icon', 'each_other')
