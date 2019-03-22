import time
from rest_framework import exceptions
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle, BaseThrottle


class LuffyAnonRateThrottle(SimpleRateThrottle):
    """
    匿名用户，根据IP进行限制
    """
    scope = "luffy_anon"

    def get_cache_key(self, request, view):
        # 用户已登录，则跳过 匿名频率限制
        if request.user:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class LuffyUserRateThrottle(SimpleRateThrottle):
    """
    登录用户，根据用户token限制
    """
    scope = "luffy_user"

    def get_ident(self, request):
        """
        认证成功时：request.user是用户对象；request.auth是token对象
        :param request:
        :return:
        """
        # return request.auth.token
        return "user_token"

    def get_cache_key(self, request, view):
        """
        获取缓存key
        :param request:
        :param view:
        :return:
        """
        # 未登录用户，则跳过 Token限制
        if not request.user:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


RECORD = {
    '用户IP': ['127.0.0.1', '192.168.1.110', 12312133, ]
}


class TestThrottle(BaseThrottle):
    ctime = time.time

    def get_ident(self, request):
        """
        根据用户IP和代理IP，当做请求者的唯一IP
        Identify the machine making the request by parsing HTTP_X_FORWARDED_FOR
        if present and number of proxies is > 0. If not use all of
        HTTP_X_FORWARDED_FOR if it is available, if not use REMOTE_ADDR.
        """
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        num_proxies = api_settings.NUM_PROXIES

        if num_proxies is not None:
            if num_proxies == 0 or xff is None:
                return remote_addr
            addrs = xff.split(',')
            client_addr = addrs[-min(num_proxies, len(addrs))]
            return client_addr.strip()

        return ''.join(xff.split()) if xff else remote_addr

    def allow_request(self, request, view):
        """
        是否仍然在允许范围内
        Return `True` if the request should be allowed, `False` otherwise.
        :param request:
        :param view:
        :return: True，表示可以通过；False表示已超过限制，不允许访问
        """
        # 获取用户唯一标识（如：IP）

        # 允许一分钟访问10次
        num_request = 2
        time_request = 60

        now = self.ctime()
        ident = self.get_ident(request)
        print(ident)
        self.ident = ident
        if ident not in RECORD:
            RECORD[ident] = [now, ]
            return True
        history = RECORD[ident]
        while history and history[-1] <= now - time_request:
            history.pop()
        if len(history) < num_request:
            history.insert(0, now)
            return True

    def wait(self):
        """
        多少秒后可以允许继续访问
        Optionally, return a recommended number of seconds to wait before
        the next request.
        """
        last_time = RECORD[self.ident][0]
        now = self.ctime()
        return int(60 + last_time - now)