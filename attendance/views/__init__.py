# This file makes the views/ directory a Python package and
# exposes all views so urls.py can import from .views as before.

from .base_views import (
    UserViewSet,
    ProgramViewSet,
    EnrollmentViewSet,
    UnitViewSet,
    SessionViewSet,
    AttendanceViewSet,
    claim_unit,
    unclaim_unit,
    upload_avatar,
)

from .attendance_views import (
    MarkAttendanceView,
    haversine,
)

from .auth_views import (
    webauthn_register_begin,
    webauthn_register_complete,
    webauthn_login_begin,
    webauthn_login_complete,
    webauthn_list_credentials,
    
    reset_student_biometric,
)
# webauthn_delete_credential,