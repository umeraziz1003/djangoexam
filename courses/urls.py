from django.urls import path    
from . import views
app_name = "courses"

urlpatterns = [
    path("offerings/", views.course_offerings_view, name="course_offerings"),
    path("courses/", views.courses_view, name="courses"),
    path("courses/add/", views.add_course_view, name="add_course"),
    path("courses/template/", views.courses_template_download, name="courses_template"),
    path("courses/bulk/preview/", views.courses_bulk_preview, name="courses_bulk_preview"),
    path("courses/bulk/commit/", views.courses_bulk_commit, name="courses_bulk_commit"),
    path("offerings/template/", views.offerings_template_download, name="offerings_template"),
    path("offerings/bulk/preview/", views.offerings_bulk_preview, name="offerings_bulk_preview"),
    path("offerings/bulk/commit/", views.offerings_bulk_commit, name="offerings_bulk_commit"),
    
]
