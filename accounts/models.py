from django.db import models
from django.contrib.auth.models import AbstractUser


class RoleModulePermission(models.Model):
    ROLE_CHOICES = (
        ("EXAM_OFFICER", "Examination Officer"),
        ("DEPT_CONTROLLER", "Department Exam Controller"),
        ("INTERNAL_EXAM_CONTROLLER", "Department Internal Exam Controller"),
        ("STUDENT", "Student"),
    )

    MODULE_CHOICES = (
        ("DEPARTMENTS", "Departments"),
        ("BATCHES", "Batches"),
        ("SEMESTERS", "Semesters"),
        ("SESSIONS", "Sessions"),
        ("COURSES", "Courses"),
        ("COURSE_OFFERINGS", "Course Offerings"),
        ("ENROLLMENTS", "Enrollments"),
        ("EXAMS", "Exams/Marks"),
        ("RESULTS", "Results"),
        ("TRANSCRIPTS", "Transcripts"),
        ("STUDENTS", "Students"),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    module = models.CharField(max_length=30, choices=MODULE_CHOICES)

    can_create = models.BooleanField(default=True)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=True)

    class Meta:
        unique_together = ("role", "module")

    def __str__(self):
        return f"{self.role} - {self.module}"

class User(AbstractUser):
    ROLE_CHOICES = (
        ("EXAM_OFFICER", "Examination Officer"),
        ("DEPT_CONTROLLER", "Department Exam Controller"),
        ("INTERNAL_EXAM_CONTROLLER", "Department Internal Exam Controller"),
        ("STUDENT", "Student"),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    is_locked = models.BooleanField(default=False)

    def is_exam_officer(self):
        return self.role == "EXAM_OFFICER"

    def is_dept_controller(self):
        return self.role == "DEPT_CONTROLLER"

    def is_internal_exam_controller(self):
        return self.role == "INTERNAL_EXAM_CONTROLLER"

    def is_student(self):
        return self.role == "STUDENT"

    def __str__(self):
        return self.username



