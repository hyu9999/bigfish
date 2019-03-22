from rest_framework import serializers

from bigfish.apps.resources.models import Amazon, Video, Audio, Image, Animation, SpecialEffect, ImageType, Pet, \
    LocResInfo


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"


class VideoRuleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    @staticmethod
    def get_image(obj):
        try:
            data = obj.img.res.url
        except Exception as e:
            return ""
        else:
            return data

    class Meta:
        model = Video
        fields = ('id', 'title', 'res', 'image')


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = "__all__"


class AudioRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ('id', 'title', 'res',)


class ImageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageType
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class ImageRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'title', 'res',)


class RoleRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'title', 'res',)


class AnimationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animation
        fields = "__all__"


class SpecialEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialEffect
        fields = "__all__"


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = "__all__"


class AmazonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amazon
        fields = '__all__'


class LocResInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocResInfo
        fields = '__all__'
