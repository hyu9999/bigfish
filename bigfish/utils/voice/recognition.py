# var hash = crypto.createHash('md5');
# //讯飞开放平台注册申请应用的应用ID(APPID)
# var xAppid = "5ade89a0";
# console.log('X-Appid:'+xAppid);
# var timestamp = Date.parse(new Date());
# var curTime = timestamp / 1000;
# console.log('X-CurTime:'+curTime);
# var xParam = {"engine_type": "sms-en16k", "aue": "raw", "scene": "main"}
# xParam = JSON.stringify(xParam);
# var xParamBase64 = new Buffer(xParam).toString('base64');
# console.log('X-Param:'+xParamBase64);
# //音频文件
# var fileData = fs.readFileSync(fname);
# var fileBase64 = new Buffer(fileData).toString('base64');
# console.log(fileBase64);
# var bodyData = "audio="+fileBase64;
# //ApiKey创建应用时自动生成
# var apiKey = "bf7f8919d9c08936459882ef25377fcb";
# var token = apiKey + curTime+ xParamBase64 ;
# hash.update(token);
# var xCheckSum = hash.digest('hex');
# console.log('X-CheckSum:'+xCheckSum);

# -*- coding: UTF-8 -*-
from urllib.parse import urlencode

import requests
import time
import json
import hashlib
import base64

from bigfish.base.choices import ENGINE_TYPE
from bigfish.base.const import XF_VOICE_RECOGNITION_API_KEY, XF_VOICE_RECOGNITION_APP_ID, XF_VOICE_RECOGNITION_URL
from bigfish.base.response import BFValidationError


def get_voice_recognition_header(engine_type=2):
    cur_time = str(int(time.time()))
    try:
        param = '{{"engine_type": "{}", "aue": "raw", "scene": "main"}}'.format(
            [x[1] for x in ENGINE_TYPE if x[0] == engine_type][0])
    except Exception as e:
        raise BFValidationError("语音识别错误")
    param_base64 = base64.b64encode(param.encode('utf-8'))
    token = "{}{}{}".format(XF_VOICE_RECOGNITION_API_KEY, cur_time, str(param_base64, 'utf-8'))
    m2 = hashlib.md5()
    m2.update(token.encode('utf-8'))
    check_sum = m2.hexdigest()
    header = {
        'X-CurTime': cur_time,
        'X-Param': param_base64,
        'X-Appid': XF_VOICE_RECOGNITION_APP_ID,
        'X-CheckSum': check_sum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


def main():
    f = open("1548048886.544.wav", 'rb')
    file_content = f.read()
    base64_audio = base64.b64encode(file_content)
    body = urlencode({'audio': base64_audio})

    r = requests.post(XF_VOICE_RECOGNITION_URL, headers=get_voice_recognition_header(), data=body)
    result = json.loads(str(r.content, 'utf-8'))
    print(result)


if __name__ == '__main__':
    main()
    # param = b'haha'
    # paramBase64 = base64.b64encode(param)
    # print(paramBase64)
