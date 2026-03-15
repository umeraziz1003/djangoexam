from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


EXAM_TYPE_CHOICES = (
    ("SESSIONAL", "Sessional"),
    ("MIDTERM", "Midterm"),
    ("TERMINAL", "Terminal"),
)


class ExamSplitConfig(models.Model):
    sessional_max = models.IntegerField(default=30)
    midterm_max = models.IntegerField(default=30)
    terminal_max = models.IntegerField(default=40)

    def total(self):
        return self.sessional_max + self.midterm_max + self.terminal_max

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={"sessional_max": 30, "midterm_max": 30, "terminal_max": 40},
        )
        return obj

    def __str__(self):
        return f"Splits: {self.sessional_max}/{self.midterm_max}/{self.terminal_max}"


class GradeScale(models.Model):
    min_percentage = models.FloatField()
    max_percentage = models.FloatField()
    grade = models.CharField(max_length=5)
    grade_point = models.FloatField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-min_percentage"]

    def __str__(self):
        return f"{self.grade} ({self.min_percentage}-{self.max_percentage})"


class ExamRules(models.Model):
    min_cgpa_dropout = models.FloatField(default=1.0)
    min_cgpa_probation = models.FloatField(default=2.0)
    max_probations_allowed = models.IntegerField(default=2)
    failed_marks_threshold = models.FloatField(default=50.0)
    improvement_min = models.FloatField(default=50.0)
    improvement_max = models.FloatField(default=62.0)
    no_drop_after_semester = models.IntegerField(default=1)
    can_drop = models.BooleanField(default=True)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Exam Rules"


class Marks(models.Model):
    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="marks"
    )

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES
    )

    obtained_marks = models.FloatField(
        validators=[MinValueValidator(0)]
    )

    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("enrollment", "exam_type")

    def __str__(self):
        return f"{self.enrollment} - {self.exam_type}"
