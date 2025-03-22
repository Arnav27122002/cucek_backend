from django.contrib import admin

from .models import Class, ClassEnrollment, ClassTeaching

admin.site.register(Class)
admin.site.register(ClassEnrollment)
admin.site.register(ClassTeaching)
