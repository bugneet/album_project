from rest_framework import serializers
from .models import *

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
            "user_address",  
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
    photoid_image = serializers.CharField(source='photoid.image', read_only=True)
    photoid_phototag = serializers.CharField(source='photoid.phototag', read_only=True)

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
            'photoid_image', 
            'photoid_phototag',
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
        
class RecommendContentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendContents
        fields = [
            "contents_id",
            "phototag",
            "contents_name",
            "contents_link",
            "contents_image",
        ]