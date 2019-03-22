from rest_framework import serializers

from bigfish.utils.functions import generate_fields
from .models import Achievement, UserAchievement


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.SerializerMethodField()
    function_type = serializers.SerializerMethodField()
    desc_type = serializers.SerializerMethodField()
    reward = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    all_need_num = serializers.SerializerMethodField()
    activity_desc = serializers.SerializerMethodField()

    def get_achievement_name(self, obj):
        return obj.achievement.name

    def get_function_type(self, obj):
        return obj.achievement.function_type

    def get_desc_type(self, obj):
        return obj.achievement.desc_type

    def get_reward(self, obj):
        return obj.achievement.reward

    def get_icon(self, obj):
        if obj.achievement.icon:
            try:
                obj_url = obj.achievement.icon.url
            except:
                obj_url = ""
            return obj_url
        else:
            return None

    def get_all_need_num(self, obj):
        return obj.achievement.all_need_num

    def get_activity_desc(self, obj):
        return obj.achievement.desc

    class Meta:
        model = UserAchievement
        fields = generate_fields(UserAchievement,
                                 add=['achievement_name', 'function_type', 'desc_type', 'reward', 'icon',
                                      'all_need_num', 'activity_desc'])
