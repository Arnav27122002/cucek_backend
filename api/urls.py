from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    TeacherViewSet,
    ResearchViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    TeacherClassesView,
    ClassDetailView,
    AddStudentToClass
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'research', ResearchViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("class/<int:class_id>/add-student/", AddStudentToClass.as_view(), name="add_student"),
    path('class/<int:pk>/details/', ClassDetailView.as_view(), name='class_details'),
    path('teacher/classes/', TeacherClassesView.as_view(), name='teacher_classes'),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
]
