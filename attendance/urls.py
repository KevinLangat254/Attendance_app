from django.urls import path, include
from rest_framework.routers import DefaultRouter

from attendance.views.auth_views import webauthn_delete_credential, webauthn_list_credentials
from . import views

router = DefaultRouter()
router.register(r"users",       views.UserViewSet,       basename="user")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"attendance",  views.AttendanceViewSet, basename="attendance")
router.register(r"programs",    views.ProgramViewSet)
router.register(r"units",       views.UnitViewSet)
router.register(r"sessions",    views.SessionViewSet)

urlpatterns = [
    # Custom endpoints — must be before router.urls
    path('units/<int:unit_id>/claim/',   views.claim_unit,   name='claim-unit'),
    path('units/<int:unit_id>/unclaim/', views.unclaim_unit, name='unclaim-unit'),
    path('mark-attendance/', views.MarkAttendanceView.as_view()),
    path('upload-avatar/', views.upload_avatar, name='upload-avatar'),

    # ── WebAuthn Registration (Linking a phone) ──
    path('webauthn/register/begin/', views.webauthn_register_begin, name='webauthn-register-begin'),
    path('webauthn/register/complete/', views.webauthn_register_complete, name='webauthn-register-complete'),

    # ── WebAuthn Authentication (Verifying identity) ──
    path('webauthn/login/begin/', views.webauthn_login_begin, name='webauthn-login-begin'),
    path('webauthn/login/complete/', views.webauthn_login_complete, name='webauthn-login-complete'),

    # ── WebAuthn — Manage Devices ──
    path('webauthn/credentials/', webauthn_list_credentials, name='webauthn-list-credentials'),
    path('webauthn/credentials/delete/<int:credential_id>/', webauthn_delete_credential, name='webauthn-delete-credential'),

    # ── Administrative Override ──
    path('webauthn/reset-student/<int:student_id>/', views.reset_student_biometric, name='webauthn-reset'),

    # Router URLs
    path('', include(router.urls)),
]