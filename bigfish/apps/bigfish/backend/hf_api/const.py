APP_ID = "demo"
APP_SECRET = "102749291019210910"

BASE_URL = "http://175.102.179.20:8000"
LOGIN_URL = "http://175.102.179.20:7052/sso/login"
CHECK_ACCESS_TOKEN_URL = "{}/aep/oauth/check_token".format(BASE_URL)  # 验证访问令牌
GET_USER_INFO_URL = "{}/aep/oauth/user_info".format(BASE_URL)  # 验证访问令牌
GET_API_TOKEN_URL = "{}/aep/gateway/api_token".format(BASE_URL)
