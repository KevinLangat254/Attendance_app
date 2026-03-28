from rest_framework import serializers
from .models import User, Program, Enrollment, Unit, Session, Attendance

class UserSerializer(serializers.ModelSerializer):
    # required=False so PATCH requests without a password don't fail
    password    = serializers.CharField(write_only=True, required=False)
    avatar_url  = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ["id", "username", "email", "first_name", "last_name",
                  "password", "is_lecturer", "is_student", "avatar_url"]

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def create(self, validated_data):
        password = validated_data.pop('password')
        user     = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "course", "department", "duration_years", "faculty"]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'program', 'date_enrolled',
          'is_active', 'current_year', 'current_semester']

    def validate_student(self, user):
        if not user.is_student:
            raise serializers.ValidationError("This user is not a student.")
        return user


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name", "unit_code", "semester", "year","program", "lecturer"]

    def validate_lecturer(self, user):
        if not user.is_lecturer:
            raise serializers.ValidationError("This user is not a lecturer.")
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