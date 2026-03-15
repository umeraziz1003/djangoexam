from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from admission.models import Student

@never_cache
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login_page")
    return render(request, "accounts/logout.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("accounts:dashboard")
        error = "Invalid username or password. Please try again."

    return render(request, "accounts/login.html", {"error": error})


@login_required(login_url="accounts:login_page")
@never_cache
def dashboard(request):
    from academics.models import Department, Batch, Session
    from results.models import Result

    student_profile = None
    student_results = []
    student_cgpa = None
    dept_count = batch_count = session_count = student_count = 0

    if request.user.role == "STUDENT":
        try:
            student_profile = request.user.student_profile
        except Student.DoesNotExist:
            student_profile = None
        if student_profile:
            student_results = Result.objects.select_related(
                "enrollment",
                "enrollment__course_offering",
                "enrollment__course_offering__course",
                "enrollment__course_offering__session",
            ).filter(
                enrollment__student=student_profile,
                result_published=True,
            ).order_by("-calculated_at")[:6]

    if request.user.role in ("EXAM_OFFICER", "DEPT_CONTROLLER"):
        dept_count = Department.objects.filter(is_active=True).count()
        batch_count = Batch.objects.filter(status="ACTIVE").count()
        session_count = Session.objects.filter(is_active=True).count()
        student_count = Student.objects.filter(is_active=True).count()

    is_student = request.user.is_student()
    is_exam_officer = request.user.is_exam_officer()

    context = {
        "student_profile": student_profile,
        "student_results": student_results,
        "student_cgpa": student_cgpa,
        "is_student": is_student,
        "is_exam_officer": is_exam_officer,
        "dept_count": dept_count,
        "batch_count": batch_count,
        "session_count": session_count,
        "student_count": student_count,
    }
    return render(request, "dashboard/index.html", context)


def sample_view(request):
    from django.http import HttpResponse
    return HttpResponse("accounts sample view")
