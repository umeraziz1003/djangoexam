from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("EXAM_OFFICER", "Examination Officer"),
        ("DEPT_CONTROLLER", "Department Exam Controller"),
        ("STUDENT", "Student"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def is_exam_officer(self):
        return self.role == "EXAM_OFFICER"

    def is_dept_controller(self):
        return self.role == "DEPT_CONTROLLER"

    def is_student(self):
        return self.role == "STUDENT"

    def __str__(self):
        return self.username



