from django.db import models


class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ("Core", "Core"),
        ("Elective", "Elective"),
    ]
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    ]
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.CASCADE,
        related_name="courses"
    )

    course_code = models.CharField(max_length=20)
    course_title = models.CharField(max_length=255)
    credit_hours = models.IntegerField()
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES)  # Core, Elective, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"


class CourseOffering(models.Model):
    class Meta:
        unique_together = ("course", "semester", "session")
        indexes = [
            models.Index(fields=["semester"]),
            models.Index(fields=["session"]),
        ]
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="offerings"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.CASCADE,
        related_name="course_offerings"
    )

    session = models.ForeignKey(
        "academics.Session",
        on_delete=models.CASCADE,
        related_name="course_offerings"
    )

    instructor_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.course.course_code} ({self.session})"
