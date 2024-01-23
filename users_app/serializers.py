from .models import User  # User 모델
# Django의 기본 패스워드 검증 
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.authtoken.models import Token  
# 이메일 중복 방지
from rest_framework.validators import UniqueValidator  


# 회원가입 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        help_text="아이디(Unique)",
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="이미 존재하는 아이디입니다.")],
    )
    password = serializers.CharField(
        help_text="비밀번호",
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        help_text = "비밀번호 재입력", write_only=True, required=True,)

    class Meta:
        model = User
        # fields = ('username', 'password', 'password2', 'email', 'user_name', 'user_phone','user_address')
        fields = ('username', 'password', 'password2', 'email', 'user_name','user_address')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "비밀번호 확인이 일치하지 않습니다"})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            user_name = validated_data['user_name'],
           # user_phone = validated_data['user_phone'],
            user_address = validated_data['user_address'],
        )

        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user

# 로그인 시리얼라이저
# 검증 과정 처리 후 토큰 반환
class LoginSerializer(serializers.Serializer):
    print("LoginSerializer 로그인")
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {"error": "아이디 또는 비밀번호가 잘못되었습니다"})

