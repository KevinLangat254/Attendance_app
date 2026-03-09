from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Program, Enrollment, Unit, Session, Attendance
from .serializers import (
    UserSerializer, ProgramSerializer, EnrollmentSerializer,
    UnitSerializer, SessionSerializer, AttendanceSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


class ProgramViewSet(viewsets.ModelViewSet):
    queryset           = Program.objects.all().order_by('faculty', 'course')
    serializer_class   = ProgramSerializer
    permission_classes = [AllowAny]   # ← public, no token needed


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['student', 'program']

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['student', 'session']