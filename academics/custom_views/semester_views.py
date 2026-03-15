from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from ..forms import SemesterForm
from ..models import Batch, Department, Semester
from accounts.permissions import can


@login_required(login_url="accounts:login_page")
@never_cache
def semesters_view(request):
    search = request.GET.get("search", "").strip()
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        department_id = str(request.user.department_id)
    qs = Semester.objects.select_related("batch").order_by("batch", "semester_number")
    if department_id:
        qs = qs.filter(batch__department_id=department_id)
    if batch_id:
        qs = qs.filter(batch_id=batch_id)
    if search:
        qs = qs.filter(
            Q(semester_number__icontains=search)
            | Q(batch__name__icontains=search)
            | Q(batch__title__icontains=search)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    form = SemesterForm()
    batches = Batch.objects.all().order_by("-start_date")
    if department_id:
        batches = batches.filter(department_id=department_id)
    departments = Department.objects.filter(is_active=True)
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        departments = departments.filter(id=request.user.department_id)

    return render(request, "academics/semesters.html", {
        "semesters": page_obj,
        "page_obj": page_obj,
        "form": form,
        "search": search,
        "batches": batches,
        "departments": departments,
        "department_id": department_id,
        "batch_id": batch_id,
    })


@login_required(login_url="accounts:login_page")
def create_semester(request):
    if request.method == "POST":
        if not can(request.user.role, "SEMESTERS", "create"):
            return redirect("academics:semesters")
        form = SemesterForm(request.POST)
        if form.is_valid():
            if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                if form.cleaned_data["batch"].department_id != request.user.department_id:
                    return redirect("academics:semesters")
            form.save()
            return redirect("academics:semesters")
        qs = Semester.objects.select_related("batch").order_by("batch", "semester_number")
        paginator = Paginator(qs, 10)
        page_obj = paginator.get_page(None)
        batches = Batch.objects.all().order_by("-start_date")
        return render(request, "academics/semesters.html", {
            "semesters": page_obj,
            "page_obj": page_obj,
            "form": form,
            "search": "",
            "batches": batches,
        })
    return redirect("academics:semesters")


@login_required(login_url="accounts:login_page")
def edit_semester(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == "POST":
        if not can(request.user.role, "SEMESTERS", "update"):
            return redirect("academics:semesters")
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            if semester.batch.department_id != request.user.department_id:
                return redirect("academics:semesters")
        batch_id = request.POST.get("batch_id")
        if batch_id and not (request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id):
            semester.batch_id = batch_id
        try:
            semester.semester_number = int(request.POST.get("semester_number", semester.semester_number))
            semester.semester_year = int(request.POST.get("semester_year", semester.semester_year))
        except (ValueError, TypeError):
            pass
        semester.save()
    return redirect("academics:semesters")


@login_required(login_url="accounts:login_page")
@require_POST
def delete_semester(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if not can(request.user.role, "SEMESTERS", "delete"):
        return redirect("academics:semesters")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        if semester.batch.department_id != request.user.department_id:
            return redirect("academics:semesters")
    semester.delete()
    return redirect("academics:semesters")
