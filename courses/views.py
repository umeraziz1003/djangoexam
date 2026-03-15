from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from academics.models import Batch, Department, Semester, Session
from courses.models import Course
from courses.forms import CourseForm
from accounts.permissions import can


@login_required(login_url="accounts:login_page")
@never_cache
def courses_view(request):
    def _dept_restrict(qs, field_path):
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            return qs.filter(**{field_path: request.user.department_id})
        return qs
    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "add_course":
            if not can(request.user.role, "COURSES", "create"):
                return redirect("courses:courses")
            course_code = request.POST.get("course_code", "").strip()
            course_title = request.POST.get("course_title", "").strip()
            credit_hours = request.POST.get("credit_hours", 3)
            course_type = request.POST.get("course_type", "Core")
            status = request.POST.get("status", "ACTIVE")
            department_id = request.POST.get("department_id")
            if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                department_id = str(request.user.department_id)
            if course_code and course_title and department_id:
                Course.objects.create(
                    course_code=course_code,
                    course_title=course_title,
                    credit_hours=credit_hours,
                    course_type=course_type,
                    status=status,
                    department_id=department_id,
                )
            return redirect("courses:courses")

        elif action == "update_course":
            if not can(request.user.role, "COURSES", "update"):
                return redirect("courses:courses")
            course_id = request.POST.get("course_id")
            course = get_object_or_404(Course, pk=course_id)
            if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                if course.department_id != request.user.department_id:
                    return redirect("courses:courses")
            course.course_code = request.POST.get("course_code", course.course_code).strip()
            course.course_title = request.POST.get("course_title", course.course_title).strip()
            try:
                course.credit_hours = int(request.POST.get("credit_hours", course.credit_hours))
            except (ValueError, TypeError):
                pass
            course.course_type = request.POST.get("course_type", course.course_type)
            course.status = request.POST.get("status", course.status)
            dept_id = request.POST.get("department_id")
            if dept_id and not (request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id):
                course.department_id = dept_id
            course.save()
            return redirect("courses:courses")

        elif action == "delete_course":
            course_id = request.POST.get("course_id")
            course = get_object_or_404(Course, pk=course_id)
            if not can(request.user.role, "COURSES", "delete"):
                return redirect("courses:courses")
            if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                if course.department_id != request.user.department_id:
                    return redirect("courses:courses")
            course.delete()
            return redirect("courses:courses")

        return redirect("courses:courses")

    # GET — apply filters
    department_id = request.GET.get("department_id", "")
    course_type = request.GET.get("course_type", "")
    search = request.GET.get("search", "").strip()

    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        if not department_id:
            department_id = str(request.user.department_id)
    qs = Course.objects.select_related("department").order_by("department__name", "course_code")
    qs = _dept_restrict(qs, "department_id")

    if department_id:
        qs = qs.filter(department_id=department_id)
    if course_type:
        qs = qs.filter(course_type=course_type)
    if search:
        qs = qs.filter(Q(course_code__icontains=search) | Q(course_title__icontains=search))

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    try:
        dept_id_int = int(department_id) if department_id else ""
    except (ValueError, TypeError):
        dept_id_int = ""

    context = {
        "courses": page_obj,
        "page_obj": page_obj,
        "departments": _dept_restrict(Department.objects.filter(is_active=True), "id"),
        "batches": Batch.objects.all(),
        "semesters": Semester.objects.all(),
        "department_id": dept_id_int,
        "course_type": course_type,
        "search": search,
    }
    return render(request, "courses/courses.html", context)


@login_required(login_url="accounts:login_page")
@never_cache
def add_course_view(request):
    def _dept_restrict(qs, field_path):
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            return qs.filter(**{field_path: request.user.department_id})
        return qs
    if request.method == "POST":
        if not can(request.user.role, "COURSES", "create"):
            return redirect("courses:courses")
        data = request.POST.copy()
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            data["department"] = request.user.department_id
        form = CourseForm(data)
        form.fields["department"].queryset = _dept_restrict(Department.objects.filter(is_active=True), "id")
        if form.is_valid():
            form.save()
            return redirect("courses:courses")
        return render(request, "courses/add_course.html", {"form": form})

    form = CourseForm()
    form.fields["department"].queryset = _dept_restrict(Department.objects.filter(is_active=True), "id")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        form.fields["department"].initial = request.user.department_id
        form.fields["department"].disabled = True
    return render(request, "courses/add_course.html", {"form": form})


@login_required(login_url="accounts:login_page")
@never_cache
def course_offerings_view(request):
    from courses.models import CourseOffering

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "add_offering":
            if not can(request.user.role, "COURSE_OFFERINGS", "create"):
                return redirect("courses:course_offerings")
            course_id = request.POST.get("course_id")
            semester_id = request.POST.get("semester_id")
            session_id = request.POST.get("session_id")
            instructor_name = request.POST.get("instructor_name", "").strip()
            if course_id and semester_id and session_id and instructor_name:
                if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                    course = get_object_or_404(Course, pk=course_id)
                    if course.department_id != request.user.department_id:
                        return redirect("courses:course_offerings")
                try:
                    CourseOffering.objects.create(
                        course_id=course_id,
                        semester_id=semester_id,
                        session_id=session_id,
                        instructor_name=instructor_name,
                    )
                except IntegrityError:
                    pass
            return redirect("courses:course_offerings")

        if action == "delete_offering":
            offering_id = request.POST.get("offering_id")
            if offering_id:
                offering = get_object_or_404(CourseOffering, pk=offering_id)
                if not can(request.user.role, "COURSE_OFFERINGS", "delete"):
                    return redirect("courses:course_offerings")
                if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
                    if offering.course.department_id != request.user.department_id:
                        return redirect("courses:course_offerings")
                offering.delete()
            return redirect("courses:course_offerings")

        return redirect("courses:course_offerings")

    # GET — filters
    search = request.GET.get("search", "").strip()
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    session_id = request.GET.get("session_id", "")
    semester_id = request.GET.get("semester_id", "")

    qs = CourseOffering.objects.select_related(
        "course",
        "course__department",
        "semester",
        "semester__batch",
        "session",
    ).order_by("-session__start_date", "course__course_code")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        qs = qs.filter(course__department_id=request.user.department_id)

    if session_id:
        qs = qs.filter(session_id=session_id)
    if semester_id:
        qs = qs.filter(semester_id=semester_id)
    if department_id:
        qs = qs.filter(course__department_id=department_id)
    if batch_id:
        qs = qs.filter(semester__batch_id=batch_id)
    if search:
        qs = qs.filter(
            Q(course__course_code__icontains=search)
            | Q(course__course_title__icontains=search)
            | Q(instructor_name__icontains=search)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "offerings": page_obj,
        "page_obj": page_obj,
        "courses": Course.objects.select_related("department").order_by("course_code"),
        "semesters": Semester.objects.select_related("batch").all(),
        "sessions": Session.objects.order_by("-start_date"),
        "departments": Department.objects.filter(is_active=True),
        "batches": Batch.objects.all().order_by("start_date"),
        "search": search,
        "department_id": department_id,
        "batch_id": batch_id,
        "session_id": session_id,
        "semester_id": semester_id,
    }
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        context["courses"] = context["courses"].filter(department_id=request.user.department_id)
        context["semesters"] = context["semesters"].filter(batch__department_id=request.user.department_id)
        context["departments"] = context["departments"].filter(id=request.user.department_id)
        context["batches"] = context["batches"].filter(department_id=request.user.department_id)
    return render(request, "courses/courses_offerings.html", context)
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        if not department_id:
            department_id = str(request.user.department_id)
