from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path( '', views.index, name='index'),
    # path('exhibition/', views.exhibition, name='exhibition'),
    path('exhibition/', ExhibitionAPI.as_view()),
    path('current_user/', CurrentUserView.as_view()),
    path('board_writing/', BoardWritingView.as_view()),
    path('photos/<int:user_id>/', PhotoListView.as_view()),
    path('boards/', BoardAPIMixins.as_view()),
    path('board/<str:board_no>/', BoardAPIMixins.as_view())

    # path('board_writing/', views.board_writing, name='board_writing'),
    # path('board_detail/<int:board_no>', views.board_detail, name='board_detail'),
    # path('board_edit/<int:board_no>', views.board_edit, name='board_edit'),
    # path('board_delete/<int:board_no>', views.board_delete, name='board_delete'),
    # path('photo_choose/', views.photo_choose, name='photo_choose'),
    # path('photo_edit/', views.photo_edit, name='photo_edit'),
]
