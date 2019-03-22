from channels.routing import route

from bigfish.apps.users.consumers import ws_connect, ws_disconnect, ws_receive


channel_routing = [
    # route('websocket.connect', ws_connect, path=r'/(?P<klass>.*)$'),  # 连接时调用
    route('websocket.connect', ws_connect, path=r'/api/auth/login/'),  # 连接时调用
    route('websocket.disconnect', ws_disconnect),  # 断开链接调用
    route('websocket.receive', ws_receive)  #
]