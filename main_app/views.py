from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from main_app.serializers import *


class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        return self.serializer_class


class AdminGroupViewSet(AdminViewSet):
    queryset = Group.objects.all()
    serializer_class = AdminGroupSerializer


class AdminSemesterViewSet(AdminViewSet):
    queryset = Semester.objects.all()
    serializer_class = AdminSemesterSerializer


class AdminCourseViewSet(AdminViewSet):
    queryset = Course.objects.all()
    serializer_class = AdminCourseSerializer


class AdminTeacherViewSet(AdminViewSet):
    queryset = Teacher.objects.all()
    serializer_class = AdminTeacherSerializer


class AdminStudentViewSet(AdminViewSet):
    permission_classes = [IsAdminUser]
    queryset = Student.objects.all()
    serializer_class = AdminStudentSerializer


class AdminStudentSemesterViewSet(AdminViewSet):
    queryset = StudentSemester.objects.all()
    serializer_class = AdminStudentSemesterSerializer


class AdminClassViewSet(AdminViewSet):
    queryset = Class.objects.all()
    serializer_class = AdminClassSerializer


class AdminClassStudentViewSet(AdminViewSet):
    queryset = ClassStudent.objects.all()
    serializer_class = AdminClassStudentSerializer


class AdminClassStudentAttendanceViewSet(AdminViewSet):
    queryset = ClassStudentAttendance.objects.all()
    serializer_class = AdminClassStudentAttendanceSerializer
