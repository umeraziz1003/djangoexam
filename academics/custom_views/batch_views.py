from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from ..forms import BatchForm
from ..models import Batch, Department
from accounts.permissions import can


@login_required(login_url="accounts:login_page")
@never_cache
def batches_view(request):
    search = request.GET.get("search", "").strip()
    department_id = request.GET.get("department_id", "")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        department_id = str(request.user.department_id)
    qs = Batch.objects.select_related("department").order_by("-start_date")
    if department_id:
        qs = qs.filter(department_id=department_id)
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(name__icontains=search)
            | Q(program__icontains=search)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    form = BatchForm()
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        form.fields["department"].initial = request.user.department_id
        form.fields["department"].disabled = True
    departments = Department.objects.filter(is_active=True)
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        departments = departments.filter(id=request.user.department_id)

    return render(request, "academics/batches.html", {
        "batches": page_obj,
        "page_obj": page_obj,
        "form": form,
        "search": search,
        "departments": departments,
        "department_id": department_id,
    })


@login_required(login_url="accounts:login_page")
def create_batch(request):
    if request.method == "POST":
        if not can(request.user.role, "BATCHES", "create"):
            return redirect("academics:batches")
        data = request.POST.copy()
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            data["department"] = request.user.department_id
        form = BatchForm(data)
        if form.is_valid():
            if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                if form.cleaned_data["department"].id != request.user.department_id:
                    return redirect("academics:batches")
            form.save()
            return redirect("academics:batches")
        qs = Batch.objects.select_related("department").order_by("-start_date")
        paginator = Paginator(qs, 10)
        page_obj = paginator.get_page(None)
        departments = Department.objects.filter(is_active=True)
        return render(request, "academics/batches.html", {
            "batches": page_obj,
            "page_obj": page_obj,
            "form": form,
            "search": "",
            "departments": departments,
        })
    return redirect("academics:batches")


@login_required(login_url="accounts:login_page")
def edit_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == "POST":
        if not can(request.user.role, "BATCHES", "update"):
            return redirect("academics:batches")
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            if batch.department_id != request.user.department_id:
                return redirect("academics:batches")
        dept_id = request.POST.get("department_id")
        if dept_id and not (request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id):
            batch.department_id = dept_id
        batch.title = request.POST.get("title", batch.title).strip()
        batch.name = request.POST.get("name", batch.name).strip()
        batch.start_date = request.POST.get("start_date", batch.start_date)
        batch.program = request.POST.get("program", batch.program).strip()
        batch.status = request.POST.get("status", batch.status)
        batch.save()
    return redirect("academics:batches")


@login_required(login_url="accounts:login_page")
@require_POST
def delete_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if not can(request.user.role, "BATCHES", "delete"):
        return redirect("academics:batches")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        if batch.department_id != request.user.department_id:
            return redirect("academics:batches")
    batch.delete()
    return redirect("academics:batches")
