from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/mypage_album', views.mypage_album, name='mypage_album'),
]
