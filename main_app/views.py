from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from .permissions import IsTeacher, IsStudent
from main_app.serializers import *
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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


class TeacherClassListView(generics.ListAPIView):
    # authentication_classes = []
    serializer_class = UserClassSerializer
    permission_classes = [IsTeacher]

    # permission_classes = []

    def get_queryset(self):
        teacher = self.request.user.teacher
        return Class.objects.filter(teacher=teacher)


class TeacherCurrentSemesterClassListView(generics.ListAPIView):
    serializer_class = UserClassSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        teacher = self.request.user.teacher
        semester_id = self.request.query_params.get('semester_id')
        queryset = Class.objects.filter(teacher=teacher)
        if semester_id:
            queryset = queryset.filter(semester__id=semester_id)
        return queryset

    def list(self, request, *args, **kwargs):
        semester_id = self.request.query_params.get('semester_id')
        if not semester_id:
            return Response({"error": "semester_id parameter is required"}, status=HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Get current semester class",
        operation_id="get_current_semester",
        manual_parameters=[
            openapi.Parameter(
                name='semester_id',
                in_=openapi.IN_QUERY,
                description="Semester id",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class StudentClassListView(generics.ListAPIView):
    serializer_class = UserClassStudentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        student = self.request.user.student
        return ClassStudent.objects.filter(student=student)


class StudentCurrentSemesterClassListView(generics.ListAPIView):
    serializer_class = UserClassStudentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        student = self.request.user.student
        semester_id = self.request.query_params.get('semester_id')
        queryset = ClassStudent.objects.filter(student=student)
        if semester_id:
            queryset = queryset.filter(course_semester__semester__id=semester_id)
        return queryset

    def list(self, request, *args, **kwargs):
        semester_id = self.request.query_params.get('semester_id')
        if not semester_id:
            return Response({"error": "semester_id parameter is required"}, status=HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get current semester class",
        operation_id="get_current_semester",
        manual_parameters=[
            openapi.Parameter(
                name='semester_id',
                in_=openapi.IN_QUERY,
                description="Semester id",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TeacherClassStudentsView(generics.ListAPIView):
    serializer_class = StudentInClassSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        teacher = self.request.user.teacher

        try:
            class_obj = Class.objects.get(id=class_id, teacher=teacher)
            return ClassStudent.objects.filter(course_semester=class_obj)
        except Class.DoesNotExist:
            return ClassStudent.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "Class not found or you don't have permission to view this class."},
                            status=HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UpdateStudentGradeView(generics.UpdateAPIView):
    serializer_class = UpdateGradeSerializer
    permission_classes = [IsTeacher]
    queryset = ClassStudent.objects.all()

    def get_object(self):
        class_id = self.kwargs.get('class_id')
        student_id = self.kwargs.get('student_id')
        teacher = self.request.user.teacher

        try:
            class_obj = Class.objects.get(id=class_id, teacher=teacher)
            return ClassStudent.objects.get(course_semester=class_obj, student_id=student_id)
        except (Class.DoesNotExist, ClassStudent.DoesNotExist):
            return None

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not instance:
            return Response({"error": "Class or student not found, or you don't have permission to modify this grade."},
                            status=HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
