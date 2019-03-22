from django.core import validators
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from bigfish.apps.areas.models import Area
from bigfish.apps.schools.models import Klass, School, Term, TermWeek, SchoolTerm, SchoolWeek, KlassProgress, \
    ClassSchedule, KlassActProgress, RegisterSerial
from bigfish.apps.users.models import BigfishUser
from bigfish.utils.functions import generate_fields


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'


class TermWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermWeek
        fields = '__all__'


class SchoolTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolTerm
        fields = '__all__'


class SchoolWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolWeek
        fields = '__all__'


class SchoolSerializer(serializers.ModelSerializer):
    counts = serializers.SerializerMethodField()
    area_name = serializers.SerializerMethodField()

    def get_counts(self, obj):
        teacher_count = BigfishUser.objects.filter(attend_class__school=obj, identity="老师").count()
        student_count = BigfishUser.objects.filter(attend_class__school=obj, identity="学生").count()
        class_count = Klass.objects.filter(school=obj).count()

        return {
            "teacher_count": teacher_count,
            "student_count": student_count,
            "class_count": class_count
        }

    def get_area_name(self, obj):
        if obj.areas and obj.areas.level == 'district':
            try:
                province = Area.objects.get(adcode=obj.areas.provCode).name
            except Exception as e:
                province = ""

            try:
                city = Area.objects.get(adcode=obj.areas.cityCode).name
            except Exception as e:
                city = ""
            area_name = "{}{}{}".format(province, city, obj.areas.name)
        else:
            area_name = obj.areas.__str__()
        return area_name

    def validate_school_type(self, school_type):
        types = school_type.split(",")
        if len(types) > 3:
            raise serializers.ValidationError("标签最多只能选中三个")
        if not set(types) <= {"高中", "初中", "小学"}:
            raise serializers.ValidationError("标签只能在高中，初中，小学选择")
        return ",".join(list(set(types)))

    class Meta:
        model = School
        fields = generate_fields(School, add=["id", "counts", "area_name"])


class KlassSerializer(serializers.ModelSerializer):
    school_data = serializers.SerializerMethodField()
    teachers_data = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()

    class_name_validate = validators.RegexValidator(regex="^[\d\u4E00-\u9FA5]+\Z", message="班级只能输入汉字和数字")

    name = serializers.CharField(max_length=30, validators=[class_name_validate])

    def get_student_count(self, obj):
        return BigfishUser.objects.filter(attend_class=obj, identity="学生").count()

    def get_school_data(self, obj):
        return SchoolSerializer(obj.school).data

    def get_teachers_data(self, obj):
        result = []
        for teacher in obj.person.filter(identity="老师"):
            result.append({
                "id": teacher.user.id,
                "nickname": teacher.nickname,
                "username": teacher.user.username
            })
        return result

    def get_teachers(self, obj):
        result = list(obj.person.filter(identity="老师").values_list('pk', flat=True))
        return result

    class Meta:
        model = Klass
        fields = generate_fields(Klass, add=["id", "school_data", "teachers_data", "teachers", "student_count"])

    validators = [
        UniqueTogetherValidator(
            queryset=Klass.objects.all(),
            fields=('school', 'grade', 'name'),
            message="名称已经存在"
        )]


class KlassBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Klass
        fields = '__all__'


class KlassProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = KlassProgress
        fields = '__all__'


class KlassActProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = KlassActProgress
        fields = '__all__'


class KlassActProgressMinSerializer(serializers.ModelSerializer):
    act_tab_name = serializers.SerializerMethodField()
    act_name = serializers.SerializerMethodField()

    @staticmethod
    def get_act_tab_name(obj):
        try:
            data = obj.act_tab.title
        except Exception as e:
            data = ""
        return data

    @staticmethod
    def get_act_name(obj):
        try:
            data = obj.activity.title
        except Exception as e:
            data = ""
        return data

    class Meta:
        model = KlassActProgress
        fields = (
            'id', 'act_tab_id', 'act_tab_name', 'activity_id', 'act_name', 'time_duration', 'suggested_time',
            'is_finish')


class TeacherCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KlassProgress
        fields = ('klass', 'textbook', 'unit', 'lesson')


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = '__all__'


class RegisterSerialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterSerial
        fields = '__all__'
