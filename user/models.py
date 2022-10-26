import uuid as uuid_lib
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, _user_has_perm
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, request_data, **kwargs):
        now = timezone.now()
        if not request_data['email']:
            raise ValueError('Users must have an email address.')

        profile = ""
        if request_data.get('profile'):
            profile = request_data['profile']

        user = self.model(
            username=request_data['username'],
            email=self.normalize_email(request_data['email']),
            is_active=True,
            last_login=now,
            date_joined=now,
            profile=profile
        )

        user.set_password(request_data['password'])
        user.save(using=self._db)
        return user

    def create_liver(self, request_data, **kwargs):
        now = timezone.now()
        if not request_data['email']:
            raise ValueError('Users must have an email address.')

        profile = ""
        if request_data.get('profile'):
            profile = request_data['profile']

        user = self.model(
            username=request_data['username'],
            email=self.normalize_email(request_data['email']),
            birthday=request_data['birthday'],
            hobby=request_data['hobby'],
            genre=request_data['genre'],
            message=request_data['message'],
            line_id=request_data['line_id'],
            is_staff=False,
            is_liver=True,
            is_active=True,
            last_login=now,
            date_joined=now,
            profile=profile
        )
        user.set_password(request_data['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        request_data = {
            'username': username,
            'email': email,
            'password': password
        }
        user = self.create_user(request_data)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


def get_check_list_default():
    check_list_default = [{
        "ツイート分析機能": False
    }]
    return check_list_default


class User(AbstractBaseUser):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False, unique=True)
    username = models.CharField(_('username'), max_length=30, null=True, blank=True)
    email = models.EmailField(verbose_name='メールアドレス', max_length=255, unique=True)
    profile = models.CharField(_('profile'), max_length=255, null=True, blank=True)
    introduction = models.CharField(_('introduction'), max_length=255, null=True, blank=True)
    avatar = models.ImageField(_('avatar'), null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False, null=True, blank=True)
    is_admin = models.BooleanField(default=False, null=True, blank=True)
    slack_id = models.CharField(_('slack_id'), max_length=30, null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now, null=True, blank=True)
    birthday = models.DateTimeField(_('birthday'), default=timezone.now, null=True, blank=True)
    hobby = models.JSONField(default=dict, null=True, blank=True)
    genre = models.CharField(max_length=100, default="", null=True, blank=True)
    message = models.TextField(default="", null=True, blank=True)
    line_id = models.CharField(max_length=20, default="", null=True, blank=True)
    is_liver = models.BooleanField(default=False, null=True, blank=True)
    rank = models.CharField(max_length=20, default="", null=True, blank=True)
    image_1 = models.ImageField(_('image_1'), upload_to='livers/', null=True, blank=True)
    image_2 = models.ImageField(_('image_2'), upload_to='livers/', null=True, blank=True)
    image_3 = models.ImageField(_('image_3'), upload_to='livers/', null=True, blank=True)
    start_live_date = models.DateTimeField(_('start_live_date'), default=timezone.now, null=True, blank=True)
    responsible_manager = models.CharField(verbose_name='担当マネ', max_length=50, default="", null=True, blank=True)
    liver_kinds = models.CharField(verbose_name='ライバー種別', max_length=20, default="", null=True, blank=True)
    profession = models.CharField(verbose_name='職業', max_length=30, default="", null=True, blank=True)
    prefecture = models.CharField(verbose_name='都道府県', max_length=5, default="", null=True, blank=True)
    is_sent_dm_type = models.CharField(verbose_name='DM手動/自動', max_length=5, default="", null=True, blank=True)
    live_app = models.CharField(verbose_name='配信アプリ', max_length=30, default="", null=True, blank=True)
    referral = models.CharField(verbose_name='経路', max_length=30, default="", null=True, blank=True)
    liver_id = models.CharField(verbose_name='ライバーID', max_length=30, default="", null=True, blank=True)
    real_name = models.CharField(verbose_name='本名', max_length=30, default="", null=True, blank=True)
    sex = models.CharField(verbose_name='性別', max_length=5, default="", null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def user_has_perm(self, perm, obj):
        return _user_has_perm(self, perm, obj)

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    class Meta:
        db_table = 'user'
        swappable = 'AUTH_USER_MODEL'
