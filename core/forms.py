from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Student, Teacher, ClassRoom, Attendance


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'section', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role=User.ROLE_TEACHER)


class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    roll_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    classroom = forms.ModelChoiceField(queryset=ClassRoom.objects.all(),
                                        widget=forms.Select(attrs={'class': 'form-select'}))
    date_of_birth = forms.DateField(required=False,
                                     widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number']
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("A student with this roll number already exists.")
        return roll_number

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=User.ROLE_STUDENT,
        )
        student = Student.objects.create(
            user=user,
            roll_number=data['roll_number'],
            classroom=data['classroom'],
            date_of_birth=data.get('date_of_birth'),
        )
        return student


class TeacherRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    employee_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=User.ROLE_TEACHER,
        )
        teacher = Teacher.objects.create(
            user=user,
            employee_id=data['employee_id'],
            department=data.get('department', ''),
        )
        return teacher


class AttendanceDateClassForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=ClassRoom.objects.all(),
                                        widget=forms.Select(attrs={'class': 'form-select'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))


class AttendanceReportFilterForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=ClassRoom.objects.all(), required=False,
                                        widget=forms.Select(attrs={'class': 'form-select'}))
    start_date = forms.DateField(required=False,
                                  widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    end_date = forms.DateField(required=False,
                                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))