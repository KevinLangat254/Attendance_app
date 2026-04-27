from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    # ── ViewSets ──
    UserViewSet,
    ProgramViewSet,
    EnrollmentViewSet,
    UnitViewSet,
    SessionViewSet,
    AttendanceViewSet,
    # ── Base views ──
    claim_unit,
    unclaim_unit,
    upload_avatar,
    # ── Attendance ──
    MarkAttendanceView,
    # ── WebAuthn ──
    webauthn_register_begin,
    webauthn_register_complete,
    webauthn_list_credentials,
    webauthn_delete_credential,
    reset_student_biometric,
    webauthn_attendance_begin,
    webauthn_attendance_complete,
)

router = DefaultRouter()
router.register(r'users',       UserViewSet,       basename='user')
router.register(r'programs',    ProgramViewSet)
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'units',       UnitViewSet)
router.register(r'sessions',    SessionViewSet)
router.register(r'attendance',  AttendanceViewSet, basename='attendance')

urlpatterns = [

    # ── Unit claim / unclaim ──
    path('units/<int:unit_id>/claim/',   claim_unit),
    path('units/<int:unit_id>/unclaim/', unclaim_unit),

    # ── Attendance marking ──
    path('mark-attendance/', MarkAttendanceView.as_view()),

    # ── Avatar upload ──
    path('upload-avatar/', upload_avatar),

    # ── WebAuthn — Biometric Registration ──
    path('webauthn/register/begin/',    webauthn_register_begin),
    path('webauthn/register/complete/', webauthn_register_complete),

    # ── WebAuthn — Manage Devices ──
    path('webauthn/credentials/',                            webauthn_list_credentials),
    path('webauthn/credentials/<int:credential_id>/delete/', webauthn_delete_credential),

    # ── WebAuthn — Lecturer Reset Student Biometric ──
    path('webauthn/reset/<int:student_id>/', reset_student_biometric),

    # ── WebAuthn — Attendance Biometric Verification ──
    path('webauthn/attendance/begin/',    webauthn_attendance_begin),
    path('webauthn/attendance/complete/', webauthn_attendance_complete),

    # ── Router URLs — must be last ──
    path('', include(router.urls)),
]
