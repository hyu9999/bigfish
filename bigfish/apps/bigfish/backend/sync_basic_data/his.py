from bigfish.apps.bigfish.backend.sync_basic_data.utils import sync_data
from bigfish.utils.django.config_settings import config_django

config_django()


# =======================================关系表
def sync_class_his():
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
                        "id": "主键 id",
                        "classId": "班级 id",
                        "schoolId": "学校 id",
                        "schoolName": "学校",
                        "className": "班级名称",
                        "classTypeCode": "班级类型 zxxbjlx",
                        "lengthSchooling": "学制类型：1-六三制；2-五四制",
                        "gradeId": "所属年级 id",
                        "gradeName": "所属年级名称",
                        "segmentId": "所属学段 id",
                        "segmentName": "所属学段名称",
                        "entranceSchoolYear": "入学年份",
                        "graduatedSchoolYear": "毕业年份",
                        "classMasterTeacherId": "班主任 id",
                        "classMasterTeacherName": "班主任姓名",
                        "classMasterUserId": "班主任用户 id",
                        "classImg": "",
                        "sortNo": "排序",
                        "isGraduated": "是否毕业",
                        "schoolYear": "学年",
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
    data = sync_data("classHis")
    return data


def sync_student_class_his():
    """
    学生班级变动历史

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
                        "studentId": "学生 id",
                        "classId": "班级 id",
                        "schoolOrgId": "所属学校 id",
                        "year": "学年",
                        "semester": "学期",
                        "isChange": "是否异动（0-否；1-是）",
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
    data = sync_data("studenclassHis")
    return data


if __name__ == '__main__':
    dd = sync_student_class_his()
    print(dd)
