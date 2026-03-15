from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("sample/", views.sample_view, name="sample_view"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("permissions/", views.permissions_view, name="permissions"),
    path("users/", views.users_view, name="users"),
    path("users/create/", views.create_user, name="create_user"),
    path("users/<int:pk>/edit/", views.edit_user, name="edit_user"),
    path("users/<int:pk>/delete/", views.delete_user, name="delete_user"),
    path("users/<int:pk>/lock/", views.toggle_user_lock, name="toggle_user_lock"),
    path("users/<int:pk>/reset-password/", views.reset_user_password, name="reset_user_password"),
    path("", views.login_page, name="login_page"),
]
