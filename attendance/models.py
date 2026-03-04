from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom user model supporting both Teacher and Student roles.
    A single user can hold both roles simultaneously.
    """
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Program(models.Model):

    class Faculty(models.TextChoices):
        FOCIT  = "FoCIT",  "Faculty of Computing and Information Technology"
        FAMECO = "FAMECO", "Faculty of Media and Economics"
        FOET   = "FoET",   "Faculty of Engineering and Technology"
        FOBE   = "FoBE",   "Faculty of Business and Economics"
        FOST   = "FoST",   "Faculty of Science and Technology"
        FOSST  = "FoSST",  "Faculty of Social Sciences and Technology"

    course     = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    duration_years = models.PositiveSmallIntegerField(default=4)
    faculty    = models.CharField(
        max_length=10,
        choices=Faculty.choices,
        default=Faculty.FOCIT,
    )

    class Meta:
        ordering = ["faculty", "course"]
        unique_together = ("course", "faculty")  # prevents duplicate program names within the same faculty

    def __str__(self):
        return f"{self.course} ({self.get_faculty_display()})"

class Enrollment(models.Model):
    """
    Junction table linking a Student (User) to a Program.
    Maps to the ENROLLMENT entity in the ERD (has_students / enrolled_as).
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"is_student": True},
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    date_enrolled = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # A student can only be enrolled in a program once
        unique_together = ("student", "program")
        ordering = ["-date_enrolled"]

    def __str__(self):
        return f"{self.student.username} → {self.program.course}"


class Unit(models.Model):
    name      = models.CharField(max_length=255)
    unit_code = models.CharField(max_length=20, unique=True)
    year = models.PositiveSmallIntegerField(default=1)
    semester  = models.PositiveSmallIntegerField()
    program   = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="units")
    teacher   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="taught_units",
                                  limit_choices_to={"is_teacher": True})

    def clean(self):
        # Validate year does not exceed program duration
        if self.year > self.program.duration_years:
            raise ValidationError(
                f"Year {self.year} exceeds the duration of "
                f"'{self.program.course}' ({self.program.duration_years} years)."
            )
        # Validate semester is consistent with year (each year has 2 semesters)
        expected_semesters = [self.year * 2 - 1, self.year * 2]
        if self.semester not in expected_semesters:
            raise ValidationError(
                f"Semester {self.semester} is inconsistent with Year {self.year}. "
                f"Expected {expected_semesters[0]} or {expected_semesters[1]}."
            )

    class Meta:
        ordering = ["year", "semester", "unit_code"]

    def __str__(self):
        return f"[{self.unit_code}] {self.name} — Year {self.year} Sem {self.semester}"
    """
    A course/unit within a Program, taught by a Teacher.
    Maps to the UNIT entity in the ERD.
    """
    name = models.CharField(max_length=255)
    unit_code = models.CharField(max_length=20, unique=True)
    semester = models.PositiveSmallIntegerField()
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="units",
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="taught_units",
        limit_choices_to={"is_teacher": True},
    )

    class Meta:
        ordering = ["semester", "unit_code"]

    def __str__(self):
        return f"[{self.unit_code}] {self.name}"


class Session(models.Model):
    """
    A single scheduled class occurrence for a Unit.
    Stores the geofence anchor (lat/long) for location-based check-in.
    Maps to the SESSION entity in the ERD.
    """
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Geofencing anchor point
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.unit.unit_code} | {self.start_time:%Y-%m-%d %H:%M}"


class Attendance(models.Model):
    """
    Records whether a student attended a specific Session.
    Maps to the ATTENDANCE entity in the ERD.
    """

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        EXCUSED = "EXCUSED", "Excused"

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        limit_choices_to={"is_student": True},
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ABSENT,
    )

    class Meta:
        # A student can only have one attendance record per session
        unique_together = ("student", "session")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.student.username} | {self.session} | {self.status}"