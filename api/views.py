from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Teacher, Research, ClassEnrollment
from .serializers import (
    TeacherSerializer,
    ResearchSerializer,
    RegisterSerializer,
    LoginSerializer,
    ClassSerializer,
    UserSerializer
)
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Teacher, Class, ClassTeaching, UserRole


User = get_user_model()

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ResearchViewSet(viewsets.ModelViewSet):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected endpoint!"})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TeacherClassesView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        # Get the authenticated teacher (User)
        teacher = request.user

        # Get the classes the teacher is teaching using ClassTeaching model
        classes = ClassTeaching.objects.filter(user=teacher)
        
        # Serialize the classes
        class_data = [class_taught.class_taught for class_taught in classes]
        serializer = ClassSerializer(class_data, many=True)

        # Create the response
        response = Response({"classes": serializer.data})

        # Add custom headers here
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'  # Add the Referrer-Policy header
        response['Custom-Header'] = 'Value'  # You can add other headers if needed

        # Return the response with custom headers
        return response
    
class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, pk):
        # Get the class object by primary key
        class_obj = get_object_or_404(Class, pk=pk)

        # Get the teachers associated with the class
        persons = ClassTeaching.objects.filter(class_taught=class_obj)
        
        teachers = []
        students = []
        
        for person in persons:
            print(person.role)
            
            if person.role == UserRole.TEACHER:
                teachers.append(person.user)

            if person.role == UserRole.STUDENT:
                students.append(person.user)

        # Serialize teacher and student data
        teacher_serializer = UserSerializer(teachers, many=True)
        student_serializer = UserSerializer(students, many=True)

        # Serialize class data
        class_serializer = ClassSerializer(class_obj)

        # Return the class data with teachers and students
        return Response({
            'class': class_serializer.data,
            'teachers': teacher_serializer.data,
            'students': student_serializer.data
        })