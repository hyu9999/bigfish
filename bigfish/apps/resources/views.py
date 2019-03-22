import os
import re

import boto3
from django.conf import settings
from rest_framework.decorators import list_route
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from bigfish.apps.resources.models import Amazon, media_path, Video, Audio, Image, Animation, SpecialEffect, \
    ImageType, Pet, LocResInfo
from bigfish.apps.resources.serializers import AmazonSerializer, VideoSerializer, AudioSerializer, ImageSerializer, \
    AnimationSerializer, SpecialEffectSerializer, ImageTypeSerializer, PetSerializer, LocResInfoSerializer
from bigfish.base import viewsets, status
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (JSONParser, MultiPartParser)


class AudioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    parser_classes = (JSONParser, MultiPartParser)


class ImageTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImageType.objects.all()
    serializer_class = ImageTypeSerializer
    parser_classes = (JSONParser, MultiPartParser)


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (JSONParser, MultiPartParser)
    filter_fields = ("id", "image_type", "title", "is_active")


class AnimationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Animation.objects.all()
    serializer_class = AnimationSerializer
    parser_classes = (JSONParser, MultiPartParser)


class SpecialEffectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SpecialEffect.objects.all()
    serializer_class = SpecialEffectSerializer
    parser_classes = (JSONParser, MultiPartParser)


class PetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    parser_classes = (JSONParser, MultiPartParser)


class AmazonViewSet(viewsets.ModelViewSet):
    """
    亚马逊：
    """
    queryset = Amazon.objects.all()
    serializer_class = AmazonSerializer
    parser_classes = (JSONParser, MultiPartParser)

    def create(self, request, *args, **kwargs):
        """
        亚马逊tts  默认为girl \n
        :param request: \n
            {"text":"my name is tts!","sex":"boy"}
        :param args: \n
        :param kwargs: \n
        :return: \n
        """
        text = request.data.get("text")
        if not text:
            data = {"detail": "text不能为空", "code": 400}
            return Response(rsp_msg_400(data=data, msg="text不能为空"), status=status.HTTP_200_OK)
        sex = request.data.get("sex", "girl")
        # 当前中文没有男生 进行限制
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zhPattern.search(text)
        if match and sex == 'boy':
            return Response(rsp_msg_400('内容存在中文时 不能使用男生'), status=status.HTTP_200_OK)
        amazon_url = ''
        # 检查是否存在文件夹 并进行创建
        # amazon = Amazon()
        # amazon_path = media_path(amazon, '')
        # path = os.path.join(MEDIA_ROOT + '/' + amazon_path)
        # if not os.path.exists(path):
        #     os.makedirs(path)
        try:
            amazon = Amazon.objects.get(text=text)
        except:
            # 生成语音
            amazon_url, obj_new = amazon_voice(text, sex)
        else:
            # 判断本地是否有文件
            if sex == 'girl':
                if not os.path.exists(amazon.tts_girl.path):
                    amazon_url, obj_new = amazon_voice(text, sex)
                else:
                    amazon_url = amazon.tts_girl.url
            elif sex == 'boy':
                if not os.path.exists(amazon.tts_boy.path):
                    amazon_url, obj_new = amazon_voice(text, sex)
                else:
                    amazon_url = amazon.tts_boy.url
        return Response(rsp_msg_200({'amazon_url': amazon_url}), status=status.HTTP_200_OK)

    # @list_route(methods=['POST'])
    # def test_amazon(self, request):
    #
    #     polly_service = boto3.client(
    #         'polly',
    #         # aws_access_key_id='AKIAJRBNGPM64F3W23SQ',
    #         # aws_secret_access_key='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',
    #         region_name='us-east-2'
    #     )
    #     my_text = 'Additionally, we\'ll need pygame to play our mp3'
    #     polly_response = polly_service.synthesize_speech(
    #         OutputFormat='mp3',
    #         Text=my_text,
    #         TextType='text',
    #         VoiceId='Emma'  # English - British female voice
    #     )
    #
    #     with open('d:\\polly_stream.mp3', 'wb') as f:
    #          f.write(polly_response['AudioStream'].read())
    #     #
    #     # session = Session(profile_name="zheng.zhang")
    #     # polly = session.client("polly")
    #     # user = request.user
    #     # word = request.data.get('word')
    #     # voice = request.data.get('voice')
    #     # polly = client("polly", region_name="us-east-2:88aacbb5-89ff-46f9-8fae-6d53b667ac70")
    #     # response = polly.synthesize_speech(Text=word, OutputFormat="mp3",
    #     #                                 VoiceId=voice)
    #     # polly = client("polly", 'us-east-2')
    #     # response = polly.synthesize_speech(
    #     #     Text="Good Morning. My Name is Rajesh. I am Testing Polly AWS Service For Voice Application.",
    #     #     OutputFormat="mp3",
    #     #     VoiceId="Raveena")
    #
    #     print(polly_response)
    #
    #     # if "AudioStream" in polly_response:
    #     #     with closing(polly_response["AudioStream"]) as stream:
    #     #         data = stream.read()
    #     #         fo = open("pollytest.mp3", "w+")
    #     #         fo.write(data)
    #     #         fo.close()
    #     return Response({"detail": "购买成功", "code": 200}, status=status.HTTP_200_OK)


def amazon_voice(text, sex):
    amazon_parmas = {
        'text': text,
    }
    obj_new, flag = Amazon.objects.update_or_create(**amazon_parmas)
    max_count = obj_new.id
    voice_name_boy = media_path(obj_new, str(max_count) + '_' + 'boy' + '.mp3')
    voice_name_girl = media_path(obj_new, str(max_count) + '_' + 'girl' + '.mp3')
    obj_new.tts_boy = voice_name_boy
    obj_new.tts_girl = voice_name_girl
    obj_new.save()
    polly_service = boto3.client(
        'polly',
        region_name='us-east-2'
    )
    # 判断一段文本中是否包含简体中文：
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    match = zhPattern.search(text)

    if match:
        # 中文只生成一个女生文件
        polly_boy_response = polly_service.synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            TextType='text',
            VoiceId='Zhiyu'
        )
        voice_path = settings.MEDIA_ROOT + '/' + voice_name_girl

        with open(voice_path, 'wb') as f:
            f.write(polly_boy_response['AudioStream'].read())

        # polly_boy_response = polly_service.synthesize_speech(
        #     OutputFormat='mp3',
        #     Text=text,
        #     TextType='text',
        #     VoiceId='Zhiyu'
        # )
        # voice_path = settings.MEDIA_ROOT + '/' + voice_name_girl
        #
        # with open(voice_path, 'wb') as f:
        #     f.write(polly_boy_response['AudioStream'].read())

    else:
        polly_boy_response = polly_service.synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            TextType='text',
            VoiceId='Joey'  # English - British female voice
        )
        voice_path = settings.MEDIA_ROOT + '/' + voice_name_boy

        with open(voice_path, 'wb') as f:
            f.write(polly_boy_response['AudioStream'].read())

        polly_boy_response = polly_service.synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            TextType='text',
            VoiceId='Salli'  # English - British female voice
        )
        voice_path = settings.MEDIA_ROOT + '/' + voice_name_girl

        with open(voice_path, 'wb') as f:
            f.write(polly_boy_response['AudioStream'].read())
    # amazon_parmas = {
    #     'activity': activity,
    #     'text': text,
    #     "tts_boy": voice_name_boy,
    #     "tts_girl": voice_name_girl
    # }
    # amazon_parmas['id'] = max_count
    # try:
    #     obj_new = Amazon.objects.create(**amazon_parmas)
    # except:
    #     amazon_parmas['id'] = max_count + 1
    #     obj_new = Amazon.objects.create(**amazon_parmas)\

    if sex == "boy":
        tts_url = obj_new.tts_boy.url
    else:
        tts_url = obj_new.tts_girl.url

    return tts_url, obj_new


class LocResInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocResInfo.objects.all()
    serializer_class = LocResInfoSerializer
