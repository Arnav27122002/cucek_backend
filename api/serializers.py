from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Exam, PlacementCompany, PlacementProfile, Teacher, Research, Class, Subject, PlacementApplication

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove the confirm password field
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        return {"user": user}

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class ResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = [ 'id', 'name', 'description']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id" ,'name', 'description']


class PlacementProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementProfile
        fields = ["cgpa", "user", "percentage_10th", "percentage_12th", "is_placement_coordinator"]
        

class PlacementCompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementCompany
        fields = "__all__"

class PlacementCompanySerializer(serializers.ModelSerializer):
    is_eligible = serializers.BooleanField(read_only=True)
    applied = serializers.BooleanField(read_only=True)
    class Meta:
        model = PlacementCompany
        fields = ["id" ,"name", "job_description", "min_cgpa", "min_10th", "min_12th", "max_backlogs", "package", "is_eligible", "applied"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        profile = self.context.get('profile')
        user = self.context.get('user')
        
        if profile:
            representation['is_eligible'] = (
                profile.cgpa >= instance.min_cgpa and
                profile.percentage_10th >= instance.min_10th and
                profile.percentage_12th >= instance.min_12th
                # and profile.backlogs <= instance.max_backlogs
            )

            representation["applied"] = PlacementApplication.objects.filter(user=user, company=instance).count() > 0

        else:
            representation['is_eligible'] = False
            
        return representation
    
class ApplicationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    company = PlacementCompanySerializer()

    class Meta:
        model = PlacementApplication
        fields = ["user", "company", "other_details"]