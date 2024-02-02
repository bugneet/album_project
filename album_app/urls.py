from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('', views.index, name='index'),
    path('mypage_album/', views.mypage_album, name='mypage_album'),
    path('mypage_mypost/', views.mypage_mypost, name='mypage_mypost'),
    path('mypage_myreply/', views.mypage_myreply, name='mypage_myreply'),
    path("mixin/mypage_album/", PhotoTableAPIMixins.as_view()),
    path("mixin/board/", BoardAPIMixins.as_view()),
    # path("mixin/reply/", ReplyAPIMixins.as_view()),
    path("mypage_album/tag_search/<str:keyword>", TagSearch.as_view()),
    path("mypost/", MyPost.as_view()),
    path("myreply/", MyReply.as_view()),
    path('classification/', views.classification, name='classification'),
    path("myreplydel/<str:rno>/", MyReplyDel.as_view()),
    path("myliked/", MyLiked.as_view()),
    path("myreplydel/<str:likeno>/", MyLikedDel.as_view()),
    path("mixin/liked/", LikedAPIMixins.as_view()),    
    path('upload/', upload_photo, name='upload-photo'),
    path( '', views.index, name='index'),
    # path('exhibition/', views.exhibition, name='exhibition'),
    path('exhibition/', ExhibitionAPI.as_view()),
    path('current_user/', CurrentUserView.as_view()),
    path('board_writing/', BoardWritingView.as_view()),
    path('photos/<int:user_id>/', PhotoListView.as_view()),
    path('boards/', BoardAPIMixins.as_view()),
    path('board/<str:board_no>/', BoardAPIMixins.as_view()),    
    path('chart_db/', tag_chart),
    # path('personal_chart/<int:login_id>',personal_chart)
    path('personal_chart/<str:username>/',personal_chart),
    path('personal_chart_yearly/<str:username>/',personal_chart_yearly),
    path('tag_chart_yearly/', tag_chart_yearly),
    path('tag_count_yearly_chart/', tag_count_yearly_chart),
    path('custom_tags_count_yearly_chart/', custom_tags_count_yearly_chart),
    

    
]

