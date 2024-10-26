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
        fields = ['id', 'email', 'password', 'name', 'gender', 'birthday', 'phone_number', 'room_capacity', 'nickname']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'email': {'required': True}, # 이메일 필수
            'gender': {'required': True}, # 성별 필수
        }
    
    def validate_email(self, value):
        # 이메일 형식이 맞는지 확인
        EmailValidator()(value)
        return value
    
    def check_duplicate(self, email, instance = None):
        # 중복 검사
        if get_user_model().objects.exclude(pk = instance.pk if instance else None).filter(email = email).exists():
            raise serializers.ValidationError("This email is already in use.")
    
    def create(self, validated_data):
        # 유효성과 중복성 검사
        email = validated_data.get('email')
        self.check_duplicate(email)

        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        # 현재 인스턴스의 이메일 및 학번 저장
        email = validated_data.get('email', instance.email)

        # 중복 검사
        self.check_duplicate(email, instance)

        # 이메일 및 학번 수정
        instance.email = email

        # 비밀번호 처리
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style = {'input_type': 'password'},
        trim_whitespace = False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request = self.context.get('request'),
            username = email,
            password = password,
        )
        if not user or user.email != email:
            msg = _('Unable to authenticate with provide credentials')
            raise serializers.ValidationError(msg, code = 'authorization')

        attrs['user'] = user
        return attrs