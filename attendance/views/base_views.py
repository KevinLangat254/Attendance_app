from rest_framework             import viewsets, status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response    import Response
from rest_framework.decorators  import api_view, permission_classes, parser_classes, action
from rest_framework.parsers     import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from ..models import User, Program, Enrollment, Unit, Session, Attendance, PasswordResetToken
from ..serializers import (
    UserSerializer,
    ProgramSerializer,
    EnrollmentSerializer,
    UnitSerializer,
    SessionSerializer,
    AttendanceSerializer,
)
from rest_framework.authentication import TokenAuthentication


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
    
    # @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    # def me(self):
    #     serializer = self.get_serializer(self.request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # Users can only update their own profile; admins can update anyone
        instance = self.get_object()
        if instance != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only update your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        kwargs['partial'] = True
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
        # OPTIMIZATION: select_related performs an SQL JOIN
        queryset = Enrollment.objects.select_related('student', 'program').all()
        # Lecturers and admins see all enrollments
        if user.is_staff or user.is_lecturer:
            return queryset
        # Students only see their own enrollment
        return queryset.filter(student=user)

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
    serializer_class = UnitSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Unit.objects.select_related('lecturer', 'program').all()
        
        # Capture filters from the URL parameters
        program  = self.request.query_params.get('program')
        year     = self.request.query_params.get('year')
        semester = self.request.query_params.get('semester')

        # Apply database-level filters if parameters are provided
        if program:
            queryset = queryset.filter(program_id=program)
        if year:
            queryset = queryset.filter(year=year)
        if semester:
            queryset = queryset.filter(semester=semester)
            
        return queryset

# ════════════════════════════════════════════════════════════
#  SESSIONS
# ════════════════════════════════════════════════════════════

class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Session.objects.select_related('unit').all()

        # 1. If the user is a Lecturer (and not a superuser/admin)
        if user.is_lecturer and not user.is_staff:
            # Filter sessions where the related unit's lecturer is the current user
            return queryset.filter(unit__lecturer=user)
        
        unit_ids = self.request.query_params.getlist('unit') # Supports ?unit=1&unit=2

        if unit_ids:
            queryset = queryset.filter(unit_id__in=unit_ids)
            
        return queryset
    
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
        queryset = Attendance.objects.select_related('session__unit', 'student').all()
        # Lecturers and admins see all attendance records
        if user.is_staff or user.is_lecturer:
            return queryset
        # Students only see their own records
        return queryset.filter(student=user)

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


# ════════════════════════════════════════════════════════════
#  FORGOT PASSWORD — EMAIL RESET
# ════════════════════════════════════════════════════════════

import secrets
from django.core.mail   import send_mail
from django.conf        import settings
from django.utils       import timezone
from datetime           import timedelta
from ..models           import PasswordResetToken


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    POST /api/auth/forgot-password/

    Accepts an email address and sends a password reset link
    if an account with that email exists.

    We always return 200 regardless of whether the email exists
    to prevent email enumeration attacks.

    Auth required: No

    Request body:
        email (str)

    Returns:
        200  { message }
        400  { error }  — email field missing
    """
    email = request.data.get('email', '').strip()

    if not email:
        return Response(
            {'error': 'Email address is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Always return success to prevent email enumeration
    # (attacker cannot tell if an email exists in the system)
    response = Response(
        {'message': 'If an account with that email exists, a reset link has been sent.'},
        status=status.HTTP_200_OK
    )

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return response

    # Delete any existing unused tokens for this user
    PasswordResetToken.objects.filter(user=user).delete()

    # Generate a secure random token
    token = secrets.token_urlsafe(32)

    # Save token — expires in 30 minutes
    PasswordResetToken.objects.create(
        user       = user,
        token      = token,
        expires_at = timezone.now() + timedelta(minutes=30),
    )

    # Build reset URL — points to the frontend reset page
    reset_url = f"{request.scheme}://{request.get_host()}/reset-password.html?token={token}"

    # Send email
    try:
        send_mail(
            subject    = 'Uni Attendance — Password Reset',
            message    = (
                f"Hello {user.first_name or user.username},\n\n"
                f"You requested a password reset for your Uni Attendance account.\n\n"
                f"Click the link below to reset your password:\n{reset_url}\n\n"
                f"This link expires in 30 minutes.\n\n"
                f"If you did not request this, ignore this email — your password will not change."
            ),
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [user.email],
            fail_silently  = False,
        )
    except Exception:
        # Email failed to send — still return success to prevent enumeration
        # Log the error server-side for admin awareness
        pass

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    POST /api/auth/reset-password/

    Validates the reset token and sets a new password.

    Auth required: No

    Request body:
        token        (str) — the token from the reset email link
        new_password (str) — the new password (min 8 characters)

    Returns:
        200  { message }
        400  { error }  — invalid/expired token or missing fields
    """
    token        = request.data.get('token', '').strip()
    new_password = request.data.get('new_password', '').strip()

    if not token or not new_password:
        return Response(
            {'error': 'Token and new password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired reset link. Please request a new one.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check token has not expired
    if reset_token.expires_at < timezone.now():
        reset_token.delete()
        return Response(
            {'error': 'This reset link has expired. Please request a new one.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Set the new password
    user = reset_token.user
    user.set_password(new_password)
    user.save()

    # Delete the used token — single use only
    reset_token.delete()

    return Response(
        {'message': 'Password reset successfully. You can now log in with your new password.'},
        status=status.HTTP_200_OK
    )
