"""
Views for Result APIs
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import requests

from core.models import Result, User
from result import serializers
from django.contrib.auth import get_user_model

class ResultViewSet(viewsets.ModelViewSet):
    """View for managing result APIs"""
    serializer_class = serializers.ResultDetailSerializer
    queryset = Result.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Receive matching data from AI and save it"""
        user = request.user

        # 요청 본문에서 matching_data를 가져옵니다.
        matching_data = request.data.get("matching_data", {})

        # userid와 core_questions를 추출합니다.
        userid = matching_data.get("userid")
        core_questions = matching_data.get("core_questions", [])

        if userid is None or not core_questions:
            return Response({"error": "userid and core_questions are required."}, status=status.HTTP_400_BAD_REQUEST)

        # AI에 GET 요청 보내기 (예시 URL 사용)
        ai_response = requests.get(f'AI_ENDPOINT?userid={userid}&questions={",".join(map(str, core_questions))}')
        
        if ai_response.status_code != 200:
            return Response({"error": "Failed to get data from AI"}, status=status.HTTP_400_BAD_REQUEST)

        # AI로부터 받은 데이터
        ai_data = ai_response.json()

        # user_list에서 matching_data를 가져옴
        user_list = ai_data.get("user_list", {})

        # AI로부터 받은 데이터를 그대로 저장
        serializer = self.get_serializer(data={
            'matching_data': user_list  # 전체 데이터를 그대로 저장
        })

        # 유효성 검사
        serializer.is_valid(raise_exception=True)

        # user 필드에 현재 사용자 설정 후 데이터 저장
        serializer.save(user=user)

        return Response({"message": "Results successfully created."}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """Return the list of results with user IDs, nicknames, and scores"""
        queryset = self.get_queryset()
        results = []

        for result in queryset:
            matching_data = result.matching_data.get("user_list", {})

            for userid, score in matching_data.items():
                try:
                    user = User.objects.get(id=int(userid))  # 사용자 ID로 사용자 정보 가져오기
                    nickname = user.nickname  # 닉네임 가져오기
                except User.DoesNotExist:
                    nickname = None  # 사용자가 존재하지 않는 경우

                results.append({
                    "userid": int(userid),
                    "nickname": nickname,
                    "score": score,
                })

        return Response(results)