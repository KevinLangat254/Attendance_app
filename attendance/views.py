from rest_framework import viewsets,status
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Program, Enrollment, Unit, Session, Attendance
from .serializers import (
    UserSerializer, ProgramSerializer, EnrollmentSerializer,
    UnitSerializer, SessionSerializer, AttendanceSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


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





# ── CLAIM A UNIT ──
# Allows a teacher to assign themselves as the teacher of a unit.
# Any authenticated user can claim an unassigned unit.
# If the unit already has a teacher, they will be replaced — 
# add an extra check below if you want to prevent that.
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def claim_unit(request, unit_id):
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found'}, status=404)

    # Optional: prevent claiming a unit already assigned to someone else
    if unit.teacher is not None and unit.teacher != request.user:
        return Response({'error': 'This unit is already assigned to another teacher'}, status=403)

    unit.teacher = request.user
    unit.save()
    return Response(UnitSerializer(unit).data)


# ── UNCLAIM A UNIT ──
# Allows a teacher to remove themselves from a unit they currently teach.
# Returns 403 if the requesting user is not the current teacher of the unit.
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unclaim_unit(request, unit_id):
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found'}, status=404)

    # Only the teacher currently assigned to this unit can unclaim it
    if unit.teacher != request.user:
        return Response({'error': 'You do not teach this unit'}, status=403)

    unit.teacher = None
    unit.save()
    return Response(UnitSerializer(unit).data)    