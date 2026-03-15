from django.urls import path
from . import views

app_name = "results"

urlpatterns = [
    path("", views.results_view, name="results"),
    path("student/<int:student_id>/", views.student_results_view, name="student_results"),
]
