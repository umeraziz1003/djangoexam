from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from ..forms import SessionForm
from ..models import Session
from accounts.permissions import can


@login_required(login_url="accounts:login_page")
@never_cache
def sessions_view(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "")
    qs = Session.objects.all().order_by("-start_date")
    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "inactive":
        qs = qs.filter(is_active=False)
    if search:
        qs = qs.filter(Q(name__icontains=search))

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    form = SessionForm()

    return render(request, "academics/sessions.html", {
        "sessions": page_obj,
        "page_obj": page_obj,
        "form": form,
        "search": search,
        "status": status,
    })


@login_required(login_url="accounts:login_page")
def create_session(request):
    if request.method == "POST":
        if not can(request.user.role, "SESSIONS", "create"):
            return redirect("academics:sessions")
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("academics:sessions")
        qs = Session.objects.all().order_by("-start_date")
        paginator = Paginator(qs, 10)
        page_obj = paginator.get_page(None)
        return render(request, "academics/sessions.html", {
            "sessions": page_obj,
            "page_obj": page_obj,
            "form": form,
            "search": "",
        })
    return redirect("academics:sessions")


@login_required(login_url="accounts:login_page")
def edit_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == "POST":
        if not can(request.user.role, "SESSIONS", "update"):
            return redirect("academics:sessions")
        session.name = request.POST.get("name", session.name).strip()
        session.start_date = request.POST.get("start_date", session.start_date)
        session.end_date = request.POST.get("end_date", session.end_date)
        session.is_active = "is_active" in request.POST
        session.save()
    return redirect("academics:sessions")


@login_required(login_url="accounts:login_page")
@require_POST
def delete_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if not can(request.user.role, "SESSIONS", "delete"):
        return redirect("academics:sessions")
    session.delete()
    return redirect("academics:sessions")
