from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bigfish.apps.users.models import UserChangeReport, UserReg, UserOnline, UserWordHero, UserKlassRelationship, \
    UserCourse, UserPosition, UserScenariosReport, BigFishSession
from bigfish.apps.users.models import UserFeedback, UserUsedInfo
from bigfish.utils.functions import generate_fields, format_admin_list

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from bigfish.base.adpter import get_adapter
    from allauth.account.utils import setup_user_email
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册ID
    """

    class Meta:
        model = UserReg
        fields = generate_fields(UserReg)


class UserOnlineSerializer(serializers.ModelSerializer):
    """
    用户在线情况
    """

    class Meta:
        model = UserOnline
        fields = generate_fields(UserOnline)


class UserCourseSerializer(serializers.ModelSerializer):
    klass = serializers.SerializerMethodField()

    @staticmethod
    def get_klass(obj):
        try:
            klass = UserKlassRelationship.objects.get(user=obj.user, is_effect=True, is_default=True).klass.id
        except Exception as e:
            klass = 0
        return klass

    class Meta:
        model = UserCourse
        fields = ('klass', 'textbook', 'unit', 'lesson')


class UserSerializer(serializers.ModelSerializer):
    """
    用户
    """
    reg = UserRegSerializer()
    course = UserCourseSerializer(read_only=True)

    def create(self, validated_data):
        with transaction.atomic():
            reg_data = validated_data.pop('reg', None)
            user = super(UserSerializer, self).create(validated_data)
            user.set_password(validated_data['password'])
            user.save()
            reg_data['user'] = user
            self.update_or_create_reg(user, reg_data)
            return user

    def update(self, instance, validated_data):
        reg_data = validated_data.pop('reg', None)
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        self.update_or_create_reg(instance, reg_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def update_or_create_reg(self, user, reg_data):
        if reg_data:
            UserReg.objects.update_or_create(user=user, defaults=reg_data)

    class Meta:
        model = get_user_model()
        fields = generate_fields(get_user_model(), add=['reg', 'course'],
                                 remove=['user_permissions', 'date_joined', 'groups'])


class MinUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'realname', 'nickname', 'icon')


class AuthUserSerializer(serializers.ModelSerializer):
    """
    用户
    """
    klass_id = serializers.SerializerMethodField()
    klass_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    auto_remember_pwd = serializers.SerializerMethodField()

    @staticmethod
    def get_klass_id(obj):
        try:
            default_class = UserKlassRelationship.objects.get(user=obj, is_effect=True, is_default=True)
        except Exception as e:
            klass_id = 0
        else:
            klass_id = default_class.klass_id
        return klass_id

    @staticmethod
    def get_klass_name(obj):
        try:
            default_class = UserKlassRelationship.objects.get(user=obj, is_effect=True, is_default=True)
        except Exception as e:
            klass_name = ''
        else:
            klass_name = "{}{}{}".format(default_class.klass.school.title, default_class.klass.get_grade_display(),
                                         default_class.klass.title)
        return klass_name

    @staticmethod
    def get_school_name(obj):
        try:
            default_class = UserKlassRelationship.objects.get(user=obj, is_effect=True, is_default=True)
        except Exception as e:
            school_name = ''
        else:
            school_name = default_class.klass.school.title
        return school_name

    @staticmethod
    def get_auto_remember_pwd(obj):
        try:
            data = obj.school.auto_remember_pwd
        except Exception as e:
            data = False
        return data

    class Meta:
        model = get_user_model()
        fields = format_admin_list(get_user_model(),
                                   add=["school_name", "klass_id", 'klass_name', 'control_area', 'auto_remember_pwd'],
                                   remove=['user_permissions', 'date_joined', 'groups', 'password', 'last_login',
                                           'is_superuser', 'first_name', 'last_name', 'email', 'is_staff', 'is_active'])


class UserKlassRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKlassRelationship
        fields = '__all__'


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = '__all__'


class UserUsedInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUsedInfo
        fields = '__all__'


class UserChangeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChangeReport
        fields = '__all__'


class UserWordHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWordHero
        fields = '__all__'


class UserPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPosition
        fields = '__all__'


class UserScenariosRopSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserScenariosReport
        fields = '__all__'


class SNRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    realname = serializers.CharField(max_length=40)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'realname': self.validated_data.get('realname', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        user.realname = self.cleaned_data.get("realname")
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class BigFishSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigFishSession
        fields = '__all__'
