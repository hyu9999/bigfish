import hashlib

import time

import requests

BASIC_SYNC_URL = "http://175.102.179.20:7146/syn/get_data"
APP_ID = 'admin'


def sync_data(type_name, url=BASIC_SYNC_URL, app_id=APP_ID):
    data = {
        "appId": app_id,
        "type": type_name
    }
    syn_data = []
    rq = requests.post(url=url, data=data)
    ret_data = rq.json()
    code = ret_data.get("retCode", None)
    if code == "000000":
        try:
            syn_data = ret_data.get("data").get("synData")
        except Exception as e:
            print("==============={}".format(e))
            pass
    return syn_data


def get_sign(api_token=""):
    timestamp = int(time.time())
    app_id = 'demo'
    app_secret = "102749291019210910"

    sign = hashlib.md5((app_id + app_secret + str(timestamp) + api_token).encode("utf8")).hexdigest()
    return {"timestamp": str(timestamp), "sign": sign}


def get_token():
    headers = {
        "appId": "demo"
    }
    headers.update(get_sign())
    print(headers)
    rq = requests.get("http://175.102.179.20:8000/aep/gateway/api_token", headers=headers)
    return rq.json()


def check_token(token_val):
    data = {
        "accessToken": token_val
    }
    headers = {
        "appId": "demo",
        "apiToken": token_val,
        'Content-Type': 'application/x-www-form-urlencoded'

    }
    headers.update(get_sign(token_val))
    print(headers)
    rq = requests.post(url="http://175.102.179.20:8000/aep/oauth/check_token", data=data, headers=headers)
    return rq.json()


class HFApi:
    def __init__(self, app_id="demo", app_secret="102749291019210910", base_url="http://175.102.179.20:8000"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url

    def get_sign(self, api_token=""):
        timestamp = int(time.time())
        sign = hashlib.md5((self.app_id + self.app_secret + str(timestamp) + api_token).encode("utf8")).hexdigest()
        return {"app_id": self.app_id, "timestamp": str(timestamp), "sign": sign}

    def get_token(self):
        headers = self.get_sign()
        rq = requests.get("http://175.102.179.20:8000/aep/gateway/api_token", headers=headers)
        return rq.json()

    def check_token(self):
        pass


if __name__ == '__main__':
    tk = get_token()
    token = tk.get("data").get("apiToken")
    print(token)
    flag = check_token(token)
    print(flag)
