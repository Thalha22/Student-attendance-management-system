from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_TEACHER = 'TEACHER'
    ROLE_STUDENT = 'STUDENT'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_STUDENT, 'Student'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_teacher_role(self):
        return self.role == self.ROLE_TEACHER

    @property
    def is_student_role(self):
        return self.role == self.ROLE_STUDENT


class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=20, blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': User.ROLE_TEACHER},
        related_name='classes_taught'
    )

    class Meta:
        ordering = ['name', 'section']
        unique_together = ('name', 'section')

    def __str__(self):
        return f"{self.name} {self.section}".strip()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, related_name='students')
    date_of_birth = models.DateField(null=True, blank=True)
    admission_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name() or self.user.username}"

    def attendance_percentage(self):
        total = self.attendance_records.count()
        if total == 0:
            return 0
        present = self.attendance_records.filter(status=Attendance.STATUS_PRESENT).count()
        return round((present / total) * 100, 2)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"


class Attendance(models.Model):
    STATUS_PRESENT = 'PRESENT'
    STATUS_ABSENT = 'ABSENT'
    STATUS_LATE = 'LATE'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_LATE, 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_marked'
    )
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'classroom', 'date')

    def __str__(self):
        return f"{self.student.roll_number} - {self.date} - {self.status}"