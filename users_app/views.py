import datetime
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from .models import Photo
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login

BASE_DIR = settings.BASE_DIR

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

        return redirect('analysis_results_view')

    return render(request, 'upload.html')


def analysis_results_view(request):
    return render(request, 'analysis_results.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  
            return redirect('index.html')  
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('index.html')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
