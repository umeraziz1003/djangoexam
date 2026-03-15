from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from ..forms import BatchForm
from ..models import Batch, Department


@login_required(login_url="accounts:login_page")
@never_cache
def batches_view(request):
    search = request.GET.get("search", "").strip()
    qs = Batch.objects.select_related("department").order_by("-start_date")
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(name__icontains=search)
            | Q(program__icontains=search)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    form = BatchForm()
    departments = Department.objects.filter(is_active=True)

    return render(request, "academics/batches.html", {
        "batches": page_obj,
        "page_obj": page_obj,
        "form": form,
        "search": search,
        "departments": departments,
    })


@login_required(login_url="accounts:login_page")
def create_batch(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
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
        dept_id = request.POST.get("department_id")
        if dept_id:
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
    batch.delete()
    return redirect("academics:batches")
