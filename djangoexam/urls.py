"""
URL configuration for djangoexam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:login_page", permanent=False)),
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("enrollments/", include("enrollments.urls")),
    path("results/", include("results.urls")),
    path("transcripts/", include("transcripts.urls")),
    path("exams/", include("exams.urls")),
    path("uploads/", include("uploads.urls")),
    path("academics/", include("academics.urls")),
    path("courses/", include("courses.urls")),
    path("admission/", include("admission.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
