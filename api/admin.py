from django.contrib import admin

from .models import Class, ClassTeaching, Subject

admin.site.register(Class)
admin.site.register(ClassTeaching)
admin.site.register(Subject)
