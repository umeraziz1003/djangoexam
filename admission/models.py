from django.db import models
from accounts.models import User

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    full_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    cnic = models.CharField(max_length=20, unique=True)

    roll_no = models.CharField(max_length=20, unique=True)
    registration_no = models.CharField(max_length=50)

    batch = models.ForeignKey(
        "academics.Batch",
        on_delete=models.CASCADE,
        related_name="students"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.roll_no} - {self.full_name}"
