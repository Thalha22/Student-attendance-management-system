from rest_framework import serializers
from .models import ClassRoom, Student, Teacher, Attendance, User


class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role']


class ClassRoomSerializer(serializers.ModelSerializer):
    teacher = UserMiniSerializer(read_only=True)

    class Meta:
        model = ClassRoom
        fields = ['id', 'name', 'section', 'teacher']


class StudentSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    classroom = ClassRoomSerializer(read_only=True)
    attendance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'user', 'classroom', 'date_of_birth', 'attendance_percentage']

    def get_attendance_percentage(self, obj):
        return obj.attendance_percentage()


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    classroom_name = serializers.CharField(source='classroom.__str__', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'roll_number', 'classroom', 'classroom_name',
            'date', 'status', 'remarks', 'marked_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['marked_by', 'created_at', 'updated_at']