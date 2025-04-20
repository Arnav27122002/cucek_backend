from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import PlacementApplication, PlacementCompany, PlacementProfile, Teacher, Research
from .serializers import (
    PlacementCompanyAdminSerializer,
    PlacementCompanySerializer,
    PlacementProfileSerializer,
    TeacherSerializer,
    ResearchSerializer,
    RegisterSerializer,
    LoginSerializer,
    ClassSerializer,
    UserSerializer,
    SubjectSerializer,
    ApplicationSerializer
)
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Teacher, Class, ClassTeaching, UserRole, Subject, Exam, ExamResult
from django.utils.timezone import get_current_timezone
import os
import requests
from django.core.files.base import ContentFile

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
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
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
        response["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"  # Add the Referrer-Policy header
        )
        # You can add other headers if needed
        response["Custom-Header"] = "Value"

        # Return the response with custom headers
        return response


class TeacherCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):

        class_obj = get_object_or_404(Class, pk=class_id)
        teaching = get_object_or_404(
            ClassTeaching, class_taught=class_obj, user=request.user)
        return Response(
            {
                "role": teaching.role
            }
        )


class TeacherCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):

        class_obj = get_object_or_404(Class, pk=class_id)
        teaching = get_object_or_404(
            ClassTeaching, class_taught=class_obj, user=request.user)
        return Response(
            {
                "role": teaching.role
            }
        )


class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, pk):
        # Get the class object by primary key
        class_obj = get_object_or_404(Class, pk=pk)

        # Get the teachers associated with the class
        persons = ClassTeaching.objects.filter(class_taught=class_obj)

        subjects = Subject.objects.filter(class_assigned=class_obj)

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
        subject_serializer = SubjectSerializer(subjects, many=True)

        # Serialize class data
        class_serializer = ClassSerializer(class_obj)

        # Return the class data with teachers and students
        return Response(
            {
                "class": class_serializer.data,
                "teachers": teacher_serializer.data,
                "students": student_serializer.data,
                "subjects": subject_serializer.data,
            }
        )


class AddStudentToClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id):
        # Get the class object
        class_obj = get_object_or_404(Class, id=class_id)

        # Check if the requesting user is a teacher in this class
        if not ClassTeaching.objects.filter(
            user=request.user, class_taught=class_obj, role=UserRole.TEACHER
        ).exists():
            return Response(
                {"error": "You are not authorized to add students to this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the student email from request data
        student_email = request.data.get("student_email")
        if not student_email:
            return Response(
                {"error": "Student email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get the student object
        student = get_object_or_404(User, email=student_email)

        # Check if the user is already enrolled
        if ClassTeaching.objects.filter(user=student, class_taught=class_obj).exists():
            return Response(
                {"error": "Student is already enrolled in this class."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enroll the student
        ClassTeaching.objects.create(
            user=student, class_taught=class_obj, role=UserRole.STUDENT
        )

        return Response(
            {"message": "Student added successfully to the class."},
            status=status.HTTP_201_CREATED,
        )


class AddSubjectToClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id):
        # Get the class object
        class_obj = get_object_or_404(Class, id=class_id)

        # Check if the user is a teacher in this class
        if not ClassTeaching.objects.filter(
            user=request.user, class_taught=class_obj, role=UserRole.TEACHER
        ).exists():
            return Response(
                {"error": "You are not authorized to add subjects to this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the subject data from the request
        subject_name = request.data.get("name")
        subject_description = request.data.get("description", "")

        # Validate subject name
        if not subject_name:
            return Response(
                {"error": "Subject name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new subject and associate it with the class
        subject = Subject.objects.create(
            name=subject_name, description=subject_description, class_assigned=class_obj
        )

        return Response(
            {
                "message": "Subject added successfully to the class.",
                "subject": {"name": subject.name, "description": subject.description},
            },
            status=status.HTTP_201_CREATED,
        )


class CreateExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id, subject_id):
        # Get the class and subject objects
        class_obj = get_object_or_404(Class, id=class_id)
        subject_obj = get_object_or_404(Subject, id=subject_id)

        # Check if the user is a teacher for the specified class
        if not ClassTeaching.objects.filter(
            user=request.user, class_taught=class_obj, role=UserRole.TEACHER
        ).exists():
            return Response(
                {"error": "You are not authorized to create an exam for this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the exam details from the request
        exam_name = request.data.get("name")
        exam_description = request.data.get("description", "")

        # Validate input
        if not exam_name:
            return Response(
                {"error": "Exam name and date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse the exam date into a datetime object

        exam = Exam.objects.create(
            name=exam_name,
            description=exam_description,
            class_assigned=class_obj,
            subject=subject_obj,
        )

        return Response(
            {
                "message": "Exam created successfully.",
                "exam": {
                    "name": exam.name,
                    "description": exam.description,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class PublishExamResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id):
        # Get the exam object
        exam = get_object_or_404(Exam, id=exam_id)

        # Check if the user is a teacher for this class
        if not exam.class_assigned.teachers.filter(id=request.user.id).exists():
            return Response(
                {"error": "You are not authorized to publish results for this exam."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the results data from the request
        results_data = request.data.get("results")
        if not results_data:
            return Response(
                {"error": "No results data provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or update the ExamResult for this exam
        exam_result, created = ExamResult.objects.get_or_create(Exam=exam)

        # Loop through the results and add them to the ExamResult model
        for result in results_data:
            student_id = result.get("student_id")
            marks = result.get("marks")
            grade = result.get("grade", None)

            # Ensure the student exists
            student = get_object_or_404(User, id=student_id)

            # Add the student result to the exam results (in JSON format)
            exam_result.add_student_result(student, marks, grade)

        return Response(
            {"message": "Exam results published successfully!"},
            status=status.HTTP_201_CREATED,
        )


class ViewExamResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        # Get the exam result for the provided exam ID
        exam_result = get_object_or_404(ExamResult, Exam__id=exam_id)

        # Retrieve the results from the JSONField
        results = exam_result.results

        # If there are no results, return a message indicating so
        if not results:
            return Response(
                {"message": "No results published for this exam yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return the results in the response
        return Response(
            {
                "exam": exam_result.Exam.name,
                "subject": exam_result.Exam.subject.name,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class ViewSubjectExamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        # Get the subject object by subject_id
        subject = get_object_or_404(Subject, id=subject_id)

        # Get all exams related to this subject
        exams = Exam.objects.filter(subject=subject)

        # If no exams are found, return a message
        if not exams:
            return Response(
                {"message": "No exams found for this subject."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the exam data
        exam_data = [
            {
                "id": exam.id,
                "name": exam.name,
                "description": exam.description,
                "class_assigned": exam.class_assigned.name,
                "subject": exam.subject.name,
            }
            for exam in exams
        ]

        # Return the exams for the subject
        return Response(
            {"subject": subject.name, "exams": exam_data}, status=status.HTTP_200_OK
        )


class PlacementProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile = get_object_or_404(PlacementProfile, user=request.user)
        return Response(
            PlacementProfileSerializer(profile).data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        try:
            profile = PlacementProfile.objects.get(user=request.user)
        except PlacementProfile.DoesNotExist:
            profile = None

        if profile is not None:
            return Response(
                {"error": "Profile already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cgpa = request.data.get("cgpa")
        percentage_10th = request.data.get("percentage_10th")
        percentage_12th = request.data.get("percentage_12th")
        if cgpa is None or percentage_10th is None or percentage_12th is None:
            return Response(
                {"error": "Invalid data provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {
            "cgpa": round(cgpa, 2),
            "percentage_10th": round(percentage_10th, 4),
            "percentage_12th": round(percentage_12th, 4),
        }

        place_profile = PlacementProfile.objects.create(
            user=request.user, **data)
        return Response(
            {"profile": PlacementProfileSerializer(place_profile).data},
            status=status.HTTP_201_CREATED,
        )


class PlacementCompanyView(APIView):
    def get(self, request):
        companies = PlacementCompany.objects.all()
        serializer = PlacementCompanyAdminSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        placement_profile = PlacementProfile.objects.get(user=request.user)
        if not placement_profile.is_placement_coordinator:
            return Response({"detail", "No permission, Only placment coordinator is permitted to add comapany"}, status=status.HTTP_403_FORBIDDEN)

        serializer = PlacementCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlacementStudentCompanyView(APIView):
    def get(self, request):
        # Get the current user's placement profile
        try:
            profile = PlacementProfile.objects.get(user=request.user)
        except PlacementProfile.DoesNotExist:
            return Response(
                {"error": "Placement profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Filter companies based on eligibility criteria
        companies = PlacementCompany.objects.all()

        serializer = PlacementCompanySerializer(companies, many=True, context={
                                                "profile": profile, "user": request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlacementApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get company ID from request data
        company_id = request.data.get("company_id")
        if not company_id:
            return Response(
                {"error": "company_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the company and profile
            company = get_object_or_404(PlacementCompany, pk=company_id)
            profile = PlacementProfile.objects.get(user=request.user)

            # Check if user already applied
            if PlacementApplication.objects.filter(user=request.user, company=company).exists():
                return Response(
                    {"error": "You have already applied to this company"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check eligibility
            if not (profile.cgpa >= company.min_cgpa and
                    profile.percentage_10th >= company.min_10th and
                    profile.percentage_12th >= company.min_12th):
                return Response(
                    {"error": "You do not meet the eligibility criteria"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Create application
            application_data = PlacementProfileSerializer(profile).data
            application = PlacementApplication.objects.create(
                user=request.user,
                company=company,
                other_details=application_data
            )

            print(ApplicationSerializer(application).data)

            return Response(
                ApplicationSerializer(application).data,
                status=status.HTTP_201_CREATED
            )

        except PlacementProfile.DoesNotExist:
            return Response(
                {"error": "Placement profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlacementApplicationView(APIView):

    def get(self, request, company_id):
        company = PlacementCompany.objects.get(pk=company_id)
        applications = PlacementApplication.objects.filter(company=company)
        return Response(
            ApplicationSerializer(applications, many=True).data
        )


class AddTeacherView(APIView):
    def get(self, request):
        teachers_data = {
            "CSE": [
                {
                    "name": "Dr. Preetha Mathew",
                    "profession": "HOD CS",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/01.jpg",
                    "profileLink": "?page=12&s=17"
                },
                {
                    "name": "Bindu P K",
                    "profession": "Associate Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/02.jpg",
                    "profileLink": "?page=12&s=18"
                },
                {
                    "name": "Manoj Kumar P",
                    "profession": "Associate Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/03.jpg",
                    "profileLink": "?page=12&s=20"
                },
                {
                    "name": "Anitha Mary Chacko",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/16.jpg",
                    "profileLink": "?page=12&s=141"
                },
                {
                    "name": "Alice Joseph",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/07.jpg",
                    "profileLink": "?page=12&s=6"
                },
                {
                    "name": "Aswathy V Shaji",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/22.jpg",
                    "profileLink": "?page=12&s=197"
                },
                {
                    "name": "Hafeesa M Habeeb",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/24.jpg",
                    "profileLink": "?page=12&s=215"
                },
                {
                    "name": "Amritha Mary Davis",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CSE/FACULTY PICS/0.jpg",
                    "profileLink": "?page=12&s=#"
                }
            ],
            "CE": [
                {
                    "name": "Dr.Sunilkumar N",
                    "profession": "HOD CE",
                    "image": "images/PIC & SIGN/CE/FACULTY PICS/01.jpg",
                    "profileLink": "?page=12&s=52"
                },
                {
                    "name": "Minimole A",
                    "profession": "Associate Professor",
                    "image": "images/PIC & SIGN/CE/FACULTY PICS/02.jpg",
                    "profileLink": "?page=12&s=15"
                },
                {
                    "name": "Harija K S",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CE/FACULTY PICS/40.jpg",
                    "profileLink": "?page=12&s=205"
                },
                {
                    "name": "Prajeesha M P",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CE/FACULTY PICS/0.jpg",
                    "profileLink": "?page=12&s=#"
                },
                {
                    "name": "Aimy Rose Joy",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/CE/FACULTY PICS/0.jpg",
                    "profileLink": "?page=12&s=#"
                }
            ],
            "ECE": [
                {
                    "name": "Dr.Anilkumar K K",
                    "profession": "HOD ECE",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/02.jpg",
                    "profileLink": "?page=12&s=26"
                },
                {
                    "name": "Dr. Manoj V J",
                    "profession": "Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/01.jpg",
                    "profileLink": "?page=12&s=199"
                },
                {
                    "name": "Nishanth R",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/24.jpg",
                    "profileLink": "?page=12&s=203"
                },
                {
                    "name": "Akhila L",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/05.jpg",
                    "profileLink": "?page=12&s=67"
                },
                {
                    "name": "Abin John Joseph",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/06.jpg",
                    "profileLink": "?page=12&s=21"
                },
                {
                    "name": "Malini Mohan",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/19.jpg",
                    "profileLink": "?page=12&s=146"
                },
                {
                    "name": "Sujith P S",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/21.jpg",
                    "profileLink": "?page=12&s=200"
                },
                {
                    "name": "Jaya Sukes",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/ECE/FACULTY PICS/26.jpg",
                    "profileLink": "?page=12&s=214"
                }
            ],
            "EEE": [
                {
                    "name": "Dr.Shiny Paul",
                    "profession": "HOD EEE",
                    "image": "images/PIC & SIGN/EEE/FACULTY PICS/02.jpg",
                    "profileLink": "?page=12&s=29"
                },
                {
                    "name": "Priya R Krishnan",
                    "profession": "Associate Professor",
                    "image": "images/PIC & SIGN/EEE/FACULTY PICS/04.jpg",
                    "profileLink": "?page=12&s=27"
                },
                {
                    "name": "Sajan Joseph",
                    "profession": "Associate Professor",
                    "image": "images/PIC & SIGN/EEE/FACULTY PICS/03.jpg",
                    "profileLink": "?page=12&s=30"
                },
                {
                    "name": "Nakul Sasikumar",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/EEE/FACULTY PICS/30.jpg",
                    "profileLink": "?page=12&s=156"
                },
                {
                    "name": "Raji Reghunanthan",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/EEE/FACULTY PICS/36.jpg",
                    "profileLink": "?page=12&s=209"
                }
            ],
            "IT": [
                {
                    "name": "Dr.Jabir K V T",
                    "profession": "HOD IT",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/02.jpg",
                    "profileLink": "?page=12&s=43"
                },
                {
                    "name": "Dr.Jayaprabha P",
                    "profession": "Associate Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/01.jpg",
                    "profileLink": "?page=12&s=42"
                },
                {
                    "name": "Dr.Harikrishnan D",
                    "profession": "Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/03.jpg",
                    "profileLink": "?page=12&s=44"
                },
                {
                    "name": "Nidhin Sani",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/05.jpg",
                    "profileLink": "?page=12&s=40"
                },
                {
                    "name": "Vineeth M V",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/16.jpg",
                    "profileLink": "?page=12&s=188"
                },
                {
                    "name": "Santhikrishna M S",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/17.jpg",
                    "profileLink": "?page=12&s=189"
                },
                {
                    "name": "Athira K R",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/21.jpg",
                    "profileLink": "?page=12&s=223"
                },
                {
                    "name": "Vidya Muraleedharan",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/22.jpg",
                    "profileLink": "?page=12&s=#"
                },
                {
                    "name": "Jesna A A",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/23.jpg",
                    "profileLink": "?page=12&s=#"
                },
                {
                    "name": "Keethimol P P",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/IT/FACULTY PICS/20.jpg",
                    "profileLink": "?page=12&s=222"
                }
            ],
            "MCA": [
                {
                    "name": "Deepa Nair",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/MCA/FACULTY PICS/01.jpg",
                    "profileLink": "?page=12&s=45"
                },
                {
                    "name": "Radhika B",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/MCA/FACULTY PICS/09.jpg",
                    "profileLink": "?page=12&s=75"
                },
                {
                    "name": "Anoop S",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/MCA/FACULTY PICS/19.jpg",
                    "profileLink": "?page=12&s=191"
                },
                {
                    "name": "Sanjana",
                    "profession": "Assistant Professor",
                    "image": "images/PIC & SIGN/MCA/FACULTY PICS/0.jpg",
                    "profileLink": "?page=12&s=#"
                }
            ]
        }

        for branch, teachers in teachers_data.items():
            for data in teachers:
                image_url = f"https://cucek.cusat.ac.in/{data['image']}"
                image_name = os.path.basename(data["image"]).replace(
                    " ", "_")  # Clean image name

                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        image_file = ContentFile(
                            response.content, name=image_name)

                        Teacher.objects.create(
                            name=data["name"],
                            profession=data["profession"],
                            about="",
                            qualifications="M.Tech",
                            experience=0,
                            branch=branch,  # Use the branch dynamically here
                            projects="",
                            image=image_file,  # Saving image to the model field
                            path=data["profileLink"]
                        )
                    else:
                        print(
                            f"Failed to download image: {image_url} (Status {response.status_code})")

                except Exception as e:
                    print(f"Error downloading image {image_url}: {e}")

        return Response({"message": "Teachers added successfully."})
