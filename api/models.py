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


class Class(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Exam(models.Model):
    class_obj = models.ForeignKey(Class, related_name='exams', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.class_obj.name})"

class Enrollment(models.Model):
    student: User = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, related_name='enrollments', on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} in {self.class_obj.name}"

class MarkList(models.Model):
    student: User = models.ForeignKey(User, related_name='marklists', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, related_name='marks', on_delete=models.CASCADE)
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.username} - {self.exam.name}"