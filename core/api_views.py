from rest_framework import viewsets, permissions
from .models import ClassRoom, Student, Attendance
from .serializers import ClassRoomSerializer, StudentSerializer, AttendanceSerializer


class IsAdminOrTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return user.is_authenticated
        return user.is_authenticated and (user.is_admin_role or user.is_teacher_role)


class ClassRoomViewSet(viewsets.ModelViewSet):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [IsAdminOrTeacher]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'classroom').all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        qs = super().get_queryset()
        classroom_id = self.request.query_params.get('classroom')
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        return qs


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student__user', 'classroom').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_student_role:
            qs = qs.filter(student__user=user)
        elif user.is_teacher_role and not user.is_admin_role:
            qs = qs.filter(classroom__teacher=user)

        student_id = self.request.query_params.get('student')
        classroom_id = self.request.query_params.get('classroom')
        date = self.request.query_params.get('date')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        if date:
            qs = qs.filter(date=date)
        return qs

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)