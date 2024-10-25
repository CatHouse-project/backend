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
]