from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClassRoom, Student, Teacher, Attendance


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'phone_number')}),
    )


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'teacher')
    search_fields = ('name', 'section')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'classroom', 'attendance_percentage')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name')
    list_filter = ('classroom',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'date', 'status', 'marked_by')
    list_filter = ('status', 'classroom', 'date')
    search_fields = ('student__roll_number',)
    date_hierarchy = 'date'