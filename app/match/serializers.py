"""
serializers for Match APIs
"""

from rest_framework import serializers

from core.models import Match

class MatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Match
        fields = ['id', 'recipient', 'status', 'created_at']
        read_only_fields = ['id', 'status']

class MatchDetailSerializer(MatchSerializer):
    """Serializer for Match detail view"""

    class Meta(MatchSerializer.Meta):
        fields = MatchSerializer.Meta.fields