from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK

from .permissions import IsTeacher, IsStudent
from main_app.serializers import *
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from django.db import transaction


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


class RecordAttendanceView(generics.CreateAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsTeacher]

    def create(self, request, *args, **kwargs):
        class_id = self.kwargs.get('class_id')
        teacher = self.request.user.teacher

        try:
            course_semester = Class.objects.get(id=class_id, teacher=teacher)
        except Class.DoesNotExist:
            return Response(
                {"error": "Class not found or you don't have permission to record attendance for this class."},
                status=HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data, many=True, context={'course_semester': course_semester})
        serializer.is_valid(raise_exception=True)

        attendance_records = []
        for item in serializer.validated_data:
            attendance_record = ClassStudentAttendance(
                course_semester=course_semester,
                student=item['student'],
                date=item['date'],
                attendance=item['attendance']
            )
            attendance_records.append(attendance_record)

        ClassStudentAttendance.objects.bulk_create(attendance_records)

        return Response({"message": "Attendance recorded successfully"}, status=HTTP_201_CREATED)


class StudentClassChangeView(generics.CreateAPIView):
    serializer_class = ClassChangeSerializer
    permission_classes = [IsStudent]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        semester_id = self.kwargs.get('semester_id')
        student = self.request.user.student
        now = timezone.now()

        # Check if StudentSemester record exists
        try:
            student_semester = StudentSemester.objects.get(student=student, semester_id=semester_id)
        except StudentSemester.DoesNotExist:
            return Response({"error": "You are not enrolled in this semester."}, status=HTTP_400_BAD_REQUEST)

        # Check if the current time is within the allowed period
        semester = student_semester.semester
        if not (semester.start == now.date() or (semester.add_drop_start <= now.date() <= semester.add_drop_end)):
            if now.date() < semester.start:
                return Response({"error": "The semester has not started yet."}, status=HTTP_400_BAD_REQUEST)
            elif now.date() > semester.add_drop_end:
                return Response({"error": "The add/drop period for this semester has ended."},
                                status=HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        add_classes = serializer.validated_data.get('add_classes', [])
        delete_classes = serializer.validated_data.get('delete_classes', [])

        for class_id in add_classes + delete_classes:
            class_obj = Class.objects.filter(id=class_id, semester=semester)
            if not class_obj.exists():
                return Response({"error": f"class id '{class_id}' in semester {semester} does not exists"},
                                HTTP_400_BAD_REQUEST)

        for class_id in delete_classes:
            if not ClassStudent.objects.filter(course_semester=class_id, student=student).exists():
                return Response({"error": f"you can not delete non-existing class id '{class_id}'."},
                                HTTP_400_BAD_REQUEST)

        for class_id in add_classes:
            if ClassStudent.objects.filter(course_semester=class_id, student=student).exists():
                return Response({"error": f"you can not add existing class id '{class_id}'."},
                                HTTP_400_BAD_REQUEST)

        # Calculate the change in units
        current_classes = ClassStudent.objects.filter(student=student)
        current_units = sum(cls.course_semester.course.units for cls in current_classes)

        add_units = sum(Class.objects.get(id=class_id, semester=semester).course.units
                        for class_id in add_classes)
        delete_units = sum(Class.objects.get(id=class_id, semester=semester).course.units
                           for class_id in delete_classes)

        new_units = current_units + add_units - delete_units

        # Check if new units are within the allowed range
        if new_units < student_semester.min_units or new_units > student_semester.max_units:
            return Response({
                "error": f"Total units must be between {student_semester.min_units} and {student_semester.max_units}."},
                status=HTTP_400_BAD_REQUEST)

        # Process deletions
        ClassStudent.objects.filter(student=student, course_semester_id__in=delete_classes).delete()

        # Process additions
        new_class_students = []
        for class_id in add_classes:
            class_obj = Class.objects.get(id=class_id, semester=semester)
            new_class_students.append(ClassStudent(student=student, course_semester=class_obj))

        ClassStudent.objects.bulk_create(new_class_students)

        # Update StudentSemester
        student_semester.chosen_units = new_units
        student_semester.save()

        return Response({"message": "Classes updated successfully", "new_total_units": new_units}, status=HTTP_200_OK)
