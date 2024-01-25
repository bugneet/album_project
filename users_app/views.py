from django.shortcuts import render
from .models import User
from rest_framework import generics, status
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.response import Response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# 시리얼라이저를 통과하여 받아온 토큰 반환
class LoginView(generics.GenericAPIView):
    print("views 로그인")
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data
        return Response({"token": token.key}, status=status.HTTP_200_OK)