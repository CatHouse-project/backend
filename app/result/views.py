"""
Views for Result APIs
"""

from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Result
from result import serializers


class ResultViewSet(viewsets.ModelViewSet):
    """View for manage Result APIs"""
    serializer_class = serializers.MatchDetailSerializer
    queryset = Result.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 현재 사용자의 매칭 결과 반환
        return self.queryset.filter(user = self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ResultDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new match result"""
        serializer.save(user = self.request.user)

    def create(self, request, *args, **kwargs):
        """Create or update a match result"""
        print(request.data)
        user = request.user
        matched_user_id = request.data.get('matched_user') # 매칭된 사용자의 ID 받아오기
        compatibility_score = request.data.get('compatibility_score') # 적합성 점수 받아오기

        # 기존 응답이 있는 경우 업데이트, 없으면 새로 생성
        result_obj, created = Result.objects.get_or_create(
            user = user,
            matched_user_id = matched_user_id,
            defaults = {'compatibility_score': compatibility_score},
        )

        return Response({"message": "Result saved successfully."}, status = status.HTTP_201_CREATED)