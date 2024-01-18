from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import upload_photo


urlpatterns=[
    path('analysis-results/', analysis_results_view, name='analysis-results'),
    path('upload/', upload_photo, name='upload-photo'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
]