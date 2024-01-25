from rest_framework import serializers
from .models import Board, PhotoTable

class BoardSerializer(serializers.ModelSerializer):
    photoid_image = serializers.CharField(source='photoid.image', read_only=True)
    photoid_phototag = serializers.CharField(source='photoid.phototag', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'created_time', 'contents', 'photoid', 'photoid_image', 'photoid_phototag']
        

class PhotoTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTable
        fields = '__all__'
