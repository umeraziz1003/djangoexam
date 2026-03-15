from django.urls import path

from . import views

app_name = "enrollments"

urlpatterns = [
    path("", views.enrollments_view, name="enrollments"),
    path("create/", views.create_enrollment, name="create_enrollment"),
    path("<int:pk>/edit/", views.edit_enrollment, name="edit_enrollment"),
    path("<int:pk>/delete/", views.delete_enrollment, name="delete_enrollment"),
]
