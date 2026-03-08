from rest_framework import serializers
from .models import User, Program, Enrollment, Unit, Session, Attendance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ["id", "username", "email", "first_name", "last_name",
                  "password", "is_teacher", "is_student"]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user     = User(**validated_data)
        user.set_password(password)  # ← hashes the password correctly
        user.save()
        return user


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "course", "department", "duration_years", "faculty"]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "student", "program", "date_enrolled", "is_active"]

    def validate_student(self, user):
        if not user.is_student:
            raise serializers.ValidationError("This user is not a student.")
        return user


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name", "unit_code", "semester", "year","program", "teacher"]

    def validate_teacher(self, user):
        if not user.is_teacher:
            raise serializers.ValidationError("This user is not a teacher.")
        return user


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "unit", "start_time", "end_time", "latitude", "longitude"]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "student", "session", "timestamp", "status"]

    def validate_student(self, user):
        if not user.is_student:
            raise serializers.ValidationError("This user is not a student.")
        return user