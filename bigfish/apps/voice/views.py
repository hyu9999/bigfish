import json
import logging
import os
import time

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bigfish.apps.voice.models import SpeechEvaluation, SpeechEvaluationReport
from bigfish.apps.voice.serializers import SpeechEvaluationSerializer, SpeechEvaluationReportSerializer
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200
from bigfish.utils.voice.evaluation import SingSoundEngine

logger = logging.getLogger('django')


class SpeechEvaluationViewSet(viewsets.ModelViewSet):
    queryset = SpeechEvaluation.objects.all()
    serializer_class = SpeechEvaluationSerializer


class SpeechEvaluationReportViewSet(viewsets.ModelViewSet):
    queryset = SpeechEvaluationReport.objects.all()
    serializer_class = SpeechEvaluationReportSerializer
    parser_classes = (JSONParser, MultiPartParser)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        语音评测记录

        :param request: \n
            {
              "res": "/media/demo.wav",
              "user": 2,
              "name": "classical",
              "eval_type": 1,
              "activity_report": 1,  # 可选
              "activity": 7,  # 可选
              "description": "test"  # 可选
            }
        :param args:
        :param kwargs:
        :return:\n
            {
                "data": {
                    "id": 1,
                    "name": "classical",
                    "res": "http://localhost:8000/media/res/ProRes/unknown/demo.wav",
                    "result": {},
                    "description": null,
                    "create_time": "2019-01-15T09:56:52.458000",
                    "update_time": "2019-01-15T09:56:52.458000",
                    "activity_report": null,
                    "activity": null,
                    "user": 1,
                    "eval_type": 1
                },
                "message": "success",
                "code": 200
            }
        """

        eval_type = request.data.get("eval_type", None)
        try:
            se_obj = SpeechEvaluation.objects.get(id=eval_type)
        except Exception as e:
            raise BFValidationError("未知的测评类型")
        else:
            input_data = se_obj.input
            input_data["refText"] = request.data.get("name", None)
        # 处理blob对象
        blob_obj = request.FILES.get('res', None)
        filename = "{}.mp3".format(time.time())
        try:
            data = [blob_obj.file, blob_obj.field_name, filename, blob_obj.content_type,
                    blob_obj.size, blob_obj.charset, blob_obj.content_type_extra]
        except Exception as e:
            raise BFValidationError("处理文件失败")
        request.data['res'] = InMemoryUploadedFile(*data)

        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
            except Exception as e:
                raise BFValidationError("[fail]{}".format(e))
            instance = serializer.instance
            # 语音识别
            # file_content = instance.res.read()
            # base64_audio = base64.b64encode(file_content)
            # body = urlencode({'audio': base64_audio})
            #
            # r = requests.post(XF_VOICE_RECOGNITION_URL, headers=get_voice_recognition_header(), data=body)
            # result = json.loads(str(r.content, 'utf-8'))
            # if result['code'] != "0":
            #     raise BFValidationError("[语音识别异常]{}".format(result['desc']))
            # else:
            #     instance.voice_recognition = result
            # 语音评测
            media_path = instance.res.url
            loc_path = os.path.join(settings.MEDIA_ROOT[:-5], media_path[1:])
            sse_obj = SingSoundEngine(request.user.username)
            try:
                result = sse_obj.send_evaluation_request(se_obj.en_title, input_data, loc_path)
            except Exception as e:
                logger.error(e)
                raise BFValidationError("获取测评结果失败！")
            instance.result = json.loads(result)
            instance.save()
            serializer = self.get_serializer(instance)
            headers = self.get_success_headers(serializer.data)
        return Response(rsp_msg_200(serializer.data), status=status.HTTP_201_CREATED, headers=headers)
