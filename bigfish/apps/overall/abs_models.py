import jsonfield
from django.db import models


class AbsStdData(models.Model):
    duration_std_val = models.FloatField("使用时长标准值", blank=True, default=0.0)
    """
    1.教学进度(0.2)
    2.平均正确率(0.35)
    3.阶段成绩(0.45)
    标准值=（每个维度单个学生的平均值-每个维度所有学生的的平均值）/每个维度的标准差
    综合值 = 标准值1*权重1 + 标准值2*权重2 + 标准值3*权重3
    """
    teach_progress_std_val = models.FloatField("教学进度标准值", blank=True, default=0.0)
    right_rate_std_val = models.FloatField("正确率标准值", blank=True, default=0.0)
    score_std_val = models.FloatField("成绩标准值", blank=True, default=0.0)
    composite = models.FloatField("总体情况综合值", blank=True, default=0.0)
    """
    1.使用人数(0.2)
    2.使用次数(0.3)
    3.交互次数(0.5)
    标准值=（每个维度单个学生的平均值-每个维度所有学生的的平均值）/每个维度的标准差
    使用效果综合值 = 标准值1*权重1 + 标准值2*权重2 + 标准值3*权重3
    """
    use_num_std_val = models.FloatField("使用人数标准值", blank=True, default=0.0)
    use_times_std_val = models.FloatField("使用次数标准值", blank=True, default=0.0)
    interactive_num_std_val = models.FloatField("交互次数标准值", blank=True, default=0.0)
    as_composite = models.FloatField("应用规模综合值", blank=True, default=0.0)

    """
    1.使用人数比例(0.3)
    2.交互次数(0.3)
    3.活动数量(0.4)
    标准值=（每个维度单个学生的平均值-每个维度所有学生的的平均值）/每个维度的标准差
    使用情况综合值 = 标准值1*权重1 + 标准值2*权重2 + 标准值3*权重3
    """
    use_num_ratio_std_val = models.FloatField("使用人数比例标准值", blank=True, default=0.0)
    activity_num_std_val = models.FloatField("活动数量标准值", blank=True, default=0)
    usage_composite = models.FloatField("使用情况综合值", blank=True, default=0.0)

    class Meta:
        abstract = True


class AbsOverallData(models.Model):
    """
    abs overall data
    """
    center = jsonfield.JSONField("区划中心点", blank=True, null=True, default=[])
    """
    某个xx学生的成绩平均值
    """
    score = models.FloatField("平均成绩", default=0.0)
    """
    某个xx各个学生的正确率平均值
    """
    right_rate = models.FloatField("平均正确率", default=0.0)
    """
    某个xx学生的数量
    """
    student_num = models.IntegerField("学生人数", default=0)
    """
    某个xx使用pad的学生的数量
    """
    student_use_num = models.IntegerField("学生使用人数", default=0)
    student_use_duration = models.FloatField("学生使用时长", default=0.0)
    student_avg_use_duration = models.FloatField("学生平均使用时长", default=0.0)
    """
    某个xx教师的实际数量
    """
    teacher_num = models.IntegerField("教师人数", default=0)
    """
    某个xx使用pad的教师的数量
    """
    teacher_use_num = models.IntegerField("教师使用人数", default=0)
    teacher_use_duration = models.FloatField("教师使用时长", default=0.0)
    teacher_avg_use_duration = models.FloatField("教师平均使用时长", default=0.0)
    push_activity_num = models.IntegerField("发布活动量", default=0)
    """
    某个xx学生的练习题数平均值
    """
    exercise_num = models.IntegerField("平均练习题数", default=0)
    """
    某个xx学生的交互次数平均值
    """
    interactive_num = models.IntegerField("平均交互次数", default=0)
    """
    某个xx学生的交互次数之和
    """
    interactive_total_num = models.IntegerField("交互次数", default=0)
    """
    某个xx教师的教学进度平均值
    """
    teaching_progress = models.FloatField("教学进度", default=0.0)
    """
    某个xx学生的人机对话量平均值 
    """
    man_machine_num = models.IntegerField("人机对话量", default=0)
    """
    使用次数
    """
    task_num = models.IntegerField("任务数", default=0)
    """
    活动数量
    """
    activity_num = models.IntegerField("活动数量", default=0)
    """
    使用次数上限
    """
    task_limit = models.IntegerField("任务数上限", default=0)

    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # create_time = models.DateTimeField("创建时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    # update_time = models.DateTimeField("更新时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))

    class Meta:
        abstract = True


class AbsStageScore(models.Model):
    """
    阶段成绩字段
    """
    # Midterm 期中
    midterm_avg_score = models.FloatField("期中平均成绩", blank=True, default=0.0)
    midterm_max_score = models.FloatField("期中最大成绩", blank=True, default=0.0)
    midterm_min_score = models.FloatField("期中最小成绩", blank=True, default=0.0)
    midterm_lower_quartile = models.FloatField("期中下四分位数", blank=True, default=0.0)
    midterm_median = models.FloatField("期中中位数", blank=True, default=0.0)
    midterm_upper_quartile = models.FloatField("期中上四分位数", blank=True, default=0.0)
    # Final simulation 期末模拟
    fs_avg_score = models.FloatField("期末模拟平均成绩", blank=True, default=0.0)
    fs_max_score = models.FloatField("期末模拟最大成绩", blank=True, default=0.0)
    fs_min_score = models.FloatField("期末模拟最小成绩", blank=True, default=0.0)
    fs_lower_quartile = models.FloatField("期末模拟下四分位数", blank=True, default=0.0)
    fs_median = models.FloatField("期末模拟中位数", blank=True, default=0.0)
    fs_upper_quartile = models.FloatField("期末模拟上四分位数", blank=True, default=0.0)
    # Final examination 期末统考
    fe_avg_score = models.FloatField("期末统考平均成绩", blank=True, default=0.0)
    fe_max_score = models.FloatField("期末统考最大成绩", blank=True, default=0.0)
    fe_min_score = models.FloatField("期末统考最小成绩", blank=True, default=0.0)
    fe_lower_quartile = models.FloatField("期末统考下四分位数", blank=True, default=0.0)
    fe_median = models.FloatField("期末统考中位数", blank=True, default=0.0)
    fe_upper_quartile = models.FloatField("期末统考上四分位数", blank=True, default=0.0)

    class Meta:
        abstract = True
