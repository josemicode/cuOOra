from rest_framework import serializers
from rest_framework.permissions import AllowAny
from todomanager.models import Board

class BoardSerializer(serializers.HyperlinkedModelSerializer):
    permission_classes = [AllowAny]
    class Meta:
        model = Board
        fields = ['id', 'title']