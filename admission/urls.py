from django.urls import path


from . import views

app_name = "admission"

urlpatterns = [
    path("students/", views.students_view, name="students"),
    path("create_student/", views.create_student, name="create_student"),
    path("edit_student/<int:pk>/", views.edit_student, name="edit_student"),
    path("delete_student/<int:pk>/", views.delete_student, name="delete_student"),
]