from django.contrib import admin

from .models import Class, ClassTeaching, Subject, ExamResult, Exam

admin.site.register(Class)
admin.site.register(ClassTeaching)
admin.site.register(Subject)
admin.site.register(ExamResult)
admin.site.register(Exam)
