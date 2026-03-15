from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.cache import never_cache

from admission.models import Student
from .models import RoleModulePermission
from .permissions import ensure_permissions
from django.contrib.auth import get_user_model
from academics.models import Department

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
        if user is not None and not getattr(user, "is_locked", False):
            login(request, user)
            return redirect("accounts:dashboard")
        if user is not None and getattr(user, "is_locked", False):
            error = "Your account is locked. Please contact the administrator."
        else:
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


@login_required(login_url="accounts:login_page")
@never_cache
def permissions_view(request):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")

    ensure_permissions()
    perms = RoleModulePermission.objects.all().order_by("role", "module")

    if request.method == "POST":
        if request.POST.get("action") == "reset":
            RoleModulePermission.objects.all().delete()
            ensure_permissions()
            return redirect("accounts:permissions")

        for perm in perms:
            key = f"{perm.role}__{perm.module}"
            perm.can_create = key + "__c" in request.POST
            perm.can_read = key + "__r" in request.POST
            perm.can_update = key + "__u" in request.POST
            perm.can_delete = key + "__d" in request.POST
            perm.save(update_fields=["can_create", "can_read", "can_update", "can_delete"])
        return redirect("accounts:permissions")

    return render(request, "accounts/permissions.html", {"perms": perms})


@login_required(login_url="accounts:login_page")
@never_cache
def users_view(request):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")

    User = get_user_model()
    search = request.GET.get("search", "").strip()
    role = request.GET.get("role", "")
    department_id = request.GET.get("department_id", "")

    qs = User.objects.select_related("department").order_by("username")
    if role:
        qs = qs.filter(role=role)
    if department_id:
        qs = qs.filter(department_id=department_id)
    if search:
        qs = qs.filter(username__icontains=search)

    return render(request, "accounts/users.html", {
        "users": qs,
        "search": search,
        "role": role,
        "department_id": department_id,
        "departments": Department.objects.filter(is_active=True).order_by("name"),
    })


@login_required(login_url="accounts:login_page")
@never_cache
def create_user(request):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")

    User = get_user_model()
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "")
        department_id = request.POST.get("department_id") or None

        if not username or not password or not role:
            error = "Username, password, and role are required."
        elif User.objects.filter(username=username).exists():
            error = "A user with this username already exists."
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                role=role,
                department_id=department_id,
            )
            return redirect("accounts:users")

    return render(request, "accounts/create_user.html", {
        "error": error,
        "roles": User.ROLE_CHOICES,
        "departments": Department.objects.filter(is_active=True).order_by("name"),
    })


@login_required(login_url="accounts:login_page")
@never_cache
def edit_user(request, pk):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")

    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        role = request.POST.get("role", user.role)
        department_id = request.POST.get("department_id") or None
        password = request.POST.get("password", "")

        if not username:
            error = "Username is required."
        else:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                error = "A user with this username already exists."
            else:
                user.username = username
                user.role = role
                user.department_id = department_id
                if password:
                    user.set_password(password)
                user.save()
                return redirect("accounts:users")

    return render(request, "accounts/edit_user.html", {
        "user_obj": user,
        "error": error,
        "roles": User.ROLE_CHOICES,
        "departments": Department.objects.filter(is_active=True).order_by("name"),
    })


@login_required(login_url="accounts:login_page")
@never_cache
def delete_user(request, pk):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")

    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if user.pk == request.user.pk:
            return redirect("accounts:users")
        user.delete()
        return redirect("accounts:users")
    return render(request, "accounts/delete_user.html", {"user_obj": user})


@login_required(login_url="accounts:login_page")
@never_cache
def toggle_user_lock(request, pk):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if user.pk == request.user.pk:
            return redirect("accounts:users")
        user.is_locked = not user.is_locked
        user.save(update_fields=["is_locked"])
    return redirect("accounts:users")


@login_required(login_url="accounts:login_page")
@never_cache
def reset_user_password(request, pk):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        new_password = request.POST.get("password", "")
        if new_password:
            user.set_password(new_password)
            user.save(update_fields=["password"])
        return redirect("accounts:users")
    return render(request, "accounts/reset_user_password.html", {"user_obj": user})


def sample_view(request):
    from django.http import HttpResponse
    return HttpResponse("accounts sample view")
