from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main_app.views import *

admin_router = DefaultRouter()
admin_router.register(r'groups', AdminGroupViewSet)
admin_router.register(r'semesters', AdminSemesterViewSet)
admin_router.register(r'courses', AdminCourseViewSet)
admin_router.register(r'teachers', AdminTeacherViewSet)
admin_router.register(r'students', AdminStudentViewSet)
admin_router.register(r'student-semesters', AdminStudentSemesterViewSet)
admin_router.register(r'classes', AdminClassViewSet)
admin_router.register(r'class-students', AdminClassStudentViewSet)
admin_router.register(r'class-student-attendances', AdminClassStudentAttendanceViewSet)

urlpatterns = [
    path('admin/', include(admin_router.urls)),
]
