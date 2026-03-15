from django.urls import path    
from . import views
app_name = "courses"

urlpatterns = [
    path("offerings/", views.course_offerings_view, name="course_offerings"),
    path("courses/", views.courses_view, name="courses"),
    path("courses/add/", views.add_course_view, name="add_course"),
    
]
