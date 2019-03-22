from collections import OrderedDict


def rsp_msg(data=None, msg=None, code=None, extra=None):
    ret = OrderedDict()
    if data is None:
        data = {}
    ret["data"] = data
    ret["message"] = msg or 'success'
    ret["code"] = code or 200
    try:
        ret.update(extra)
    except Exception as e:
        pass
    return ret


def rsp_msg_200(data=None, msg=None, extra=None):
    ret = OrderedDict()
    if data is None:
        data = {}
    ret["data"] = data
    ret["message"] = msg or 'success'
    ret["code"] = 200
    try:
        ret.update(extra)
    except Exception as e:
        pass
    return ret


def rsp_msg_400(msg=None, data=None, extra=None):
    ret = OrderedDict()
    if data is None:
        data = {}
    ret["data"] = data
    ret["message"] = msg or 'fail'
    ret["code"] = 400
    try:
        ret.update(extra)
    except Exception as e:
        pass
    return ret


def rsp_msg_404(msg=None, data=None, extra=None):
    ret = OrderedDict()
    if data is None:
        data = {}
    ret["data"] = data
    ret["message"] = msg or 'not found'
    ret["code"] = 404
    try:
        ret.update(extra)
    except Exception as e:
        pass
    return ret
