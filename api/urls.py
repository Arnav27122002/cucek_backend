from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    PlacementProfileView,
    TeacherViewSet,
    ResearchViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    TeacherClassesView,
    ClassDetailView,
    AddStudentToClass,
    AddSubjectToClass,
    CreateExamView,
    PublishExamResultsView,
    ViewExamResultsView,
    ViewSubjectExamsView,
    TeacherCheckView
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'research', ResearchViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('class/<int:class_id>/role/', TeacherCheckView.as_view()),
    path('placement/profile/', PlacementProfileView.as_view(), name="placement_views"),
    path('view-exam-results/<int:exam_id>/', ViewExamResultsView.as_view(), name='view_exam_results'),
    path('view-exam-results/<int:exam_id>/', ViewExamResultsView.as_view() , name='view_exam_results'),
    path('subjects/<int:subject_id>/exams/', ViewSubjectExamsView.as_view(), name='view_exam_results'),
    path('exams/<int:exam_id>/publish-results/', PublishExamResultsView.as_view(), name='publish_exam_results'),
    path("class/<int:class_id>/<int:subject_id>/add-exam/",  CreateExamView.as_view(), name="add_subject"),
    path("class/<int:class_id>/add-subject/", AddSubjectToClass.as_view(), name="add_subject"),
    path("class/<int:class_id>/add-student/", AddStudentToClass.as_view(), name="add_student"),
    path('class/<int:pk>/details/', ClassDetailView.as_view(), name='class_details'),
    path('teacher/classes/', TeacherClassesView.as_view(), name='teacher_classes'),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
