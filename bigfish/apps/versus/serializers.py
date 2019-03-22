from rest_framework import serializers

from bigfish.apps.versus.models import VersusDetail, Versus


class VersusDetailSerializer(serializers.ModelSerializer):
    word_spell = serializers.SerializerMethodField()

    def get_word_spell(self, obj):
        return obj.word.spell

    user_id = serializers.SerializerMethodField()

    def get_user_id(self, obj):
        return obj.versus.pk_user.id

    class Meta:
        model = VersusDetail
        fields = ('id', 'versus', 'order', 'user_id', 'user_type', 'word', 'word_spell', 'question_type', 'result')


class VersusSerializer(serializers.ModelSerializer):
    versus_details = serializers.SerializerMethodField()

    def get_versus_details(self, obj):
        ret_data = {}
        for k, v in VersusDetail.QUESTION_TYPE_CHOICE:
            queryset = obj.versus_details.filter(question_type=k)
            order_list = queryset.values_list('order', flat=True).distinct()
            if obj.competitor_type == 0:
                tmp_dict = []
                for order_val in order_list:
                    order_arr = queryset.filter(order=order_val).order_by('user_type')
                    order_arr = VersusDetailSerializer(order_arr, many=True).data
                    tmp_dict.append(order_arr)
                ret_data[k] = tmp_dict
            elif obj.competitor_type == 1:
                tmp_dict = []
                for order_val in order_list:
                    try:
                        organizer_word = queryset.get(order=order_val)
                    except Exception as e:
                        organizer_word = None
                    try:
                        competitor_word = obj.competitor.versus_details.get(question_type=k, order=order_val)
                    except Exception as e:
                        competitor_word = None
                    order_arr = [VersusDetailSerializer(x).data for x in [organizer_word, competitor_word] if x]
                    tmp_dict.append(order_arr)
                ret_data[k] = tmp_dict
        return ret_data

    # competitor_type = serializers.SerializerMethodField()
    #
    # def get_competitor_type(self, obj):
    #     return obj.get_competitor_type_display()
    #
    # complete_type = serializers.SerializerMethodField()
    #
    # def get_complete_type(self, obj):
    #     return obj.get_complete_type_display()
    #
    # pk_type = serializers.SerializerMethodField()
    #
    # def get_pk_type(self, obj):
    #     return obj.get_pk_type_display()
    #
    # pk_result = serializers.SerializerMethodField()
    #
    # def get_pk_result(self, obj):
    #     return obj.get_pk_result_display()

    class Meta:
        model = Versus
        fields = ('id', 'competitor_type', 'complete_type', 'pk_type', 'classroom', 'start_time', 'end_time',
                  'pk_user', 'head_icon', 'pet_name', 'speed', 'score', 'real_score', 'big_fishery', 'pk_result',
                  'right_times', 'wrong_times', 'total_times', 'user_ai', 'ai_icon', 'ai_icon_frame', 'pet_name_ai',
                  'speed_ai', 'score_ai', 'real_score_ai', 'big_fishery_ai', 'pk_result_ai', 'right_times_ai',
                  'wrong_times_ai', 'total_times_ai', 'competitor', 'versus_details')
