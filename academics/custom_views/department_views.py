from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from ..forms import DepartmentForm
from ..models import Department
from accounts.permissions import can


@login_required(login_url="accounts:login_page")
@never_cache
def departments_view(request):
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")
    search = request.GET.get("search", "").strip()
    qs = Department.objects.all().order_by("name")
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    form = DepartmentForm()

    return render(request, "academics/departments.html", {
        "departments": page_obj,
        "page_obj": page_obj,
        "form": form,
        "search": search,
    })


@login_required(login_url="accounts:login_page")
def create_department(request):
    if request.method == "POST":
        if not request.user.is_exam_officer():
            return redirect("accounts:dashboard")
        if not can(request.user.role, "DEPARTMENTS", "create"):
            return redirect("academics:departments")
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("academics:departments")
        # Re-render with errors
        qs = Department.objects.all().order_by("name")
        paginator = Paginator(qs, 10)
        page_obj = paginator.get_page(None)
        return render(request, "academics/departments.html", {
            "departments": page_obj,
            "page_obj": page_obj,
            "form": form,
            "search": "",
        })
    return redirect("academics:departments")


@login_required(login_url="accounts:login_page")
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        if not request.user.is_exam_officer():
            return redirect("accounts:dashboard")
        if not can(request.user.role, "DEPARTMENTS", "update"):
            return redirect("academics:departments")
        department.name = request.POST.get("name", department.name).strip()
        department.code = request.POST.get("code", department.code).strip()
        try:
            department.duration_years = int(request.POST.get("duration_years", department.duration_years))
        except (ValueError, TypeError):
            pass
        department.is_active = "is_active" in request.POST
        department.save()
    return redirect("academics:departments")


@login_required(login_url="accounts:login_page")
@require_POST
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if not request.user.is_exam_officer():
        return redirect("accounts:dashboard")
    if not can(request.user.role, "DEPARTMENTS", "delete"):
        return redirect("academics:departments")
    department.delete()
    return redirect("academics:departments")
