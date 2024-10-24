"""
serializers for Answer APIs
"""
from rest_framework import serializers

from core.models import Answer


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['id', 'answer']
        read_only_fields = ['id']

class AnswerDetailSerializer(AnswerSerializer):
    """Serializer for Answer detail view"""

    class Meta(AnswerSerializer.Meta):
        fields = AnswerSerializer.Meta.fields