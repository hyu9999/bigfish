from django.db import models

from bigfish.apps.knowledgepoint.models import KnowledgePoint


class Question(models.Model):
    version = models.CharField('版本', max_length=100, default="", blank=True, null=True)
    grade = models.CharField('年级', max_length=100, default="", blank=True, null=True)
    volume = models.CharField('册', max_length=100, default="", blank=True, null=True)
    unit = models.CharField(max_length=100, default="", blank=True, null=True)
    lesson = models.CharField(max_length=100, default="", blank=True, null=True)
    textbook = models.CharField("教材", max_length=100, default="", blank=True, null=True)
    question_type = models.CharField("题目类型", max_length=100, default="", blank=True, null=True)  # 一级分类
    show_type = models.CharField("表现类型", max_length=100, default="", blank=True, null=True)  # 二级分类
    third_type = models.CharField("三级分类", max_length=100, default="", blank=True, null=True)  # 三级分类
    difficulty = models.IntegerField("难度系数")
    name = models.CharField("题型名称", max_length=100, default="", blank=True, null=True)
    desc = models.TextField("答题说明")
    content = models.TextField("题目内容")
    option_type = models.CharField("选项表现类型", max_length=100, default="", blank=True, null=True)
    options = models.TextField("选项", default="", blank=True)
    answer = models.CharField("答案", max_length=500, default="", blank=True, null=True)
    suitable = models.CharField("适用活动", max_length=200, default="", blank=True, null=True)
    purpose = models.CharField("练习目的", max_length=200, default="", blank=True, null=True)
    label = models.CharField("标签", max_length=200, default="", blank=True, null=True)
    is_push = models.BooleanField("是否推送题", default=False)
    knowledge_point = models.ManyToManyField(KnowledgePoint,
                                             related_name="%(app_label)s_%(class)s_knowledge_point",
                                             verbose_name="知识点",
                                             through='QuestionKPRelationship')

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "题目"
        verbose_name_plural = verbose_name


class QuestionKPRelationship(models.Model):
    knowledge_point = models.ForeignKey(KnowledgePoint,
                                        verbose_name="知识点",
                                        on_delete=models.CASCADE,
                                        related_name="%(app_label)s_%(class)s_knowledge_point",
                                        help_text="知识点"
                                        )
    question = models.ForeignKey(Question,
                                 verbose_name="题目",
                                 on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_question",
                                 help_text="题目"
                                 )
    order = models.IntegerField("排序", blank=True, default=0)
    seconds = models.IntegerField("二级排序", blank=True, default=0)
    update_time = models.DateTimeField("修改时间", auto_now=True, help_text="修改时间")
    add_time = models.DateTimeField("添加时间", auto_now_add=True, help_text="添加时间")
    # update_time = models.DateTimeField("修改时间", default=timezone.now, help_text="修改时间")
    # add_time = models.DateTimeField("添加时间",  default=timezone.now, help_text="添加时间")
    is_effect = models.BooleanField("是否有效", default=True, help_text="是否有效")
    is_default = models.BooleanField("是否默认", default=False, help_text="是否默认")
    remark = models.TextField("备注", default="", blank=True, help_text="备注")

    class Meta:
        verbose_name = "题目知识点关系表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.knowledge_point.name
