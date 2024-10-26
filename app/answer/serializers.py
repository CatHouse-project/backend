"""
serializers for Answer APIs
"""
from rest_framework import serializers

from core.models import Answer
from user.serializers import UserSerializer

class AnswerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only = True) # user의 id만 가져오기

    class Meta:
        model = Answer
        fields = ['id', 'user', 'responses']
        read_only_fields = ['id']

class AnswerDetailSerializer(AnswerSerializer):
    """Serializer for Answer detail view"""

    class Meta(AnswerSerializer.Meta):
        fields = AnswerSerializer.Meta.fields