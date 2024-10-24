"""
URL mappings for the group app
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from result import views

router = DefaultRouter() # CRUD를 자동으로 생성
router.register('results', views.ResultViewSet)

app_name = 'result'

urlpatterns = [
    path('', include(router.urls))
]