import requests
import six
import json
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException, _get_error_details


class BFValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail, code=None, extra=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        data = {"data": {}, "code": self.status_code, "message": detail}
        if extra is not None:
            if isinstance(extra, dict):
                data.update(extra)

        self.detail = _get_error_details(data, code)

    def __str__(self):
        return six.text_type(self.detail)


class BFPermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You do not have permission to perform this action.')
    default_code = 'permission_denied'

    def __init__(self, detail, code=None, extra=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        data = {"data": {}, "code": self.status_code, "message": detail}
        if extra is not None:
            if isinstance(extra, dict):
                data.update(extra)

        self.detail = _get_error_details(data, code)

    def __str__(self):
        return six.text_type(self.detail)


def fmt_url_post(url, **param_dict):
    json_data = json.dumps(param_dict)
    # .encode('utf8')
    # req = Request(method="POST", url=url, data=json_data, headers={'Content-Type': 'application/json'})
    # res = urlopen(req)
    headers = {'Content-Type': 'application/json'}
    response_data = requests.post(url, data=json_data, headers=headers).text
    return response_data

