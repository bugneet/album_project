from django.urls import path
from . import views
from .views import PhotoTableAPIMixins, BoardAPIMixins, ReplyAPIMixins,LikedAPIMixins, TagSearch, MyPost, MyReply, MyReplyDel, MyLiked, MyLikedDel

urlpatterns = [
    path('', views.index, name='index'),
    path('mypage_album/', views.mypage_album, name='mypage_album'),
    path('mypage_mypost/', views.mypage_mypost, name='mypage_mypost'),
    path('mypage_myreply/', views.mypage_myreply, name='mypage_myreply'),
    path("mixin/mypage_album/", PhotoTableAPIMixins.as_view()),
    path("mixin/board/", BoardAPIMixins.as_view()),
    path("mixin/reply/", ReplyAPIMixins.as_view()),
    path("mypage_album/tag_search/<str:keyword>", TagSearch.as_view()),
    path("mypost/", MyPost.as_view()),
    path("myreply/", MyReply.as_view()),
    path('classification/', views.classification, name='classification'),
    path("myreplydel/<str:rno>/", MyReplyDel.as_view()),
    path("myliked/", MyLiked.as_view()),
    path("myreplydel/<str:likeno>/", MyLikedDel.as_view()),
    path("mixin/liked/", LikedAPIMixins.as_view()),
    

]
