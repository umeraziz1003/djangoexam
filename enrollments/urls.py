from django.urls import path

from . import views

app_name = "enrollments"

urlpatterns = [
    path("", views.enrollments_view, name="enrollments"),
    path("create/", views.create_enrollment, name="create_enrollment"),
    path("<int:pk>/edit/", views.edit_enrollment, name="edit_enrollment"),
    path("<int:pk>/delete/", views.delete_enrollment, name="delete_enrollment"),
    path("semester-courses/", views.semester_courses_view, name="semester_courses"),
    path("course-students/", views.course_students_view, name="course_students"),
    path("student-courses/", views.student_courses_view, name="student_courses"),
    path("ajax/batches/", views.ajax_batches, name="ajax_batches"),
    path("ajax/semesters/", views.ajax_semesters, name="ajax_semesters"),
    path("ajax/students/", views.ajax_students, name="ajax_students"),
    path("ajax/offerings/", views.ajax_offerings, name="ajax_offerings"),
]
