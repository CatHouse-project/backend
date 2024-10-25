"""
serializers for Result APIs
"""
from rest_framework import serializers

from core.models import Result

class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ['id', 'user', 'matching_data']
        read_only_fields = ['id', 'user']

        def validate_data(self, value):
            # 데이터 검증: results 내에 target_user_id와 compatibility_score가 존재하는지 확인
            if not isinstance(value, dict) or 'results' not in value:
                raise serializers.ValidationError("Invalid compatibility_data format.")

            for entry in value['results']:
                if 'target_user_id' not in entry or 'compatibility_score' not in entry:
                    raise serializers.ValidationError("Each result must have 'target_user_id' and 'compatibility_score'.")
            
            return value

class ResultDetailSerializer(ResultSerializer):
    """Serializer for Result detail view"""

    class Meta(ResultSerializer.Meta):
        fields = ResultSerializer.Meta.fields