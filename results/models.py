from django.db import models

class Result(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["enrollment"]),
        ]
    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="result"
    )

    total_marks = models.FloatField()

    grade = models.CharField(max_length=5)
    grade_point = models.FloatField()

    result_published = models.BooleanField(default=False)

    calculated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.enrollment.student.roll_no} - {self.grade}"


# =========================
# SEMESTER GPA
# =========================

class SemesterResult(models.Model):
    student = models.ForeignKey(
        "admission.Student",
        on_delete=models.CASCADE,
        related_name="semester_results"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.CASCADE,
        related_name="results"
    )
    gpa = models.FloatField()

    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "semester")

    def __str__(self):
        return f"{self.student.roll_no} - GPA {self.gpa}"

