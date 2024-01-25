from rest_framework import serializers
from .models import PhotoTable, Board, Reply

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
    class Meta:
        model = Board
        fields = [
            "board_no",
            "title",
            "contents",
            "id",
            "created_time",
            "photoid",            
        ]

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = [
            "rno",
            "board_no",
            "replytext",
            "id",
            "regdate",          
        ]