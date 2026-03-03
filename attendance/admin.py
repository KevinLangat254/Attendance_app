from django.contrib import admin
from .models import User, Program, Enrollment, Unit, Session, Attendance

admin.site.register([User, Program, Enrollment, Unit, Session, Attendance])