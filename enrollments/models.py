from django.db import models

 


class Enrollment(models.Model):
    class Meta:
        unique_together = ("student", "course_offering")
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course_offering"]),
        ]
    student = models.ForeignKey(
        "admission.Student",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course_offering = models.ForeignKey(
        "courses.CourseOffering",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    date_enrolled = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course_offering")

    def __str__(self):
        return f"{self.student.roll_no} -> {self.course_offering}"


# =========================
# EXAM STRUCTURE
# =========================


