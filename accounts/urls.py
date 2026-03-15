from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("sample/", views.sample_view, name="sample_view"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.login_page, name="login_page"),
]
