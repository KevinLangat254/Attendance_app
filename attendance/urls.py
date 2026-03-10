from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"users",       views.UserViewSet)
router.register(r"programs",    views.ProgramViewSet)
router.register(r"enrollments", views.EnrollmentViewSet)
router.register(r"units",       views.UnitViewSet)
router.register(r"sessions",    views.SessionViewSet)
router.register(r"attendance",  views.AttendanceViewSet)

urlpatterns = [
    # Custom endpoints — must be before router.urls
    path('api/units/<int:unit_id>/claim/',   views.claim_unit,   name='claim-unit'),
    path('api/units/<int:unit_id>/unclaim/', views.unclaim_unit, name='unclaim-unit'),
    path('api/mark-attendance/', views.MarkAttendanceView.as_view()),

    # Router URLs
    path('api/', include(router.urls)),
]