import sys

from bigfish.apps.bigfish.backend.sync_basic_data.utils import sync_data

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.schools.models import Subjects, Segment, School, Grade, Klass
from bigfish.apps.users.models import BigfishUser

# =======================================用户
basic_list = ["person", "subject", "segment", "school", "grade", "class"]
identity = (
    (1, 5),
    (2, 1),
    (3, 2),
    (4, 7),
    (5, 9),

)


def sync_user():
    """
    同步用户

    :return: \n

    """
    # basic user
    data_list = sync_data("sysUser")
    queryset_list = []
    for data in data_list:
        params = {
            "username": data.get("id"), "realname": data.get("truename", ""),
            "nickname": data.get("username", ""), "telephone": data.get("mobile", ""), "email": data.get("email", ""),
            "card_id": data.get("idCard", ""), "wechat": data.get("wechat", ""), "openid": data.get("openid", ""),
            "is_active": (not data.get("userStatus", True))
        }
        print("sys user------{}".format(params))
        queryset_list.append(BigfishUser(**params))
    try:
        BigfishUser.objects.bulk_create(queryset_list)
    except Exception as e:
        print("============={}".format(e))
        sys.exit(-1)
    # user extra
    data_list = sync_data("sysUserExt")
    queryset_list = []
    for data in data_list:
        params = {
            "username": data.get("id"), "realname": data.get("truename", ""),
            "nickname": data.get("username", ""), "telephone": data.get("mobile", ""), "email": data.get("email", ""),
            "card_id": data.get("idCard", ""), "wechat": data.get("wechat", ""), "openid": data.get("openid", ""),
            "is_active": (not data.get("userStatus", True))
        }
        print("sys user------{}".format(params))
        kwargs = {"id": data.get("id")}
        BigfishUser.objects.update_or_create(defaults=params, **kwargs)
    try:
        BigfishUser.objects.bulk_create(queryset_list)
    except Exception as e:
        print("============={}".format(e))


def sync_extra():
    # user extra
    data_list = sync_data("sysUserExt")
    for data in data_list:
        params = {
            "username": data.get("userType"), "realname": data.get("authStatus", ""),
            "nickname": data.get("schoolOrgId", ""), "telephone": data.get("schoolOrgName", ""),
            "email": data.get("remark", "")
        }
        print("sys user------{}".format(params))
        kwargs = {"id": data.get("userId")}
        BigfishUser.objects.update_or_create(defaults=params, **kwargs)


# =======================================学校
def sync_subject():
    """
    同步学科

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "学科 id",
                        "subjectName": "学科名称",
                        "subjectShortName": "简称",
                        "sortNo": "序号",
                        "isDeleted": "是否逻辑删除标识（0-未删除，1-已删除）",
                        "createdBy": "创建人 id",
                        "createdDt": "创建时间",
                        "updatedBy": "更新人 id",
                        "updatedDt": "更新时间",
                        "version": "版本号",
                        "customerId": "客户 id",
                        "appId": "应用 id",
                        "remark": "备注"
                    }
                ]
            }buil
        }
    """
    data_list = sync_data("subject")
    queryset_list = []
    for data in data_list:
        print("subject------{}".format(data))
        queryset_list.append(
            Subjects(id=data.get("id"), title=data.get("subjectName", ""),
                     short_name=data.get("subjectShortName", ""),
                     order=data.get("sortNo", ""), is_active=data.get("isDeleted", "")))
    try:
        Subjects.objects.bulk_create(queryset_list)
    except Exception as e:
        print("==============={}".format(e))
    else:
        print("***************sync_subject success")


def sync_segment():
    """
    同步学段

    :return:
    """
    data_list = sync_data("segment")
    queryset_list = []
    for data in data_list:
        print("segment------{}".format(data))
        queryset_list.append(Segment())
    try:
        Segment.objects.bulk_create(queryset_list)
    except Exception as e:
        print("==============={}".format(e))
    else:
        print("***************sync_segment success")


def sync_school():
    """
    同步学校

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "学校（机构）id",
                        "parentId": "父机构 id",
                        "parentIds": "父机构 ids",
                        "orgNum": "学校（机构）代码",
                        "orgName": "学校（机构）名称",
                        "orgShortName": "学校（机构）简称",
                        "orgNameEn": "学校（机构）英文",
                        "orgTypeCode": "机构类型",
                        "orgLevelCode": "机构等级",
                        "orgIntroduction": "学校（机构）简介",
                        "img": "学校（机构）图片",
                        "orgAddress": "学校（机构）详细地址",
                        "areaId": "学校（机构）所属行政区划码",
                        "areaInfo": "学校（机构）所属区域",
                        "postNum": "邮政编码",
                        "contactName": "联系人",
                        "contactMobile": "联系电话",
                        "contactFaxMobile": "传真电话",
                        "email": "电子邮箱",
                        "webUrl": "主页地址",
                        "sortNo": "排序",
                        "remark": "备注",
                        "syncStatus": ""
                    }
                ]
            }
        }
    """
    data_list = sync_data("school")
    queryset_list = []
    for data in data_list:
        print("school------{}".format(data))
        queryset_list.append(
            School(id=data.get("id"), title=data.get("orgName", ""), coding=data.get("orgNum", ""),
                   short_name=data.get("orgShortName", ""), en_title=data.get("orgNameEn", ""),
                   org_introduction=data.get("orgIntroduction", ""), org_address=data.get("orgAddress", ""),
                   post_num=data.get("postNum", ""), contact_name=data.get("contactName", ""),
                   contact_mobile=data.get("contactMobile", ""), contact_fax_mobile=data.get("contactFaxMobile", ""),
                   email=data.get("email", ""), web_url=data.get("webUrl", ""), order=data.get("sortNo", "")
                   )
        )
    try:
        School.objects.bulk_create(queryset_list)
    except Exception as e:
        print("==============={}".format(e))
    else:
        print("***************sync_school success")


def sync_grade():
    """
    同步年级

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "年级 id",
                        "gradeNo": "年级编号",
                        "gradeName": "年级名称",
                        "aliasName": "年级别名",
                        "segmentId": "学段 id",
                        "segmentName": "学段名称",
                        "sortNo": "序号",
                        "isDeleted": "是否逻辑删除标识（0-未删除，1-已删除）",
                        "createdBy": "创建人 id",
                        "createdDt": "创建时间",
                        "updatedBy": "更新人 id",
                        "updatedDt": "更新时间",
                        "version": "版本号",
                        "appId": "应用 id",
                        "customerId": "客户 id",
                        "remark": "备注"
                    }
                ]
            }
        }
    """
    data_list = sync_data("grade")
    queryset_list = []
    for data in data_list:
        print("grade------{}".format(data))
        queryset_list.append(
            Grade(id=data.get("id"), title=data.get("gradeName", ""), coding=data.get("gradeNo", ""),
                  short_name=data.get("aliasName", ""), segment=data.get("segmentId", ""),
                  segment_name=data.get("segmentName", ""), is_acitve=data.get("isDeleted", ""),
                  order=data.get("sortNo", "")
                  )
        )
    try:
        Grade.objects.bulk_create(queryset_list)
    except Exception as e:
        print("==============={}".format(e))
    else:
        print("***************sync_grade success")


def sync_klass():
    """
    同步班级

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "班级 id",
                        "schoolId": "学校 id",
                        "schoolName": "学校",
                        "className": "班级名称",
                        "classTypeCode": "班级类型 zxxbjlx",
                        "lengthSchooling": "学制类型：1-六三制；2-五四制",
                        "gradeId": "所属年级 id",
                        "gradeName": "所属年级名称",
                        "segmentId": "所属学段 id",
                        "segmentName": "所属学段名称",
                        "syncStatus": ""
                    }
                ]
            }
        }
    """
    data_list = sync_data("klass")
    queryset_list = []
    for data in data_list:
        print("klass------{}".format(data))
        queryset_list.append(
            Klass(id=data.get("id"), title=data.get("className", ""), coding=data.get("gradeNo", ""),
                  class_type=data.get("classTypeCode", ""), length_schooling=data.get("lengthSchooling", ""),
                  school=data.get("schoolId", ""), school_name=data.get("schoolName", ""),
                  belong_grade=data.get("gradeId", ""), grade=data.get("gradeName", ""),
                  segment=data.get("segmentId", ""), segment_name=data.get("segmentName", "")
                  )
        )
    try:
        Klass.objects.bulk_create(queryset_list)
    except Exception as e:
        print("==============={}".format(e))
    else:
        print("***************sync_klass success")


def main_func():
    sync_subject()
    # sync_segment()
    sync_school()
    sync_grade()
    sync_klass()


if __name__ == '__main__':
    # main_func()
    data_list = sync_data("sysUser")
    for item in data_list:
        print(item)
