from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

    # Router URLs
    path('', include(router.urls)),
]