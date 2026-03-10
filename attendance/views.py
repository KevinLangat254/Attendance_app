import math
from django.utils        import timezone
from rest_framework      import viewsets, status
from rest_framework.views       import APIView
from rest_framework.decorators  import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response    import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Program, Enrollment, Unit, Session, Attendance
from .serializers import (
    UserSerializer, ProgramSerializer, EnrollmentSerializer,
    UnitSerializer, SessionSerializer, AttendanceSerializer,
)


# ════════════════════════════════════════════════════════════
#  VIEWSETS
# ════════════════════════════════════════════════════════════

class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Registration is public — everything else requires a token
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


class ProgramViewSet(viewsets.ModelViewSet):
    # Public — needed by the register page dropdown before the user has a token
    queryset           = Program.objects.all().order_by('faculty', 'course')
    serializer_class   = ProgramSerializer
    permission_classes = [AllowAny]


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset         = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['student', 'program']


class UnitViewSet(viewsets.ModelViewSet):
    queryset         = Unit.objects.all()
    serializer_class = UnitSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset         = Session.objects.all()
    serializer_class = SessionSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset         = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['student', 'session']


# ════════════════════════════════════════════════════════════
#  UNIT CLAIM / UNCLAIM
# ════════════════════════════════════════════════════════════

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def claim_unit(request, unit_id):
    """
    Assign the requesting teacher as the teacher of a unit.
    - Returns 404 if the unit does not exist.
    - Returns 403 if the unit is already assigned to a different teacher.
    """
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Prevent overwriting another teacher's assignment
    if unit.teacher is not None and unit.teacher != request.user:
        return Response(
            {'error': 'This unit is already assigned to another teacher.'},
            status=status.HTTP_403_FORBIDDEN
        )

    unit.teacher = request.user
    unit.save()
    return Response(UnitSerializer(unit).data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unclaim_unit(request, unit_id):
    """
    Remove the requesting teacher from a unit they currently teach.
    - Returns 404 if the unit does not exist.
    - Returns 403 if the requesting user is not the assigned teacher.
    """
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found.'}, status=status.HTTP_404_NOT_FOUND)

    if unit.teacher != request.user:
        return Response(
            {'error': 'You do not teach this unit.'},
            status=status.HTTP_403_FORBIDDEN
        )

    unit.teacher = None
    unit.save()
    return Response(UnitSerializer(unit).data, status=status.HTTP_200_OK)


# ════════════════════════════════════════════════════════════
#  GEOFENCED ATTENDANCE MARKING
# ════════════════════════════════════════════════════════════

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the straight-line distance in metres between two
    GPS coordinates using the Haversine formula.
    """
    R    = 6371000  # Earth's mean radius in metres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class MarkAttendanceView(APIView):
    """
    POST /api/mark-attendance/

    Body:
        session_id  (int)   — ID of the active session
        latitude    (float) — student's current GPS latitude
        longitude   (float) — student's current GPS longitude

    Checks (in order):
        1. All required fields are present
        2. Session exists
        3. Session is currently active (now is between start and end time)
        4. Student has not already marked attendance for this session
        5. Student is within the session's geofence radius

    Returns:
        201  { message, distance_metres, attendance_id }
        400  { error }   — missing fields / inactive session / duplicate
        403  { error, distance_metres, allowed_radius }  — outside geofence
        404  { error }   — session not found
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        latitude   = request.data.get('latitude')
        longitude  = request.data.get('longitude')

        # ── 1. Validate required fields ──
        if not all([session_id, latitude is not None, longitude is not None]):
            return Response(
                {'error': 'session_id, latitude and longitude are all required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── 2. Check the session exists ──
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── 3. Check the session is currently active ──
        now = timezone.now()
        if not (session.start_time <= now <= session.end_time):
            return Response(
                {'error': 'This session is not currently active.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── 4. Check for duplicate attendance ──
        if Attendance.objects.filter(student=request.user, session=session).exists():
            return Response(
                {'error': 'You have already marked attendance for this session.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── 5. Geofence check ──
        distance       = haversine(
            float(latitude),
            float(longitude),
            float(session.latitude),
            float(session.longitude),
        )
        allowed_radius = session.radius_metres or 50

        if distance > allowed_radius:
            return Response(
                {
                    'error':           'You are outside the geofence.',
                    'distance_metres': round(distance),
                    'allowed_radius':  allowed_radius,
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ── 6. All checks passed — create the attendance record ──
        attendance = Attendance.objects.create(
            student=request.user,
            session=session,
            status='PRESENT',
        )

        return Response(
            {
                'message':         'Attendance marked successfully.',
                'distance_metres': round(distance),
                'attendance_id':   attendance.id,
            },
            status=status.HTTP_201_CREATED
        )
