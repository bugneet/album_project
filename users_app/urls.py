from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# from .views import upload_photo
from .views import RegisterView, LoginView

urlpatterns=[
    # path('analysis-results/', views.analysis_results_view, name='analysis-results'),
    # path('upload/', upload_photo, name='upload-photo'),
    path('register/', RegisterView.as_view()), 
    path('login/', LoginView.as_view()),
]