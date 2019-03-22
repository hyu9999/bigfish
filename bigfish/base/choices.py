# ===============================================BASIC
# 操作
OPERATE_CHOICE = (
    (1, '添加'),
    (2, '替换'),
    (3, '删除')
)
# ===============================================活动
# 一级分类
FIRST_TYPE_CHOICE = (
    (1, "练习活动"),
    (2, "学习活动"),
)
# 二级分类
SECOND_TYPE_CHOICE = (
    (1, "学习练习"),
    (2, "复习巩固"),
)
# 活动展示类型
ACT_DISPLAY_CHOICES = (
    (1, "播放视频"),
    (2, "课文跟读"),
    (3, "课文朗读"),
    (4, "角色扮演"),
    (5, "练习题"),
    (6, "词汇学习"),
    (7, "人际活动-无游戏"),
    (8, "人际活动-画画"),
    (9, "人际活动-拼图"),
    (10, "人际活动-装扮"),
    (11, "人际活动-转盘"),
    (12, "人际活动-黑板")
)
# ===============================================成就
# 成就功能类型
FUNCTION_CHOICE = (
    (1, '普通成就'),
    (2, '多条件成就'),
    (3, '关联成就'),
)
# 成就描述类型
DESC_CHOICE = (
    (1, '学习成就'),
    (2, '练习成就'),
    (3, '娱乐成就'),
)
# 成就获取状态
ACHIEVE_STATUS_CHOICE = (
    (1, '未开始'),
    (2, '进行中'),
    (3, '已获取'),
)
# =============================================日期
# 星期
WEEK_CHOICE = (
    (1, "星期一"),
    (2, "星期二"),
    (3, "星期三"),
    (4, "星期四"),
    (5, "星期五"),
    (6, "星期六"),
    (7, "星期日"),
)
# =============================================学校
# 学期
TERM_CHOICE = (
    (1, 'A'),
    (2, 'B'),
)
# 班级
GRADE_CHOICE = (
    (11, "小学一年级"),
    (12, "小学二年级"),
    (13, "小学三年级"),
    (14, "小学四年级"),
    (15, "小学五年级"),
    (16, "小学六年级"),
    (21, "初中一年级"),
    (22, "初中二年级"),
    (23, "初中三年级"),
    (31, "高中一年级"),
    (32, "高中二年级"),
    (33, "高中三年级")
)
# 课程表
SCHEDULE_CHOICE = (
    (0, "早读"),
    (1, "第一节"),
    (2, "第二节"),
    (3, "第三节"),
    (4, "第四节"),
    (5, "第五节"),
    (6, "第六节"),
    (7, "第七节"),
    (8, "第八节"),
    (9, "晚自习"),
    (10, "晚自习1"),
    (11, "晚自习2"),
)
# 学制
LENGTH_SCHOOLING_CHOICE = (
    (1, "六三制"),
    (2, "五四制"),
)
# =============================================题目
# 题目类型
QUESTION_TYPE_CHOICE = (
    (1, "单选"),
    (2, "选词填空"),
    (3, "套用练习"),
    (4, "词图匹配"),
)

VERSUS_QUESTION_TYPE_CHOICE = (
    (1, '听音选图'),
    (2, '看图选词'),
    (3, '英译中'),
)
# 推送类型
PUSH_TYPE_CHOICE = (
    (1, "错题综合复习"),
    (2, "课堂知识巩固"),
    (3, "个性化推荐作业"),
    (4, "巩固性推荐作业"),
    (5, "手动组建作业"),
)
# 答案
RESULT_CHOICE = (
    (0, '错'),
    (1, '对'),
    (2, '未答'),
)
# 考察类型
REVIEW_TYPE_CHOICE = (
    (1, "话题"),
    (2, "词汇"),
    (3, "句型"),
    (4, "功能"),
    (5, "语音"),
)
# 成绩类型
SCORE_TYPE = (
    (1, "期中"),
    (2, "期末模拟"),
    (3, "期末统考"),
)
# =============================================用户
# 角色
IDENTITY_CHOICE = (
    (1, "老师"),
    (2, "学生"),
    (3, "录题员"),
    (4, "用户管理员"),
    (5, "管理员"),
    (6, "数据员"),
    (7, "家长"),
    (8, "教研员"),
    (9, "教育行政人员")
)
AUTH_STATUS_CHOICE = (
    (0, "未认证"),
    (1, "已认证"),
    (2, "认证未通过"),
    (3, "认证中"),
)
# 性别
SEX_CHOICE = (
    (1, "男"),
    (2, "女")
)
# 级别
LEVEL_CHOICE = (
    (1, 'Good'),
    (2, 'Bad')
)

# 教学模式
TEACHING_MODE_CHOICE = (
    (1, "互动型"),  # 在线时间<15min
    (2, "练习型"),  # 在线时间>=15min
)
# 课型
LESSON_TYPE_CHOICE = (
    (1, "新课"),
    (2, "旧课"),
    (3, "新旧交替"),
)
# 教师类型
TEACHER_TYPE_CHOICE = (
    (1, "专业教师"),
    (2, "非专业教师"),
)
# 学生上课状态
ONLINE_STATUS_CHOICE = (
    (0, "unknown"),
    (1, "设备异常"),
    (2, "请假"),
)

STUDENT_REL_CHOICE = (
    (1, "父亲"),
    (2, "母亲"),
    (3, "家人"),

)
ACCOUNT_SOURCE_CHOICE = (
    (0, "其他"),
    (1, "树鱼"),
    (2, "恒峰"),
)
# =============================================对战
# 对战用户类型
USER_TYPE_CHOICE = (
    (0, '发起者'),
    (1, '接受者'),
    (2, '机器人'),
)

# =============================================错题本
# 掌握程度
MASTER_LEVEL = (
    (1, "未掌握"),
    (2, "初级掌握"),
    (3, "基本掌握"),
    (4, "完全掌握"),
    (5, "完美记忆"),
    (6, "已掌握"),
)
# 数据来源
DATA_SOURCE = (
    (1, "综合复习"),
    (2, "课堂知识巩固"),
    (3, "个性化推荐作业"),  # 目前作业数据来源全存为3，
    (4, "巩固性推荐作业"),
    (5, "手动组建作业"),
    (6, "自主学习"),
    (7, "课堂任务"),  # 任务中的练习活动
)
# =============================================希沃
# 绑定状态
BIND_STATUS = (
    (1, "未绑定"),
    (2, "已绑定"),
    (3, "已过期"),
)
# =============================================语音
# 语音评测类型
EVALUATION_TYPE = (
    (1, "英文单词评测"),
    (2, "英文句子评测"),
    (3, "英文段落朗读评测"),
    (4, "英文单项选择题评测"),
    (5, "扩展选择题"),
    (6, "句子选读题型评测"),
    (7, "半开放题与开放题"),
    (8, "英文问答题评测"),
    (9, "英文看图作文评测"),
    (10, "故事复述评测"),
    (11, "音标评测题"),
    (12, "自有识别题"),
)
EVALUATION_TYPE_EN = (
    (1, "en.word.score"),
    (2, "en.sent.score"),
    (3, "en.pred.score"),
    (4, "en.choc.score"),
    (5, "en.pche.score"),
    (6, "en.pcha.score"),
    (7, ""),
    (8, "en.pqan.score"),
    (9, "en.pict.score"),
    (10, "en.retell.score"),
    (11, "en.alpha.score"),
    (12, "en.sent.rec"),
)
# 语音识别引擎类型
ENGINE_TYPE = (
    (1, 'sms-en8k'),  # 英语
    (2, 'sms-en16k'),  # 英语
    (3, 'sms8k'),  # 普通话
    (4, 'sms16k'),  # 普通话
)
# ==============================知识点
PART_OF_SPEECH = (
    (0, "unknown"),
    (1, "art."),
    (2, "abbr."),
    (3, "n."),
    (4, "adv."),
    (5, "adj."),
    (6, "aux.v."),
    (7, "v."),
    (8, "prep."),
    (9, "excl."),
    (10, "pron."),
    (11, "n.(pl.)"),
    (12, "词组"),

)
# ==============================文章
ARTICLE_CLASSIFY = (
    (1, "课文"),
    (2, "微语篇"),
)
# ==============================课堂
# 拖堂情况
DELAY_STATUS = (
    (0, "正常"),
    (1, "拖堂"),
    (2, "早退"),
)

BEHAVIOR_TYPE = (
    (0, "未知"),
    (1, "活动"),
    (2, "黑屏"),
    (3, "课堂"),
    (4, "对战"),
    (5, "课堂知识巩固"),
    (6, "游戏"),
)