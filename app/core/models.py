"""
Database models
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user
    
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self.db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length = 255, unique=True)
    name = models.CharField(max_length = 255)
    student_id = models.IntegerField(
        unique = True,
        validators = [MinValueValidator(100000000), MaxValueValidator(999999999)], # 9자리 숫자로 제한
        null = False, # 필수 항목
    )
    description = models.CharField(max_length = 255, default="", blank = True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 추가적인 프로필 정보
    gender = models.CharField(max_length = 10, choices = [('male', 'Male'), ('female', 'Female')], blank = False)
    age = models.PositiveIntegerField(null = True, blank = True)
    grade = models.CharField(max_length = 10, blank = True)
    major = models.CharField(max_length = 100, blank = True)

    objects = UserManager()

    USERNAME_FIELD = 'student_id' # 학번을 사용자 인증 필드로 사용
    REQUIRED_FIELDS = ['name', 'email'] # 회원 가입 시 필수 입력 필드

class Answer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    answer = models.JSONField(default = dict) # 유저의 응답을 딕셔너리로 저장

    def __str__(self):
        return f"User: {self.user.email}, Answer: {self.answer}"

# 룸메이트 신청 모델
class Match(models.Model):
    # 요청한 사람
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'sent_requests',
        on_delete = models.CASCADE,
    )
    # 요청을 받은 사람
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'received_requests',
        on_delete = models.CASCADE,
    )
    # 요청 상태
    status = models.CharField(max_length = 10, choices = [
        ('pending', 'Pending'), # 대기 상태
        ('accepted', 'Accepted'), # 수락 상태
        ('rejected', 'Rejected'), # 거부 상태
    ], default = 'pending')
    # 요청 일시
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        # 동일한 사용자에게 중복 신청 방지
        unique_together = ('requester', 'recipient')

# 매칭 그룹과 관련된 모델
class Group(models.Model):
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add = True)

# 매칭 결과를 받아오는 모델
class Result(models.Model):
    user = models.ForeignKey( # 사용자
        settings.AUTH_USER_MODEL,
        related_name = 'match_results', # 이 유저의 매칭 결과를 조회
        on_delete = models.CASCADE,
    )
    matched_user = models.ForeignKey( # AI가 매칭한 다른 사용자
        settings.AUTH_USER_MODEL,
        related_name = 'matched_results', # 이 유저와 매칭된 결과를 조회
        on_delete = models.CASCADE,
    )
    compatibility_score = models.FloatField() # AI가 계산한 적합성 점수
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.email} matched with {self.matched_user.email} - Score: {self.compatibility_score}"