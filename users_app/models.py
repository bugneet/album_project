from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    #pass # 기본 auth_user 테이블과 동일 
    # 새로운 필드 추가 
    user_name = models.CharField(max_length=30)
    user_adress = models.CharField(max_length=200)    



class Photo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='photos/') 

    def __str__(self):
        return self.title