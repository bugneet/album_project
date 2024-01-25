from rest_framework import serializers
from .models import PhotoTable, Board, Reply, Liked, UsersAppUser

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsersAppUser
        fields = [
            "id",
            "username",
            "first_name", 
            "last_name",            
            "user_name",
            "email",
            "user_adress",  
            "last_login",
            "date_joined",          
        ]

class PhotoTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTable
        fields = [
            "photoid",
            "photohash",
            "phototag",
            "photodate",
            "uploaddate",
            "image",
            "id",
        ]

class BoardSerializer(serializers.ModelSerializer):
    photoid = PhotoTableSerializer()
    id = UserSerializer()

    class Meta:
        model = Board
        fields = [
            "board_no",
            "title",
            "contents",
            "id",
            "created_time",
            "photoid",     
            "board_photo_tag",      
        ]




class ReplySerializer(serializers.ModelSerializer):
    board_no = BoardSerializer()
    
    
    class Meta:
        model = Reply
        fields = [
            "rno",
            "board_no",
            "replytext",
            "id",
            "regdate",          
        ]


class LikedSerializer(serializers.ModelSerializer):
    board_no = BoardSerializer()
    
    class Meta:
        model = Liked
        fields = [
            "likeno",
            "board_no",
            "id",
            "likedate",          
        ]