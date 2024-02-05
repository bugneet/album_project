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
    path('save-data/<str:username>', save_data, name='save-data'),    
    path("albumupdate/<str:photoid>/", MyAlbumUpdate.as_view()),
    path("album_update/<str:photoid>/", album_update),
    
    path("myalbumdel/<str:photoid>/", MyAlbumDel.as_view()),
    path("myreplydel/<str:rno>/", MyReplyDel.as_view()),
    path("myliked/<str:username>/", MyLiked.as_view()),
    path("mylikedel/<str:likeno>/", MyLikedDel.as_view()),

    path("mixin/liked/", LikedAPIMixins.as_view()),    
    # path('upload/', upload_photo, name='upload_photo'),
    path( '', views.index, name='index'),
    # path('exhibition/', views.exhibition, name='exhibition'),
    path('exhibition/', ExhibitionAPI.as_view()),
    path('exhibition/like/<int:board_no>/', LikeBoardView().as_view()),
    path('exhibition/userlikes/<str:username>/', UserLikesView().as_view()),
    path('exhibition/add_comment/<int:board_no>/', AddReply().as_view()),
    path('exhibition/delete_comment/<int:rno>/', ReplyDelete.as_view()),

    path('board_writing/', BoardWritingView.as_view()),
    path('photos/<str:username>/', PhotoListView.as_view()),

    path('board/<int:board_no>/', BoardUpdate.as_view()),  
    path('board_delete/<int:board_no>', BoardDelete.as_view()),
 
    path('user_analysis/<str:username>/', UserAnalysis.as_view(), name='user_analysis'), 
    path('board_delete/<int:board_no>/', BoardDelete.as_view()),
    path('recommend_tags/<str:username>/', RecommendTags.as_view()),
      
    path('recommend_contents/', RecommendContent.as_view()),

    path('user_analysis/<str:username>/', UserAnalysis.as_view(), name='user_analysis'),
    path('get_matching_activities/', UserAnalysis.get_matching_activities, name='get_matching_activities'),

    path('chart_db/', tag_chart),
    # path('personal_chart/<int:login_id>',personal_chart)
    path('personal_chart/<str:username>/',personal_chart),
    path('personal_chart_yearly/<str:username>/',personal_chart_yearly),
    path('personal_chart_yearly_top3/<str:username>/',personal_chart_yearly_top3),
    path('combined_api_view/<str:username>/', combined_api_view),

    path('tag_chart_yearly/', tag_chart_yearly),
    path('tag_count_yearly_chart/', tag_count_yearly_chart),
    path('custom_tags_count_yearly_chart/', custom_tags_count_yearly_chart),
    path('tag_chart_yearly_top3/', tag_chart_yearly_top3),
    path('recommend_contents3/', total_combined_api_view),

    path('recommend_table/', Recommendtable.as_view()),



    path("upload/", file_upload),
]    

