import hashlib
import time

import requests

from bigfish.apps.bigfish.backend.hf_api.const import APP_ID, APP_SECRET, GET_API_TOKEN_URL, CHECK_ACCESS_TOKEN_URL, \
    LOGIN_URL, GET_USER_INFO_URL


class HFApi:
    def __init__(self, app_id=APP_ID, app_secret=APP_SECRET, access_token="99628e66-2428-44a2-848a-8918cf018d39"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token

    def login(self):
        """
        登陆接口

        :return:\n
            {
                "retCode": "000000",
                "retDesc": "login sucess!",
                "data": {
                    "truename": "魏小明",
                    "schoolOrgName": "云南省教育厅",
                    "userTypeList": "5,4",
                    "authStatus": "1",
                    "groupId": "97373",
                    "schoolOrgId": "1070991875590381569",
                    "roleList": [
                        {
                            "authority": "1070998778387120129",
                            "roleId": "1070998778387120129",
                            "roleName": "org-admin"
                        }
                    ],
                    "userId": "1070997593651429378",
                    "spaceName": "魏小明",
                    "imgFileId": "1096240262564601857",
                    "HF_Auth_Token": "fa8d38b1-babe-4612-85a2-d598c7f664c0",
                    "userType": "5",
                    "subsiteGroupId": "96658",
                    "username": "weixiaoming"
                }
            }
        """
        data = {
            "username": "weixiaoming",
            "password": "98d1395f97e8ca5ea6cf9021144849275f7150f6fa1d0d9217f27b61cbdfc667d59a0233be08eba3c98562abeeee194eda0933d369f7ffea5792be714fa3e2b0d38b44c53fc96900a2bca215174d510d6a683e959d625eb3fd7eeb0e9a1325d94c1b62e55b7b6cdd1da57bbdc112659091b79a5d1f9be2192d85e903325ff3db",
            "loginType": "1",
            "groupId": "97373",
        }
        rq = requests.post(url=LOGIN_URL, data=data)
        return rq.json()

    def get_sign(self, api_token=""):
        """
        接口签名
        sign=md5(appId +appSecret+ timestamp + apiToken)

        :param api_token:请求接口凭证。除获取 apiToken 自身的接口中不需要携带外，其他所有接口均需携带；
        :return:
            {
                "app_id": "",
                "timestamp": "",
                "sign":""
            }
        """
        timestamp = int(time.time())
        sign = hashlib.md5((self.app_id + self.app_secret + str(timestamp) + api_token).encode("utf8")).hexdigest()
        return {"app_id": self.app_id, "timestamp": str(timestamp), "sign": sign}

    def get_headers(self, api_token=""):
        """
        获取请求头

        :param api_token:
        :return:
        """
        headers = {
            "appId": self.app_id

        }
        if api_token:
            headers["apiToken"] = api_token
        headers.update(self.get_sign(api_token=api_token))
        return headers

    def check_access_token(self, api_token):
        """
        检测access token

        :param api_token:
        :return:
        """
        data = {
            "accessToken": self.access_token
        }
        headers = self.get_headers(api_token)
        rq = requests.post(url=CHECK_ACCESS_TOKEN_URL, data=data, headers=headers)
        return rq.json()

    def get_user_info(self, api_token):
        """
        获取用户基本信息

        :param api_token:
        :return:
        """
        data = {"accessToken": self.access_token}
        headers = self.get_headers(api_token)
        rq = requests.post(url=GET_USER_INFO_URL, data=data, headers=headers)
        return rq.json()

    def get_api_token(self):
        """
        获取 api token

        :return:
            {

            }
        """
        headers = self.get_headers()
        rq = requests.get(GET_API_TOKEN_URL, headers=headers)
        return rq.json()


if __name__ == '__main__':

    hf = HFApi()
    # ll = hf.login()
    # print(ll)
    aa = hf.get_api_token()
    apiToken = aa.get("data").get("apiToken")
    userinfo = hf.get_user_info(apiToken)
    print(userinfo.get("data").get("username"))