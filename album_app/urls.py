from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('', views.index, name='index'),
    path('mypage_album/', views.mypage_album, name='mypage_album'),
    path('mypage_mypost/', views.mypage_mypost, name='mypage_mypost'),
    path('mypage_myreply/', views.mypage_myreply, name='mypage_myreply'),
    path("mixin/mypage_album/<str:username>/", PhotoTableAPIMixins.as_view()),
    path("mixin/board/", BoardAPIMixins.as_view()),
    # path("mixin/reply/", ReplyAPIMixins.as_view()),
    path("mypage_album/tag_search/<str:keyword>", TagSearch.as_view()),
    path("mypost/<str:username>/", MyPost.as_view()),
    path("myreply/<str:username>/", MyReply.as_view()),
    path('classification/', Classification.as_view()),
    path('save-data/', save_data, name='save-data'),
    path("myreplydel/<str:rno>/", MyReplyDel.as_view()),
    path("myliked/<str:username>/", MyLiked.as_view()),
    path("myreplydel/<str:likeno>/", MyLikedDel.as_view()),
    path("mixin/liked/", LikedAPIMixins.as_view()),    
    path('upload/', upload_photo, name='upload_photo'),
    path( '', views.index, name='index'),
    # path('exhibition/', views.exhibition, name='exhibition'),
    path('exhibition/', ExhibitionAPI.as_view()),
    path('exhibition/like/<int:board_no>/', LikeBoardView().as_view()),
    path('exhibition/userlikes/<str:username>/', UserLikesView().as_view()),
    path('exhibition/add_comment/<int:board_no>/', AddReply().as_view()),

    path('board_writing/', BoardWritingView.as_view()),
    path('photos/<str:username>/', PhotoListView.as_view()),

    path('board/<int:board_no>/', BoardUpdate.as_view()),  
    path('board_delete/<int:board_no>', BoardDelete.as_view()),
    path('recommend_contents/', RecommendContents.as_view()),
      
    path('chart_db/', tag_chart),
    path('chart_db_personal',tag_chart_personal)
]

