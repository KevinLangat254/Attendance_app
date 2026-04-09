from rest_framework             import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response    import Response
from rest_framework.decorators  import api_view, permission_classes, parser_classes
from rest_framework.parsers     import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from ..models import User, Program, Enrollment, Unit, Session, Attendance
from ..serializers import (
    UserSerializer,
    ProgramSerializer,
    EnrollmentSerializer,
    UnitSerializer,
    SessionSerializer,
    AttendanceSerializer,
)


# ════════════════════════════════════════════════════════════
#  USERS
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


# ════════════════════════════════════════════════════════════
#  PROGRAMS
# ════════════════════════════════════════════════════════════

class ProgramViewSet(viewsets.ModelViewSet):
    # Public — needed by the register page dropdown before the user has a token
    queryset           = Program.objects.all().order_by('faculty', 'course')
    serializer_class   = ProgramSerializer
    permission_classes = [AllowAny]


# ════════════════════════════════════════════════════════════
#  ENROLLMENTS
# ════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════
#  UNITS
# ════════════════════════════════════════════════════════════

class UnitViewSet(viewsets.ModelViewSet):
    queryset         = Unit.objects.all()
    serializer_class = UnitSerializer


# ════════════════════════════════════════════════════════════
#  SESSIONS
# ════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════
#  ATTENDANCE
# ════════════════════════════════════════════════════════════

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
    PATCH /api/units/{id}/claim/

    Assigns the requesting lecturer as the lecturer of a unit.
    Returns 403 if the unit is already claimed by another lecturer.
    Returns 403 if the requesting user is not a lecturer.
    Returns 404 if the unit does not exist.
    """
    if not (request.user.is_lecturer or request.user.is_staff):
        return Response(
            {'error': 'Only lecturers can claim units.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response(
            {'error': 'Unit not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

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
    PATCH /api/units/{id}/unclaim/

    Removes the requesting lecturer from a unit they currently teach.
    Returns 403 if the requesting user is not the assigned lecturer.
    Returns 404 if the unit does not exist.
    """
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response(
            {'error': 'Unit not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if unit.lecturer != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You are not the lecturer for this unit.'},
            status=status.HTTP_403_FORBIDDEN
        )

    unit.lecturer = None
    unit.save()
    return Response(UnitSerializer(unit).data, status=status.HTTP_200_OK)


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
        return Response(
            {'error': 'No file provided.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Delete old avatar file from disk before saving new one
    if user.avatar:
        user.avatar.delete(save=False)

    user.avatar = request.FILES['avatar']
    user.save()

    avatar_url = request.build_absolute_uri(user.avatar.url)
    return Response({'avatar_url': avatar_url}, status=status.HTTP_200_OK)
