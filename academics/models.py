from django.db import models
from django.conf import settings


# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    duration_years = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Batch(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="batches"
    )
    title = models.CharField(max_length=100)  # e.g. "Batch 2024"
    name = models.CharField(max_length=100)  # e.g. "Computer Science Batch 2024"
    start_date = models.DateField()

    program = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="ACTIVE")
    def __str__(self):
        return f"{self.program} {self.start_date.year}"


class Semester(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="semesters"
    )
    semester_number = models.IntegerField()
    semester_year = models.IntegerField() # as 1st year, 2nd year, etc.

    def __str__(self):
        return f"{self.batch} - Semester {self.semester_number}"


class Session(models.Model):
    name = models.CharField(max_length=100)  # Fall 2024
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name




class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)

    object_id = models.IntegerField(null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action}"
