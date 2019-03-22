import datetime
import hashlib
import json
import requests
import uuid


class SingSoundEngine(object):
    """先声引擎"""

    SINGSOUND_WARRANT_SERVER_URL = "http://api.cloud.ssapi.cn:8080/auth/authorize"
    SINGSOUND_GINGER_SERVER_URL = "http://api.cloud.ssapi.cn:8080"
    APP_KEY = 'a368'
    SECRET_KEY = 'c11163aa6c834a028da4a4b30955be49'
    USER_ID = ""
    CLIENT_IP = '106.14.222.232'  # 需要换成真实ip

    def __init__(self, username):
        self.USER_ID = username

    # @staticmethod
    # def get_file_path(url, with_uuid=False):
    #     """
    #     将音频链接下载为缓存文件，使用后需要调用 clear 方法清空缓存
    #
    #     :param url:
    #     :param with_uuid:
    #     :return: work_space object, string
    #     """
    #     try:
    #         data = urlopen(url, timeout=30).read()
    #     except:
    #         if with_uuid:
    #             return None, None, None
    #         return None, None
    #     uuid_str = uuid.uuid1().get_urn().replace(":", "")
    #     work_space = WorkSpace(usage='voice_tag_ask_engine')
    #     work_space.create()
    #     file_path = os.path.join(work_space.dir, uuid_str + '.mp3')
    #     work_space.save_file(data_or_fp=data, path=file_path)
    #     if with_uuid:
    #         return work_space, file_path, uuid_str
    #     return work_space, file_path

    @classmethod
    def get_warrant(cls):
        """
        :return: 1.系统返回的warrant_id  2.请求的signature
        """
        params = dict(
            appid=cls.APP_KEY,
            user_id=cls.USER_ID,
            user_client_ip=cls.CLIENT_IP,
            timestamp=str(datetime.datetime.now().timestamp())[:10],
            app_secret=cls.SECRET_KEY
        )
        sig = cls.calculate_sign(params)
        params.update(
            request_sign=
            sig
        )
        response = requests.post(
            url=cls.SINGSOUND_WARRANT_SERVER_URL,
            data=params
        )
        return json.loads(bytes.decode(response.content))['data']['warrant_id'], sig

    @staticmethod
    def calculate_sign(params):

        def _build_md5_str(params):
            return '&'.join(
                [
                    k + '=' + params[k]
                    for k in sorted(params.keys())
                ]
            )

        md5_hash = hashlib.md5()
        signature = _build_md5_str(params).encode(encoding='utf-8')
        md5_hash.update(signature)
        return md5_hash.hexdigest()

    @classmethod
    def load_config(cls, request, coreType):
        """

        :param request_id:
        :param connect_id:
        :param warrant_id:
        :return: 已经封装好的 1.请求url 2. text请求体，均为评测体的重要组成
        """

        def version(a, b, c):
            return (a * (2 << 15) | b * (2 << 7) | c) * (2 << 7)

        def construct_url(request_id, connect_id, warrant_id):
            params = dict(
                appkey=cls.APP_KEY,
                connect_id=request_id,
                request_id=connect_id,
                warrant_id=warrant_id,

            )
            return cls.SINGSOUND_GINGER_SERVER_URL + "/" + coreType + "?" + \
                   '&'.join([str(k) + '=' + str(v) for k, v in params.items()])

        request_id = str(uuid.uuid4()).replace("-", "")
        connect_id = str(uuid.uuid4()).replace("-", "")
        warrant_id, sig = cls.get_warrant()
        request.update(request_id=request_id)
        connect = dict(
            cmd='connect',
            param=dict(
                sdk=dict(
                    version=version(1, 1, 1),
                    source=6,
                    type=1,
                    arch='x86_64',
                    os='linux',
                    protocol=2,
                    os_version='4.4.0-93-generic',
                    product='default'
                ),
                app=dict(
                    applicationId=cls.APP_KEY,
                    timestamp=str(datetime.datetime.now().timestamp())[:10],
                    signature=sig,
                    sig=sig,
                    warrantId=warrant_id,
                    connect_id=connect_id
                )
            )
        )
        start = dict(
            cmd='start',
            param=dict(
                app=dict(
                    applicationId=cls.APP_KEY,
                    timestamp=str(datetime.datetime.now().timestamp())[:10],
                    signature=sig,
                    sig=sig,
                    warrantId=warrant_id,
                    userId=cls.USER_ID,
                    clientId='default'
                ),
                audio=dict(
                    sampleRate=16000,
                    channel=1,
                    sampleBytes=2,

                    # sampleRate=44100,
                    # channel=1,
                    # sampleBytes=2,
                    audioType='wav',
                ),
                request=request
            )
        )
        text = dict(
            start=start,
            connect=connect
        )
        url = construct_url(
            connect_id=connect_id,
            request_id=request_id,
            warrant_id=warrant_id
        )
        return url, text

    @classmethod
    def send_evaluation_request(cls, coreType, request, audio):
        """
        向先声引擎发出请求，返回音频打分结构
        coreType
        评测题型
        text
        评测请求体
        JSON格式
        audio
        音频内容
        二进制音频内容
        """

        url, text = cls.load_config(request, coreType)
        files = {'text': json.dumps(text), 'audio': open(audio, 'rb')}
        headers = {'Request-Index': "0"}
        r = requests.post(url, files=files,
                          headers=headers, timeout=600000)
        # print(r.json())
        return r.text

    @classmethod
    def send_pqan_evaluation(cls, answers, audio_url, keys):
        """
        向先声引擎发出请求，返回音频打分结构，题型为问答题
        参数结构：
        {
            "coreType": "en.pqan.score",
            "para": "paragraph, blablabla..."
            "quest_ans": "What makes Mr. Bean so successful?",
            "lm": [
                    {"text" : "It's his giftedness and hard works that make him succeed."},
                    {"text" : "his talents and hard works."}
                    ],
            "key":[{"test" : "foo"},{}]      # 关键词
        }
        """
        core_type = "en.pqan.score"
        # 空文本报错
        work_space, file_path = None, None
        try:
            if not answers:
                return 0, 0
            if audio_url:
                work_space, file_path = cls.get_file_path(audio_url)
                if not work_space:
                    return False

            request = dict(
                tokenId='1',  # 该参数不影响打分
                coreType=core_type,
                para="whatever",  # 该参数不影响打分
                quest_ans='qs',  # 该参数不影响打分
                lm=[dict(text=answer) for answer in answers],
                key=[dict(text=[key for key in keys])]
            )

            response = cls.send_evaluation_request(core_type, request, file_path)

            return json.loads(response)['result']['overall']
        except Exception as e:
            print('singsound fail {error_message}'.format(error_message=e))
            return False
        finally:
            if work_space:
                work_space.clear()


if __name__ == "__main__":
    obj = SingSoundEngine()

    result = obj.send_evaluation_request("en.word.score",
                                         {"coreType": "en.pred.score",
                                          "refText": "This is my father. This is my mother. This is my brother. This is my sister. This is me!",
                                          "rank": 100, "precision": 0.5, "tokenId": "default",
                                          "sampleRate": 44100,
                                          "channel": 1,
                                          "sampleBytes": 2
                                          }, "demo.wav")
    print(result)
