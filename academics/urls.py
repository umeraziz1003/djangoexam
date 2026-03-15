from django.urls import path
from . import views

app_name = "academics"

urlpatterns = [
    # Department
    path("departments/", views.departments_view, name="departments"),
    path("create_department/", views.create_department, name="create_department"),
    path("edit_department/<int:pk>/", views.edit_department, name="edit_department"),
    path("delete_department/<int:pk>/", views.delete_department, name="delete_department"),

    # Batch
    path("batches/", views.batches_view, name="batches"),
    path("create_batch/", views.create_batch, name="create_batch"),
    path("edit_batch/<int:pk>/", views.edit_batch, name="edit_batch"),
    path("delete_batch/<int:pk>/", views.delete_batch, name="delete_batch"),

    # Semester
    path("semesters/", views.semesters_view, name="semesters"),
    path("create_semester/", views.create_semester, name="create_semester"),
    path("edit_semester/<int:pk>/", views.edit_semester, name="edit_semester"),
    path("delete_semester/<int:pk>/", views.delete_semester, name="delete_semester"),

    # Session
    path("sessions/", views.sessions_view, name="sessions"),
    path("create_session/", views.create_session, name="create_session"),
    path("edit_session/<int:pk>/", views.edit_session, name="edit_session"),
    path("delete_session/<int:pk>/", views.delete_session, name="delete_session"),
]
