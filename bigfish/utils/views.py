# encoding: utf-8

"""
@author: h3l
@contact: xidianlz@gmail.com
@file: views.py.py
@time: 2017/7/10 18:07
"""
import os

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import decorators
from rest_framework.response import Response
from rest_framework.reverse import reverse

from bigfish.base.permissions import Everyone
from .forms import FileForm
from .functions import generate_file_name


@decorators.api_view()
@decorators.permission_classes([Everyone])
def sitemap(request):
    """
    提供用户列表，学校列表，班级列表，文件上传地址链接信息
    """
    return Response({
        "users": reverse("user-list", request=request),
        "school": reverse("school-list", request=request),
        "class": reverse("klass-list", request=request),
        "upload_file": reverse("upload_file", request=request)
    })


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        file_type = request.FILES['file'].name.split('.', 1)[1]
        file_name = generate_file_name(file_type)
        if form.is_valid():
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            return JsonResponse({
                "url": "http://" + request.get_host() + "{}{}".format(settings.MEDIA_URL, file_name),
                "submit": "{}{}".format(settings.MEDIA_URL, file_name)
            }, status=201)


@csrf_exempt
def ci(request):
    import os
    os.system("/bin/bash /home/ubuntu/project/bigfish/deploy_new/ci.sh")
    return HttpResponse("success")
