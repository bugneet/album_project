import datetime
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from .models import Photo


def upload_photo(request):
    if request.method == 'POST':
        if not request.csrf_token.is_valid:
            return HttpResponseForbidden('CSRF token missing or incorrect.')

        title = request.POST['title']
        description = request.POST['description']

        photo = request.FILES['photo']

        if photo.content_type not in ['image/jpeg', 'image/png']:
            return HttpResponseBadRequest('허용된 파일 형식이 아닙니다.')

        if not photo.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return HttpResponseBadRequest('허용된 파일 확장자가 아닙니다.')

        photo_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        photo_path = os.path.join(settings.MEDIA_ROOT, photo_name)

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

        return redirect('analysis-results.html')

    return render(request, 'upload.html')
