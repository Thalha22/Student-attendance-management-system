from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.urls import reverse_lazy

from .forms import (
    LoginForm, ClassRoomForm, StudentRegistrationForm, TeacherRegistrationForm,
    AttendanceDateClassForm, AttendanceReportFilterForm
)
from .models import User, ClassRoom, Student, Teacher, Attendance


def is_admin(user):
    return user.is_authenticated and user.is_admin_role


def is_teacher(user):
    return user.is_authenticated and (user.is_teacher_role or user.is_admin_role)


def is_student(user):
    return user.is_authenticated and user.is_student_role


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse_lazy('dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user

    if user.is_admin_role:
        context = {
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_classes': ClassRoom.objects.count(),
            'today_attendance': Attendance.objects.filter(date=_today()).count(),
        }
        return render(request, 'core/dashboard_admin.html', context)

    if user.is_teacher_role:
        classes = ClassRoom.objects.filter(teacher=user)
        context = {'classes': classes}
        return render(request, 'core/dashboard_teacher.html', context)

    student = get_object_or_404(Student, user=user)
    records = student.attendance_records.all()[:10]
    context = {
        'student': student,
        'records': records,
        'percentage': student.attendance_percentage(),
    }
    return render(request, 'core/dashboard_student.html', context)


def _today():
    from django.utils import timezone
    return timezone.localdate()


@login_required
@user_passes_test(is_admin)
def class_list(request):
    classes = ClassRoom.objects.select_related('teacher').annotate(student_count=Count('students'))
    return render(request, 'core/class_list.html', {'classes': classes})


@login_required
@user_passes_test(is_admin)
def class_add(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class created successfully.")
            return redirect('class_list')
    else:
        form = ClassRoomForm()
    return render(request, 'core/class_form.html', {'form': form, 'title': 'Add Class'})


@login_required
@user_passes_test(is_admin)
def class_edit(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, "Class updated successfully.")
            return redirect('class_list')
    else:
        form = ClassRoomForm(instance=classroom)
    return render(request, 'core/class_form.html', {'form': form, 'title': 'Edit Class'})


@login_required
@user_passes_test(is_admin)
def class_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, "Class deleted.")
        return redirect('class_list')
    return render(request, 'core/confirm_delete.html', {'object': classroom, 'type': 'Class'})


@login_required
@user_passes_test(is_admin)
def student_list(request):
    students = Student.objects.select_related('user', 'classroom').all()
    query = request.GET.get('q')
    if query:
        students = students.filter(
            Q(roll_number__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    return render(request, 'core/student_list.html', {'students': students, 'query': query or ''})


@login_required
@user_passes_test(is_admin)
def student_add(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student registered successfully.")
            return redirect('student_list')
    else:
        form = StudentRegistrationForm()
    return render(request, 'core/student_form.html', {'form': form, 'title': 'Add Student'})


@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()
        messages.success(request, "Student removed.")
        return redirect('student_list')
    return render(request, 'core/confirm_delete.html', {'object': student, 'type': 'Student'})


@login_required
@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    records = student.attendance_records.select_related('classroom').all()
    return render(request, 'core/student_detail.html', {
        'student': student, 'records': records, 'percentage': student.attendance_percentage()
    })


@login_required
@user_passes_test(is_admin)
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').all()
    return render(request, 'core/teacher_list.html', {'teachers': teachers})


@login_required
@user_passes_test(is_admin)
def teacher_add(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher registered successfully.")
            return redirect('teacher_list')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'core/teacher_form.html', {'form': form, 'title': 'Add Teacher'})


@login_required
@user_passes_test(is_admin)
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.user.delete()
        messages.success(request, "Teacher removed.")
        return redirect('teacher_list')
    return render(request, 'core/confirm_delete.html', {'object': teacher, 'type': 'Teacher'})


@login_required
@user_passes_test(is_teacher)
def mark_attendance_select(request):
    if request.method == 'POST':
        form = AttendanceDateClassForm(request.POST)
        if form.is_valid():
            classroom = form.cleaned_data['classroom']
            date = form.cleaned_data['date']
            return redirect('mark_attendance', classroom_id=classroom.id, date=date)
    else:
        form = AttendanceDateClassForm()

    if request.user.is_teacher_role and not request.user.is_admin_role:
        form.fields['classroom'].queryset = ClassRoom.objects.filter(teacher=request.user)

    return render(request, 'core/mark_attendance_select.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def mark_attendance(request, classroom_id, date):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    students = classroom.students.select_related('user').all()

    existing = {
        rec.student_id: rec
        for rec in Attendance.objects.filter(classroom=classroom, date=date)
    }

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}', Attendance.STATUS_ABSENT)
            remarks = request.POST.get(f'remarks_{student.id}', '')
            record, created = Attendance.objects.update_or_create(
                student=student, classroom=classroom, date=date,
                defaults={'status': status, 'remarks': remarks, 'marked_by': request.user}
            )
        messages.success(request, f"Attendance saved for {classroom} on {date}.")
        return redirect('attendance_report')

    rows = [
        {'student': s, 'current_status': existing[s.id].status if s.id in existing else Attendance.STATUS_PRESENT}
        for s in students
    ]

    return render(request, 'core/mark_attendance.html', {
        'classroom': classroom, 'date': date, 'rows': rows,
        'status_choices': Attendance.STATUS_CHOICES,
    })


@login_required
def attendance_report(request):
    user = request.user
    form = AttendanceReportFilterForm(request.GET or None)
    records = Attendance.objects.select_related('student__user', 'classroom')

    if user.is_student_role:
        student = get_object_or_404(Student, user=user)
        records = records.filter(student=student)
    elif user.is_teacher_role and not user.is_admin_role:
        records = records.filter(classroom__teacher=user)

    if form.is_valid():
        if form.cleaned_data.get('classroom'):
            records = records.filter(classroom=form.cleaned_data['classroom'])
        if form.cleaned_data.get('start_date'):
            records = records.filter(date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            records = records.filter(date__lte=form.cleaned_data['end_date'])

    records = records.order_by('-date')[:500]

    return render(request, 'core/attendance_report.html', {'form': form, 'records': records})