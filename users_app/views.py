from django.shortcuts import render
from .models import User
from rest_framework import generics, status
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from datetime import datetime
from .models import PhotoTable, Board, Reply, Photo
import os
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

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

def upload_photo(request):
    if request.method == 'POST':
        if not request.POST.get('csrfmiddlewaretoken'):
            return HttpResponseForbidden('CSRF token missing or incorrect.')

        title = request.POST['title']
        description = request.POST['description']
        photo = request.FILES['photo']

        if photo.content_type not in ['image/jpeg', 'image/png']:
            return HttpResponseBadRequest('허용된 파일 형식이 아닙니다.')

        if not photo.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return HttpResponseBadRequest('허용된 파일 확장자가 아닙니다.')

        photo_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        photo_path = os.path.join('Upload', f'{photo_name}.jpg')  

        with open(photo_path, 'wb') as f:
            f.write(photo.read())

        try:
            photo = Photo.objects.create(
                title=title,
                description=description,
                image=photo_path,
            )
        except ValidationError as e:
            return HttpResponseBadRequest(e.messages)

        return redirect('classfication.html')

    return render(request, 'upload.html')        

def analysis_results_view(request):
    return render(request, 'classfication.html')    