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
    serializer_class = serializers.ResultDetailSerializer
    queryset = Result.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user = self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ResultDetailSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """Receive matching data from AI and save it"""
        # 현재 로그인된 사용자 가져오기
        user = request.user

        # serializer 초기화
        serializer = self.get_serializer(data = request.data)

        # 유효성 검사
        serializer.is_valid(raise_exception = True)

        # user 필드에 현재 사용자 설정 후 데이터 저장
        serializer.save(user = user)

        return Response({"message": "Result successfully created."}, status = status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Deleting a result with a success message"""
        instance = self.get_object() # 삭제할 객체 가져오기
        self.perform_destroy(instance) # 객체 삭제

        # 삭제 성공 메시지
        return Response(
            {"message": "Result successfully deleted."},
            status = status.HTTP_200_OK
        )