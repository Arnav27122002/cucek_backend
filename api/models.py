from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    name = models.CharField(max_length=255, verbose_name="Teacher Name")
    profession = models.CharField(max_length=255, verbose_name="Profession")
    about = models.TextField(verbose_name="About", blank=True)
    qualifications = models.TextField(verbose_name="Qualifications")
    experience = models.PositiveIntegerField(verbose_name="Years of Experience")
    branch = models.CharField(max_length=255,default='General', verbose_name="Branch Name")
    projects = models.TextField(verbose_name="Projects", blank=True)
    image = models.ImageField(upload_to='teachers_images/', blank=True, null=True)
    path = models.CharField(max_length=255, verbose_name="Path",default='\home')
    def __str__(self):
        return self.name

class Research(models.Model):
    name = models.CharField(max_length=255, verbose_name="Researcher Name")
    profession = models.CharField(max_length=255, verbose_name="Profession")
    research_interests = models.TextField(verbose_name="Research Interests")
    research_scholars = models.TextField(verbose_name="Research Scholars")
    projects = models.TextField(verbose_name="Projects")
    image = models.ImageField(upload_to='research_images/', blank=True, null=True, verbose_name="Profile Image")
    publications = models.TextField(verbose_name="Publications", blank=True)

    def __str__(self):
        return self.name



# Role choices for user type (student or teacher)
class UserRole(models.TextChoices):
    STUDENT = 'Student'
    TEACHER = 'Teacher'

# Class model

class Class(models.Model):
    # Explicitly defining the `id` field
    id = models.AutoField(primary_key=True)  # Automatically an integer, auto-incrementing field
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    # students = models.ManyToManyField(User, related_name='classes_as_student', through='ClassEnrollment')
    teachers = models.ManyToManyField(User, related_name='classes_as_teacher', through='ClassTeaching')

    def __str__(self):
        return self.name


class ClassTeaching(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_taught = models.ForeignKey(Class, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.TEACHER)

    def __str__(self):
        return f"{self.user.username} teaching {self.class_taught.name} as {self.role}"


class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name="Subject Name")
    description = models.TextField(verbose_name="Subject Description", blank=True)
    
    # One-to-many relationship (a subject belongs to one class)
    class_assigned = models.ForeignKey(
        'Class', 
        related_name='subjects', 
        on_delete=models.CASCADE, 
        verbose_name="Assigned Class"
    )
    
    def __str__(self):
        return self.name