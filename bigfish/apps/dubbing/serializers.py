from rest_framework import serializers

from bigfish.apps.dubbing.models import DubbingSRC, UserDubbing, DubbingZan, DubbingRead, \
    DubbingCategory, DubbingMain, DubbingClick, Competition, SubCompetition, CompetitionRank, RewardConfig, \
    CompetitionImg
from bigfish.utils.functions import generate_fields


class DubbingMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubbingMain
        fields = '__all__'


class DubbingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DubbingCategory
        fields = '__all__'


class DubbingSRCSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubbingSRC
        fields = '__all__'


class UserDubbingSerializer(serializers.ModelSerializer):
    zan_num = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    nick_name = serializers.SerializerMethodField()
    user_icon = serializers.SerializerMethodField()
    src_image = serializers.SerializerMethodField()
    stop_image = serializers.SerializerMethodField()

    def get_zan_num(self, obj):
        num_list = DubbingZan.objects.filter(userdubbing=obj.id)
        return num_list.count()

    def get_user_name(self, obj):
        return obj.user.profile.realname

    def get_nick_name(self, obj):
        return obj.user.profile.nickname

    def get_user_icon(self, obj):
        return obj.user.profile.icon

    def get_src_image(self, obj):
        if obj.dubbingsrc.image:
            return obj.dubbingsrc.image.url
        else:
            return ""

    def get_stop_image(self, obj):
        if obj.dubbingsrc.stop_image:
            return obj.dubbingsrc.stop_image.url
        else:
            return ""

    class Meta:
        model = UserDubbing
        fields = generate_fields(UserDubbing, add=["zan_num", "id", "user_name", "user_icon", "src_image", "stop_image",
                                                   "nick_name"])


class UDMinSerializer(serializers.ModelSerializer):
    user_icon = serializers.SerializerMethodField()
    dubbingsrc_id = serializers.SerializerMethodField()
    src_image = serializers.SerializerMethodField()

    @staticmethod
    def get_dubbingsrc_id(obj):
        try:
            dubbingsrc_id = obj.dubbingsrc.id
        except Exception as e:
            dubbingsrc_id = None
        return dubbingsrc_id

    @staticmethod
    def get_user_icon(obj):
        try:
            icon = obj.user.icon.url
        except Exception as e:
            icon = ""
        return icon

    @staticmethod
    def get_src_image(obj):
        try:
            src_image = obj.dubbingsrc.image.url
        except Exception as e:
            src_image = ""
        return src_image

    class Meta:
        model = UserDubbing
        fields = ('id', 'dubbingsrc_id', 'video', 'video_url', 'user', 'user_icon', 'zan_num', 'is_competition',
                  'src_image', 'create_time', 'description')


class DubbingClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubbingClick
        fields = '__all__'


class DubbingZanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubbingZan
        fields = generate_fields(DubbingZan)


class DubbingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubbingRead
        fields = generate_fields(DubbingRead)


class CompetitionImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionImg
        fields = '__all__'


class CompetitionSerializer(serializers.ModelSerializer):
    banner_data = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = generate_fields(Competition, add=['id', 'banner_data'])

    def get_banner_data(self, obj):
        quertset = obj.banner.all()
        data = CompetitionImgSerializer(quertset, many=True).data
        return data


class SubCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCompetition
        fields = '__all__'


class CompetitionRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionRank
        fields = '__all__'


class RewardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardConfig
        fields = '__all__'
