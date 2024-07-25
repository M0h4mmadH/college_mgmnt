from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from main_app.models import Group, Teacher, Student, Semester, Course, Class, ClassStudent
from datetime import timedelta
from tqdm import tqdm
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        ClassStudent.objects.all().delete()
        Student.objects.all().delete()
        Class.objects.all().delete()
        Course.objects.all().delete()
        Teacher.objects.all().delete()
        ClassStudent.objects.all().delete()
        Semester.objects.all().delete()
        Group.objects.all().delete()

        self.stdout.write('Populating database...')

        # Create groups
        groups = [
            Group.objects.create(name="CS"),
            Group.objects.create(name="CE"),
            Group.objects.create(name="IT")
        ]

        # Create teachers
        for group in tqdm(groups):
            for i in range(10):
                Teacher.objects.create(
                    username=f"{group.name.lower()}_teacher_{i + 1}",
                    password="test",
                    first_name=f"Teacher{i + 1}",
                    last_name=f"{group.name}",
                    email=f"{group.name.lower()}_teacher_{i + 1}@example.com",
                    group=group,
                    gender=random.choice(["M", "F"])
                )

        # Create semesters
        now = timezone.now()
        for group in tqdm(groups):
            Semester.objects.create(
                entrant_date=now.date(),
                group=group,
                start=now.date(),
                add_drop_start=now.date() + timedelta(days=7),
                add_drop_end=now.date() + timedelta(days=14)
            )
            Semester.objects.create(
                entrant_date=now.date() + timedelta(days=180),
                group=group,
                start=now.date() + timedelta(days=180),
                add_drop_start=now.date() + timedelta(days=187),
                add_drop_end=now.date() + timedelta(days=194)
            )

        # Create students
        for group in tqdm(groups):
            for i in range(10):
                Student.objects.create(
                    username=f"{group.name.lower()}_student_{i + 1}",
                    password="test",
                    first_name=f"Student{i + 1}",
                    last_name=f"{group.name}",
                    email=f"{group.name.lower()}_student_{i + 1}@example.com",
                    group=group,
                    gender=random.choice(["M", "F"])
                )

        # Create courses
        courses = [
            Course.objects.create(name="Introduction to Programming", group=groups[0], units=3),
            Course.objects.create(name="Data Structures", group=groups[0], units=4),
            Course.objects.create(name="Digital Logic", group=groups[1], units=3),
            Course.objects.create(name="Computer Architecture", group=groups[1], units=4),
            Course.objects.create(name="Network Fundamentals", group=groups[2], units=3),
            Course.objects.create(name="Database Management", group=groups[2], units=4),
        ]

        # Create classes and assign students
        for semester in tqdm(Semester.objects.all()):
            for course in courses:
                if course.group == semester.group:
                    teacher = Teacher.objects.filter(group=semester.group).order_by('?').first()
                    class_obj = Class.objects.create(
                        course=course,
                        semester=semester,
                        teacher=teacher,
                        class_start_time=timezone.now().time()
                    )

                    # Assign students to the class
                    students = Student.objects.filter(group=semester.group).order_by('?')[:5]
                    for student in students:
                        ClassStudent.objects.create(
                            course_semester=class_obj,
                            student=student
                        )

        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))