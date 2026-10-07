from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from .api_views import ClassRoomViewSet, StudentViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'classes', ClassRoomViewSet, basename='api-class')
router.register(r'students', StudentViewSet, basename='api-student')
router.register(r'attendance', AttendanceViewSet, basename='api-attendance')

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('', include(router.urls)),
]