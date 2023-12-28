from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'album_app/index.html')

def mypage_album(request):
    return render(request, 'album_app/mypage_album.html')
