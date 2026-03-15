from django.urls import path
from . import views

app_name = "transcripts"

urlpatterns = [
    path("my/", views.my_transcript_view, name="my_transcript"),
    path("student/<int:student_id>/", views.transcript_view, name="transcript"),
]
