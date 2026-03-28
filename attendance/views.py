import math
from django.utils        import timezone
from rest_framework      import viewsets, status
from rest_framework.views       import APIView
from rest_framework.decorators  import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response    import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Program, Enrollment, Unit, Session, Attendance
from .serializers import (
    UserSerializer, ProgramSerializer, EnrollmentSerializer,
    UnitSerializer, SessionSerializer, AttendanceSerializer,
)
from rest_framework.parsers import MultiPartParser, FormParser


# ════════════════════════════════════════════════════════════
#  VIEWSETS
# ════════════════════════════════════════════════════════════

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_permissions(self):
        # Registration is public — everything else requires a token
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Lecturers and admins can see all users (needed for dashboards)
        if user.is_staff or user.is_lecturer:
            return User.objects.all()
        # Students only see themselves
        return User.objects.filter(id=user.id)

    def get_serializer_context(self):
        # Pass request into serializer so avatar_url can build absolute URLs
        return {'request': self.request}

    def update(self, request, *args, **kwargs):
        # Users can only update their own profile; admins can update anyone
        instance = self.get_object()
        if instance != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only update your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only admins can delete user accounts
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can delete users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class ProgramViewSet(viewsets.ModelViewSet):
    # Public — needed by the register page dropdown before the user has a token
    queryset           = Program.objects.all().order_by('faculty', 'course')
    serializer_class   = ProgramSerializer
    permission_classes = [AllowAny]


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['student', 'program']

    def get_queryset(self):
        user = self.request.user
        # Lecturers and admins see all enrollments
        if user.is_staff or user.is_lecturer:
            return Enrollment.objects.all()
        # Students only see their own enrollment
        return Enrollment.objects.filter(student=user)

    def update(self, request, *args, **kwargs):
        # Students can only modify their own enrollment; admins can modify any
        instance = self.get_object()
        if instance.student != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only modify your own enrollment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only admins can delete enrollments
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can delete enrollments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class UnitViewSet(viewsets.ModelViewSet):
    queryset         = Unit.objects.all()
    serializer_class = UnitSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset         = Session.objects.all()
    serializer_class = SessionSerializer

    def create(self, request, *args, **kwargs):
        # Only lecturers and admins can create sessions
        if not (request.user.is_lecturer or request.user.is_staff):
            return Response(
                {'error': 'Only lecturers can create sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Only the lecturer who owns the unit can update the session
        session = self.get_object()
        if session.unit.lecturer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only modify sessions for units you teach.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only the lecturer who owns the unit or an admin can delete the session
        session = self.get_object()
        if session.unit.lecturer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only delete sessions for units you teach.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['student', 'session']

    def get_queryset(self):
        user = self.request.user
        # Lecturers and admins see all attendance records
        if user.is_staff or user.is_lecturer:
            return Attendance.objects.all()
        # Students only see their own records
        return Attendance.objects.filter(student=user)

    def update(self, request, *args, **kwargs):
        # Only lecturers and admins can modify attendance records
        # Students cannot change their own status (e.g. ABSENT → PRESENT)
        if not (request.user.is_staff or request.user.is_lecturer):
            return Response(
                {'error': 'Only lecturers can modify attendance records.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only admins can delete attendance records
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can delete attendance records.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


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
    - Returns 403 if the requesting user is not a teacher.
    """
    if not (request.user.is_lecturer or request.user.is_staff):
        return Response(
            {'error': 'Only lecturers can claim units.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Prevent overwriting another lecturer's assignment
    if unit.lecturer is not None and unit.lecturer != request.user:
        return Response(
            {'error': 'This unit is already assigned to another lecturer.'},
            status=status.HTTP_403_FORBIDDEN
        )

    unit.lecturer = request.user
    unit.save()
    return Response(UnitSerializer(unit).data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unclaim_unit(request, unit_id):
    """
    Remove the requesting lecturer from a unit they currently teach.
    - Returns 404 if the unit does not exist.
    - Returns 403 if the requesting user is not the assigned lecturer.
    """
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found.'}, status=status.HTTP_404_NOT_FOUND)

    if unit.lecturer != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You are not the lecturer for this unit.'},
            status=status.HTTP_403_FORBIDDEN
        )

    unit.lecturer = None
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
        # Only students can mark attendance
        if not (request.user.is_student or request.user.is_staff):
            return Response(
                {'error': 'Only students can mark attendance.'},
                status=status.HTTP_403_FORBIDDEN
            )

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
        distance = haversine(
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


# ════════════════════════════════════════════════════════════
#  AVATAR UPLOAD
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    """
    POST /api/upload-avatar/

    Uploads a profile photo for the currently authenticated user.
    The old avatar file is deleted from disk before saving the new one.
    Returns the absolute URL of the new avatar.
    """
    user = request.user

    if 'avatar' not in request.FILES:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Delete old avatar file from disk before saving new one
    if user.avatar:
        user.avatar.delete(save=False)

    user.avatar = request.FILES['avatar']
    user.save()

    avatar_url = request.build_absolute_uri(user.avatar.url)
    return Response({'avatar_url': avatar_url}, status=status.HTTP_200_OK)
