from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    TeacherViewSet,
    ResearchViewSet,
    RegisterView,
    LoginView,
    LogoutView, TeacherClassViewSet
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'research', ResearchViewSet)
router.register(r'teacher-classes', TeacherClassViewSet, basename='teacher-class')

urlpatterns = [
    path('', include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
