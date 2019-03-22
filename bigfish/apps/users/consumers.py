import datetime
import json
import logging
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from bigfish.apps.operation.models import OperationRecord
from bigfish.apps.textbooks.models import Activity
from bigfish.apps.users.models import BigfishUser, UserOnline, OnlineReport
from bigfish.apps.classrooms.models import BlackSetting, Classroom
from bigfish.base.ret_msg import rsp_msg_400, rsp_msg_200


logger = logging.getLogger('django')


@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({'text': '成功连接'})
    print('==========长连接成功============')


@channel_session_user
def ws_disconnect(message):
    """长连接异常断开"""
    try:
        username = message.channel_session['username']
        klass_id = message.channel_session['klass_id']
    except:
        logger.debug('该用户没有登录')
        return
    now_time = datetime.datetime.now()
    # 记录退出行为
    user_online = UserOnline.objects.get(user__username=username)
    online_time = user_online.online_time
    report_online_time = int((now_time - user_online.last_login).total_seconds() * 1000)
    online_time += report_online_time
    UserOnline.objects.filter(user__username=username).update(
        **{"is_online": False, 'last_logout': now_time, 'online_time': online_time})
    # 更新OnlineReport
    online_report_data = {'logout_time': now_time, 'online_time': report_online_time}
    OnlineReport.objects.filter(user__username=username, login_time=user_online.last_login).update(**online_report_data)
    send_message(klass_id, 'logout')
    Group(str(klass_id)).discard(message.reply_channel)
    print('==========长连接断开连接============')


@channel_session_user
def ws_receive(message):
    """
    长连接消息交互
    """
    message_obj = message
    message = message.content['text']
    message = json.loads(message)
    print('请求参数是： {}'.format(message))
    klass_id = message['data'].get('klass_id', None)
    username = message['data'].get('username', None)
    if isinstance(message, dict):
        if message['type'] == 'black_screen':
            # 黑屏
            pass
        elif message['type'] == 'socket_ping':
            # 心跳包消息
            pass
        elif message['type'] == 'logout':
            # 退出登录
            logout(username, message_obj)
            send_message(str(klass_id), message['type'])
            Group(str(klass_id)).discard(message_obj.reply_channel)
            # 前端用此消息判断是否刷新用户在线页面
            send_message(str(klass_id), 'online_status')
            return
        elif message['type'] == 'login':
            # 登录
            message_obj.channel_session['username'] = username
            message_obj.channel_session['klass_id'] = klass_id
            login(username, klass_id, message_obj)
            # 是否有正在开启的课堂
            filtrate_classroom_data(message_obj, klass_id)
            # 前端用此消息判断是否刷新用户在线页面
            send_message(str(klass_id), 'online_status')
        elif message['type'] == 'classroom':
            class_room = Classroom.objects.filter(klass_id=klass_id).order_by('-start_time').first()
            send_message(str(klass_id), message['type'], {'classroom_id': class_room.id})
            return
        elif message['type'] == 'classroom_out':
            pass
        elif message['type'] == 'activity':
            # 开启活动
            activity_id = message['data'].get('activity_id', None)
            send_message(str(klass_id), message['type'], {'activity_id': activity_id})
            return
        elif message['type'] == 'activity_out':
            activity_id = message['data'].get('activity_id', None)
            send_message(str(klass_id), message['type'], {'activity_id': activity_id})
            return
        elif message['type'] == 'online_status':
            pass
        send_message(str(klass_id), message['type'])

    else:
        message_dict = {'message': '参数类型不正确'}
        Group(str(klass_id)).send({
            'text': json.dumps({
                'data': json.dumps(message_dict, ensure_ascii=False)
            }, ensure_ascii=False)
        })


def send_message(klass_id, type, data=None):
    if data is None:
        Group(str(klass_id)).send({
            'text': json.dumps({
                'type': type
            }, ensure_ascii=False)
        })
    else:
        Group(str(klass_id)).send({
            'text': json.dumps({
                'type': type,
                'data': data
            }, ensure_ascii=False)
        })


def login(username, klass_id, message_obj):
    try:
        Group(str(klass_id)).add(message_obj.reply_channel)
        user = BigfishUser.objects.get(username=username)
    except:
        message_obj.reply_channel.send({'text': json.dumps(
            '用户不存在',
            ensure_ascii=False
        )})
        return
    now_time = datetime.datetime.now()
    # 修改用户登录状态和登录时间
    UserOnline.objects.update_or_create(defaults={"is_online": True, 'last_login': now_time}, **{'user': user})
    try:
        OnlineReport.objects.get(user=user, login_time=now_time)
    except:
        OnlineReport.objects.create(**{'user': user, 'login_time': now_time})
    # 检查用户是否被标记
    try:
        user_online = UserOnline.objects.get(user__username=username)
    except Exception as e:
        logger.debug(e)
        return
    if user_online.is_mark:
        user_online.is_mark = False
        user_online.status = 0
        user_online.save()


def logout(username, message_obj):
    """正常退出"""
    now_time = datetime.datetime.now()
    try:
        user_online = UserOnline.objects.get(user__username=username)
    except:
        message_obj.reply_channel.send({'text': json.dumps(
            '用户没有记录在线状态表',
            ensure_ascii=False
        )})
        return
    online_time = user_online.online_time
    report_online_time = int((now_time - user_online.last_login).total_seconds() * 1000)
    online_time += report_online_time
    UserOnline.objects.filter(user__username=username).update(
        **{"is_online": False, 'last_logout': now_time, 'online_time': online_time})
    # 更新OnlineReport
    online_report_data = {'logout_time': now_time, 'online_time': report_online_time}
    OnlineReport.objects.filter(user__username=username, login_time=user_online.last_login).update(**online_report_data)


def filtrate_classroom_data(message_obj, klass_id):
    """判断是否有在进行课堂和活动"""
    try:
        classroom = Classroom.objects.filter(klass_id=klass_id, is_open=True).order_by('-start_time').first()
        if classroom:
            # 是否有正在进行的活动
            try:
                operation_record = OperationRecord.objects.filter(classroom=classroom, operate_type_id=1, operation_id=1
                                                              ).order_by('-start_time').first()

                if operation_record.is_finish is False:
                    send_message(str(klass_id), 'classroom',
                                 {'classroom_id': classroom.id, 'activity_id': operation_record.operate_id,
                                  'operation_record_id': operation_record.id})
            except:
                pass
            send_message(str(klass_id), 'classroom', {'classroom_id': classroom.id})
        # 判断黑屏状态
        black_set = BlackSetting.objects.get(klass_id=klass_id)
        if black_set.is_black:
            send_message(str(klass_id), 'black_screen')
        return
    except:
        pass




