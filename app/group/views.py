"""
Views for Group API
"""
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Group
from group import serializers


class GroupViewSet(viewsets.ModelViewSet):
    """View for manage Group APIs"""
    serializer_class = serializers.GroupDetailSerializer
    queryset = Group.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(members = self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new Group"""
        group = serializer.save() # 새로운 그룹 생성
        group.members.add(self.request.user) # 요청한 사용자를 그룹에 추가
        group.save() # 변경사항 저장

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.GroupDetailSerializer

        return self.serializer_class

    def partial_update(self, request, *args, **kwargs):
        """Add user to an existing Group"""
        group = self.get_object() # 그룹 가져오기
        group.members.add(request.user) # 요청한 사용자 추가
        group.save() # 변경사항 저장
        serializer = self.get_serializer(group) # 직렬화
        return Response(serializer.data) # 응답 반환

    # 그룹에서 탈퇴 시
    @action(detail = True, methods = ['post'], url_path = 'leave')
    def leave_group(self, request, pk = None):
        """Remove user from the group"""
        group = self.get_object() # 그룹 객체 가져오기
        user = request.user # 요청한 사용자 가져오기

        if user not in group.members.all(): # 사용자가 그룹의 멤버인지 확인
            return Response({"error": "You are not a member of this group."}, status = status.HTTP_400_BAD_REQUEST)

        group.members.remove(user) # 사용자를 그룹에서 제거
        group.save() # 변경사항 저장

        # 마지막 멤버가 나가면 그룹 삭제
        if group.members.count() == 0:
            group.delete()
            return Response({"message": "You have left the group and the group has been deleted."}, status = status.HTTP_200_OK)

        
        return Response({"message": "You have successfully left the group"}, status = status.HTTP_200_OK)