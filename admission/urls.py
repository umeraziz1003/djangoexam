from django.urls import path


from . import views

app_name = "admission"

urlpatterns = [
    path("students/", views.students_view, name="students"),
    path("create_student/", views.create_student, name="create_student"),
    path("students/template/", views.students_template_download, name="students_template"),
    path("students/bulk/preview/", views.students_bulk_preview, name="students_bulk_preview"),
    path("students/bulk/commit/", views.students_bulk_commit, name="students_bulk_commit"),
    path("edit_student/<int:pk>/", views.edit_student, name="edit_student"),
    path("delete_student/<int:pk>/", views.delete_student, name="delete_student"),
]
