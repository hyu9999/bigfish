from bigfish.apps.bigfish.backend.sync_basic_data.utils import sync_data
from bigfish.utils.django.config_settings import config_django

config_django()


# =======================================关系表
def sync_school_segment_rel():
    """
    同步学校学段关系

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "id",
                        "schoolOrgId": "学校 id",
                        "segmentId": "学段 id",
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
            }
        }
    """
    data = sync_data("schoolSegmenrel")
    return data


def sync_segment_grade_rel():
    """
    同步学段年级关系

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "id",
                        "segmentId": "学段 id",
                        "gradeId": "年级 id",
                        "gradeName": "年级名称",
                        "subjectId": "学科",
                        "eductionalSystem": "学制 （xz01 六三制；xz02 五四制；xz03 高中）",
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
            }
        }
    """
    data = sync_data("schoolSegmenrel")
    return data


def sync_school_segment_grade_rel():
    """
    同步学校学段关系

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "id",
                        "schoolId": "学校 id",
                        "segmentId": "学段 id",
                        "segmentName": "学段名称",
                        "gradeId": "年级 id",
                        "gradeName": "年级名称",
                        "eductionalSystem": "学制 （xz01 六三制；xz02 五四制；xz03 高中）",
                        "syncStatus": "",
                        "createdBy": "创建人 id",
                        "createdDt": "创建时间",
                        "updatedBy": "更新人 id",
                        "updatedDt": "更新时间",
                        "version": "",
                        "customerId": "客户 id",
                        "appId": "应用 id",
                        "remark": "备注",
                        "isDeleted": ""
                    }
                ]
            }
        }
    """
    data = sync_data("schoolGradeRel")
    return data


def sync_teacher_class_rel():
    """
    同步学校学段关系

    :return:\n
        {
            "retCode": "000000",
            "retDesc": "操作成功",
            "data": {
                "isContinue": 1,
                "synBatchId": 101111011,
                "synData": [
                    {
                        "id": "教师学科 id",
                        "teacherId": "教师 id",
                        "classId": "班级 id",
                        "subjectId": "学科 id",
                        "syncStatus": ""
                    }
                ]
            }
        }
    """
    data = sync_data("teacherClassRel")
    return data
