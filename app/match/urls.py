"""
URL mappings for the Match app
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from match import views

router = DefaultRouter() # CRUD를 자동으로 생성
router.register('matching', views.MatchViewSet)

app_name = 'match'

urlpatterns = [
    path('', include(router.urls)),
    # path('matching/sent/', views.MatchViewSet.as_view({'get': 'list_sent_requests'}), name = 'sent-requests'),
    # path('matching/received/', views.MatchViewSet.as_view({'get': 'list_received_requests'}), name = 'received-requests'),
    # path('matching/<int:request_id>/accept/', views.MatchViewSet.as_view({'post': 'accept_request'}), name = 'accept-request'),
]