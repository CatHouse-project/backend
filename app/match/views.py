"""
Views for Match APIs
"""

from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404
from core.models import Match, Group
from match import serializers

class MatchViewSet(viewsets.ModelViewSet):
    """View for manage Match APIs"""
    serializer_class = serializers.MatchDetailSerializer
    queryset = Match.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(requester = self.request.user).order_by('-id')

    def create(self, request, *args, **kwargs):
        """Send a match request"""
        recipient_id = request.data.get('recipient') # 수신자 ID
        requester = request.user # 현재 사용자 (신청자)

        # 1. 요청자가 이미 pending이나 accepted 상태인 경우 확인
        if Match.objects.filter(requester = requester, status__in = ['pending', 'accepted']).exists():
            return Response(
                {"error": "Cannot send match request: you already have a pending or accepted request."},
                status = status.HTTP_400_BAD_REQUEST
            )

        # 2. 수신자가 이미 accepted 상태인 경우 확인
        if Match.objects.filter(recipient_id = recipient_id, status__in = ['accepted']).exists():
            return Response(
                {"error": "Cannot send match request: recipient already has an accepted request."},
                status = status.HTTP_400_BAD_REQUEST
            )

        # 3. 서로 간의 요청이 있는지 확인
        if Match.objects.filter(requester = requester, recipient_id = recipient_id).exists() or \
        Match.objects.filter(requester = recipient_id, recipient_id = requester.id).exists():
            return Response(
                {"error": "Cannot send match request: there is already a match request between you two."},
                status = status.HTTP_400_BAD_REQUEST
            )

        # 4. 요청자가 속한 그룹 확인
        if Group.objects.filter(memers = requester).exists():
            return Response(
                {"error": "Cannot send match request: you are already a member of a group."},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        # Match 객체 생성
        match_request = Match.objects.create(
            requester = requester,
            recipient_id = recipient_id,
            status = 'pending' # 초기 상태는 pending
        )

        serializer = self.get_serializer(match_request)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """Retrieve incoming match requests for the current user"""
        requests = Match.objects.filter(recipient = request.user)

        serializer = self.get_serializer(requests, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @action(detail = False, methods = ['get'], url_path = 'sent')
    def list_sent_requests(self, request):
        """Retrieve all match requests sent by the current user"""
        requests_sent = Match.objects.filter(requester = request.user)
        serializer = self.get_serializer(requests_sent, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @action(detail = False, methods = ['get'], url_path = 'received')
    def list_received_requests(self, request):
        """Retrieve all match requests received by the current user"""
        requests_received = Match.objects.filter(recipient = request.user)
        serializer = self.get_serializer(requests_received, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    # 매칭 성공
    @action(detail = True, methods = ['post'], url_path = 'accept')
    def accept_request(self, request, pk = None):
        """Accept a match request and create a group"""
        match_request = get_object_or_404(Match, id = pk, recipient = request.user)

        # 요청자가 이미 accepted 상태인 경우 처리 불가
        if match_request.status == 'accepted':
            return Response({"error": "Match request already accepted."}, status = status.HTTP_400_BAD_REQUEST)

        # 요청 상태를 accepted로 변경
        match_request.status = "accepted"
        match_request.save()

        # 새로운 Group 생성
        group = Group.objects.create()

        # 두 사람 모두 그룹에 추가
        group.members.add(match_request.requester)
        group.members.add(match_request.recipient)

        return Response({
            "message": "Match request accepted and group created successfully.",
            "group_id": group.id
        }, status = status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MatchDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new MatchRequest"""
        serializer.save(requester = self.request.user)

    # 상대방이 거절할 시
    @action(detail = True, methods = ['post'], url_path = 'reject')
    def reject_request(self, request, pk = None):
        """Reject the match request and delete the group if it exists"""
        match_request = get_object_or_404(Match, pk = pk, recipient = request.user)

        # 상태를 rejected로 변경
        match_request.status = 'rejected'
        match_request.save()

        return Response({"message": "Match request rejected and deleted."}, status = status.HTTP_200_OK)