from bigfish.base.response import BFPermissionDenied, BFValidationError


def check_wechat_env(view):
    """
    检查微信环境

    :param view:
    :return:
    """

    def decorator(request, *args, **kwargs):
        if hasattr(request, "META"):
            req = request
        elif hasattr(request, "request"):
            req = request.request
        else:
            raise BFValidationError("未知环境！")
        try:
            user_agent = str(req.META.get("HTTP_USER_AGENT")).lower()
        except Exception as e:
            raise BFValidationError("未知环境！【{}】".format(e))
        if "micromessenger" in user_agent:
            return view(request, *args, **kwargs)
        raise BFPermissionDenied("请从微信端访问")

    return decorator
