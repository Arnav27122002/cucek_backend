from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=255, verbose_name="Teacher Name")
    profession = models.CharField(max_length=255, verbose_name="Profession")
    about = models.TextField(verbose_name="About", blank=True)
    qualifications = models.TextField(verbose_name="Qualifications")
    experience = models.PositiveIntegerField(verbose_name="Years of Experience")
    branch = models.CharField(max_length=255,default='General', verbose_name="Branch Name")
    projects = models.TextField(verbose_name="Projects", blank=True)
    others = models.TextField(verbose_name="Other Achievements", blank=True)
    conferences = models.TextField(verbose_name="Conferences Attended", blank=True)
    journals = models.TextField(verbose_name="Journals Published", blank=True)
    image = models.ImageField(upload_to='teachers_images/', blank=True, null=True)

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
