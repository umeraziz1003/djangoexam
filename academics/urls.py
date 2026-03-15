from django.urls import path
from . import views

app_name = "academics"

urlpatterns = [
    # Department
    path("departments/", views.departments_view, name="departments"),
    path("create_department/", views.create_department, name="create_department"),
    path("departments/template/", views.departments_template_download, name="departments_template"),
    path("departments/bulk/preview/", views.departments_bulk_preview, name="departments_bulk_preview"),
    path("departments/bulk/commit/", views.departments_bulk_commit, name="departments_bulk_commit"),
    path("edit_department/<int:pk>/", views.edit_department, name="edit_department"),
    path("delete_department/<int:pk>/", views.delete_department, name="delete_department"),

    # Batch
    path("batches/", views.batches_view, name="batches"),
    path("create_batch/", views.create_batch, name="create_batch"),
    path("batches/template/", views.batches_template_download, name="batches_template"),
    path("batches/bulk/preview/", views.batches_bulk_preview, name="batches_bulk_preview"),
    path("batches/bulk/commit/", views.batches_bulk_commit, name="batches_bulk_commit"),
    path("edit_batch/<int:pk>/", views.edit_batch, name="edit_batch"),
    path("delete_batch/<int:pk>/", views.delete_batch, name="delete_batch"),

    # Semester
    path("semesters/", views.semesters_view, name="semesters"),
    path("create_semester/", views.create_semester, name="create_semester"),
    path("semesters/template/", views.semesters_template_download, name="semesters_template"),
    path("semesters/bulk/preview/", views.semesters_bulk_preview, name="semesters_bulk_preview"),
    path("semesters/bulk/commit/", views.semesters_bulk_commit, name="semesters_bulk_commit"),
    path("edit_semester/<int:pk>/", views.edit_semester, name="edit_semester"),
    path("delete_semester/<int:pk>/", views.delete_semester, name="delete_semester"),

    # Session
    path("sessions/", views.sessions_view, name="sessions"),
    path("create_session/", views.create_session, name="create_session"),
    path("sessions/template/", views.sessions_template_download, name="sessions_template"),
    path("sessions/bulk/preview/", views.sessions_bulk_preview, name="sessions_bulk_preview"),
    path("sessions/bulk/commit/", views.sessions_bulk_commit, name="sessions_bulk_commit"),
    path("edit_session/<int:pk>/", views.edit_session, name="edit_session"),
    path("delete_session/<int:pk>/", views.delete_session, name="delete_session"),
]
