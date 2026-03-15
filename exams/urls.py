from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    path("marks/", views.manage_marks_view, name="manage_marks"),
    path("marks/template/", views.marks_template_download, name="marks_template"),
    path("splits/", views.exam_splits_view, name="exam_splits"),
    path("grading/", views.grading_system_view, name="grading_system"),
    path("grading/template/", views.grade_scale_template_download, name="grade_scale_template"),
    path("grading/import/", views.grade_scale_import, name="grade_scale_import"),
    path("grading/<int:pk>/edit/", views.edit_grade_scale, name="edit_grade_scale"),
    path("grading/<int:pk>/delete/", views.delete_grade_scale, name="delete_grade_scale"),
    path("rules/", views.exam_rules_view, name="exam_rules"),
]
