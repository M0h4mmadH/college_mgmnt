from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db import models


class CustomStudentManager(UserManager):

    def _create_user(self, username, password, **extra_fields):
        user = Student(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        raise TypeError('Cannot create Student super user')


class CustomTeacherManager(UserManager):

    def _create_user(self, username, password, **extra_fields):
        user = Teacher(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        raise TypeError('Cannot create Teacher super user')


class Group(models.Model):
    name = models.CharField(max_length=50, primary_key=True)


class Semester(models.Model):
    entrant_date = models.DateField(db_index=True, null=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, db_index=True)
    start = models.DateField(db_index=True)
    add_drop_start = models.DateField()
    add_drop_end = models.DateField()

    def __str__(self):
        semester_id = f"{self.group}_{self.entrant_date}_{str(self.start)}"
        return f"Semester {semester_id}\nAdd/Drop From {str(self.add_drop_start)} to {str(self.add_drop_end)}"


class Course(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    units = models.IntegerField(default=1)


class Teacher(User):
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    current_semesters = models.ManyToManyField(Semester, null=True, blank=True)

    GENDER = [("M", "Male"), ("F", "Female")]
    gender = models.CharField(max_length=1, choices=GENDER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS = ["username"]
    objects = CustomTeacherManager()

    def __str__(self):
        return self.last_name + " " + self.first_name


class Student(User):
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    current_semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING, null=True, blank=True)

    GENDER = [("M", "Male"), ("F", "Female")]
    gender = models.CharField(max_length=1, choices=GENDER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS = ["username"]
    objects = CustomStudentManager()

    def __str__(self):
        return self.last_name + " " + self.first_name


class Admin(UserAdmin):
    pass


class StudentSemester(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, db_index=True)
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING, db_index=True)
    min_units = models.IntegerField(default=13)
    max_units = models.IntegerField(default=20)
    chosen_units = models.IntegerField(default=None, null=True, blank=True)


class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    class_start_time = models.TimeField(help_text="HH:mm", null=False, blank=False, db_index=True)


class ClassStudent(models.Model):
    course_semester = models.ForeignKey(Class, on_delete=models.DO_NOTHING, null=False, db_index=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, null=False, db_index=True)
    midterm_grade = models.IntegerField(default=None, null=True, blank=True)
    final_grade = models.IntegerField(default=None, null=True, blank=True)


class ClassStudentAttendance(models.Model):
    ATTENDANCE = [("P", "Present"), ("A", "Absent"), ("U", "Unknown")]
    date = models.DateField(null=False, blank=False, db_index=True)
    course_semester = models.ForeignKey(Class, on_delete=models.DO_NOTHING, null=False, db_index=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, null=False, db_index=True)
    attendance = models.CharField(max_length=1, choices=ATTENDANCE, default="U")
