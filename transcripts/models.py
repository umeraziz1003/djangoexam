from django.db import models

class Transcript(models.Model):
    student = models.OneToOneField(
        "admission.Student",
        on_delete=models.CASCADE,
        related_name="transcript"
    )

    cgpa = models.FloatField()

    generated_at = models.DateTimeField(auto_now=True)

    pdf_file = models.FileField(
        upload_to="transcripts/",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Transcript - {self.student.roll_no}"

