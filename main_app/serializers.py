from rest_framework import serializers
from main_app.models import *


class AdminGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class AdminSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'


class AdminCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class AdminTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class AdminStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class AdminStudentSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSemester
        fields = '__all__'


class AdminClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class AdminClassStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassStudent
        fields = '__all__'


class AdminClassStudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassStudentAttendance
        fields = '__all__'
