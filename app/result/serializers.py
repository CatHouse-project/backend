"""
serializers for Result APIs
"""

from rest_framework import serializers

from core.models import Result


class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ['id', 'user', 'matched_user', 'compatibility_score', 'created_at']
        read_only_fields = ['id', 'created_at']

class ResultDetailSerializer(ResultSerializer):
    """Serializer for Result detail view"""

    class Meta(ResultSerializer.Meta):
        fields = ResultSerializer.Meta.fields