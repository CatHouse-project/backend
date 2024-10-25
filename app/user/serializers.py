"""
Serializers for the user API View
"""
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators = [EmailValidator()])

    class Meta:
        model = get_user_model()
        fields = ['id', 'student_id', 'email', 'password', 'name', 'gender', 'age', 'major', 'grade', 'description']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'email': {'required': True}, # 이메일 필수
            'student_id': {'required': True}, # 학번 필수
            'gender': {'required': True}, # 성별 필수
            'age': {'required': False}, # 나이 선택
            'grade': {'required': False}, # 학년 선택
            'major': {'required': False}, # 전공 선택
        }
    
    def validate_email(self, value):
        # 이메일 형식이 맞는지 확인
        EmailValidator()(value)
        return value
    
    def check_duplicate(self, student_id, email, instance = None):
        # 중복 검사
        if get_user_model().objects.exclude(pk = instance.pk if instance else None).filter(email = email).exists():
            raise serializers.ValidationError("This email is already in use.")
        if get_user_model().objects.exclude(pk = instance.pk if instance else None).filter(student_id = student_id).exists():
            raise serializers.ValidationError("This student ID is already in use.")
    
    def create(self, validated_data):
        # 유효성과 중복성 검사
        student_id = validated_data.get('student_id')
        email = validated_data.get('email')
        self.check_duplicate(student_id, email)

        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        # 현재 인스턴스의 이메일 및 학번 저장
        email = validated_data.get('email', instance.email)
        student_id = validated_data.get('student_id', instance.student_id)

        # 중복 검사
        self.check_duplicate(student_id, email, instance)

        # 이메일 및 학번 수정
        instance.email = email
        instance.student_id = student_id

        # 비밀번호 처리
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    email = serializers.EmailField()
    password = serializers.CharField(
        style = {'input_type': 'password'},
        trim_whitespace = False
    )

    def validate(self, attrs):
        student_id = attrs.get('student_id')
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request = self.context.get('request'),
            username = student_id, # email -> student_id로 변경
            password = password,
        )
        if not user or user.student_id != student_id:
            msg = _('Unable to authenticate with provide credentials')
            raise serializers.ValidationError(msg, code = 'authorization')

        attrs['user'] = user
        return attrs