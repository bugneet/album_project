from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from .models import Photo


def upload_photo(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        photo = request.FILES['photo']
        photo_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        photo_path = os.path.join(BASE_DIR, 'media', photo_name)
        if photo.content_type not in ['image/jpeg', 'image/png']:
            return HttpResponseBadRequest('허용된 파일 형식이 아닙니다.')
        with open(photo_path, 'wb') as f:
            f.write(photo.read())
        photo = Photo(
            title=title,
            description=description,
            image=photo_path,
        )
        photo.full_clean()
        photo.save()

        return redirect('analysis-results')

    return render(request, 'upload.html')
