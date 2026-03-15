from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    is_locked = models.BooleanField(default=False)

    def in_group(self, name):
        return self.groups.filter(name=name).exists()

    def is_exam_officer(self):
        return self.in_group("EXAM_OFFICER")

    def is_dept_controller(self):
        return self.in_group("DEPT_CONTROLLER") or self.in_group("INTERNAL_EXAM_CONTROLLER")

    def is_internal_exam_controller(self):
        return self.is_dept_controller()

    def is_student(self):
        return self.in_group("STUDENT")

    def is_department_scoped(self):
        return self.is_dept_controller()

    def __str__(self):
        return self.username



