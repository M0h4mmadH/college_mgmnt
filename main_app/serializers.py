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


class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'units']


class UserSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'entrant_date', 'start', 'add_drop_start', 'add_drop_end']


class UserClassSerializer(serializers.ModelSerializer):
    course = UserCourseSerializer()
    semester = UserSemesterSerializer()

    class Meta:
        model = Class
        fields = ['id', 'course', 'semester', 'class_start_time']


class UserClassStudentSerializer(serializers.ModelSerializer):
    course_semester = UserClassSerializer()

    class Meta:
        model = ClassStudent
        fields = ['id', 'course_semester', 'midterm_grade', 'final_grade']


class UpdateGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassStudent
        fields = ['midterm_grade', 'final_grade']

    def validate(self, data):
        if 'midterm_grade' in data and (data['midterm_grade'] < 0 or data['midterm_grade'] > 100):
            raise serializers.ValidationError("Midterm grade must be between 0 and 100.")
        if 'final_grade' in data and (data['final_grade'] < 0 or data['final_grade'] > 100):
            raise serializers.ValidationError("Final grade must be between 0 and 100.")
        return data


class StudentInClassSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    class Meta:
        model = ClassStudent
        fields = ['id', 'student', 'midterm_grade', 'final_grade']

    def get_student(self, obj):
        return {
            'id': obj.student.id,
            'username': obj.student.username,
            'first_name': obj.student.first_name,
            'last_name': obj.student.last_name,
            'email': obj.student.email
        }


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassStudentAttendance
        fields = ['student', 'attendance', 'date']

    def validate(self, data):
        course_semester = self.context['course_semester']
        student = data['student']

        if not ClassStudent.objects.filter(course_semester=course_semester, student=student).exists():
            raise serializers.ValidationError("This student is not enrolled in this class.")

        return data


class ClassChangeSerializer(serializers.Serializer):
    add_classes = serializers.ListField(child=serializers.IntegerField(), required=False)
    delete_classes = serializers.ListField(child=serializers.IntegerField(), required=False)