from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from admission.models import Student
from academics.models import Department, Semester, Session, Batch
from courses.models import CourseOffering
from .forms import EnrollmentForm
from .models import Enrollment


@login_required(login_url="accounts:login_page")
@never_cache
def enrollments_view(request):
    search = request.GET.get("search", "").strip()
    student_id = request.GET.get("student_id", "")
    offering_id = request.GET.get("offering_id", "")

    qs = Enrollment.objects.select_related(
        "student",
        "student__batch",
        "course_offering",
        "course_offering__course",
        "course_offering__course__department",
        "course_offering__semester",
        "course_offering__session",
    ).order_by("-date_enrolled")

    if student_id:
        qs = qs.filter(student_id=student_id)
    if offering_id:
        qs = qs.filter(course_offering_id=offering_id)
    if search:
        qs = qs.filter(
            Q(student__roll_no__icontains=search)
            | Q(student__full_name__icontains=search)
            | Q(course_offering__course__course_code__icontains=search)
            | Q(course_offering__course__course_title__icontains=search)
            | Q(course_offering__instructor_name__icontains=search)
            | Q(course_offering__session__name__icontains=search)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "enrollments": page_obj,
        "page_obj": page_obj,
        "students": Student.objects.filter(is_active=True).order_by("roll_no"),
        "offerings": CourseOffering.objects.select_related(
            "course",
            "semester",
            "session",
        ).order_by("course__course_code"),
        "search": search,
        "student_id": student_id,
        "offering_id": offering_id,
    }
    return render(request, "enrollments/enrollments.html", context)


@login_required(login_url="accounts:login_page")
@never_cache
def create_enrollment(request):
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("enrollments:enrollments")
            except IntegrityError:
                form.add_error(None, "This student is already enrolled in the selected course offering.")
    else:
        form = EnrollmentForm()

    return render(request, "enrollments/create_enrollment.html", {"form": form})


@login_required(login_url="accounts:login_page")
@never_cache
def edit_enrollment(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == "POST":
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            try:
                form.save()
                return redirect("enrollments:enrollments")
            except IntegrityError:
                form.add_error(None, "This student is already enrolled in the selected course offering.")
    else:
        form = EnrollmentForm(instance=enrollment)

    return render(request, "enrollments/edit_enrollment.html", {
        "form": form,
        "enrollment": enrollment,
    })


@login_required(login_url="accounts:login_page")
@never_cache
def delete_enrollment(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == "POST":
        enrollment.delete()
        return redirect("enrollments:enrollments")
    return render(request, "enrollments/delete_enrollment.html", {"enrollment": enrollment})


@login_required(login_url="accounts:login_page")
@never_cache
def semester_courses_view(request):
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    semester_id = request.GET.get("semester_id", "")

    batches = Batch.objects.all()
    semesters = Semester.objects.select_related("batch").all()
    if department_id:
        batches = batches.filter(department_id=department_id)
        semesters = semesters.filter(batch__department_id=department_id)
    if batch_id:
        semesters = semesters.filter(batch_id=batch_id)

    offerings = CourseOffering.objects.select_related(
        "course",
        "semester",
        "session",
        "course__department",
        "semester__batch",
    ).order_by("course__course_code")
    if department_id:
        offerings = offerings.filter(course__department_id=department_id)
    if batch_id:
        offerings = offerings.filter(semester__batch_id=batch_id)
    if semester_id:
        offerings = offerings.filter(semester_id=semester_id)

    rows = []
    for o in offerings:
        rows.append({
            "offering": o,
            "students_count": o.enrollments.count(),
        })

    return render(request, "enrollments/semester_courses.html", {
        "departments": Department.objects.filter(is_active=True).order_by("name"),
        "batches": batches.order_by("start_date"),
        "semesters": semesters.order_by("semester_number"),
        "department_id": department_id,
        "batch_id": batch_id,
        "semester_id": semester_id,
        "rows": rows,
    })


@login_required(login_url="accounts:login_page")
@never_cache
def course_students_view(request):
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    semester_id = request.GET.get("semester_id", "")
    session_id = request.GET.get("session_id", "")
    offering_id = request.GET.get("offering_id", "")

    offerings = CourseOffering.objects.select_related(
        "course", "session", "semester", "semester__batch", "course__department"
    ).order_by("course__course_code")
    if department_id:
        offerings = offerings.filter(course__department_id=department_id)
    if batch_id:
        offerings = offerings.filter(semester__batch_id=batch_id)
    if semester_id:
        offerings = offerings.filter(semester_id=semester_id)
    if session_id:
        offerings = offerings.filter(session_id=session_id)

    enrollments_qs = Enrollment.objects.select_related(
        "student",
        "student__batch",
        "course_offering",
        "course_offering__course",
        "course_offering__semester",
        "course_offering__session",
    ).order_by("student__roll_no")

    if department_id:
        enrollments_qs = enrollments_qs.filter(course_offering__course__department_id=department_id)
    if batch_id:
        enrollments_qs = enrollments_qs.filter(course_offering__semester__batch_id=batch_id)
    if semester_id:
        enrollments_qs = enrollments_qs.filter(course_offering__semester_id=semester_id)
    if session_id:
        enrollments_qs = enrollments_qs.filter(course_offering__session_id=session_id)
    if offering_id:
        enrollments_qs = enrollments_qs.filter(course_offering_id=offering_id)

    # show unique students (avoid duplicates across multiple offerings)
    seen = set()
    enrollments = []
    for e in enrollments_qs:
        if e.student_id in seen:
            continue
        seen.add(e.student_id)
        enrollments.append(e)

    return render(request, "enrollments/course_students.html", {
        "departments": Department.objects.filter(is_active=True).order_by("name"),
        "batches": Batch.objects.all().order_by("start_date"),
        "semesters": Semester.objects.select_related("batch").all().order_by("semester_number"),
        "sessions": Session.objects.order_by("-start_date"),
        "department_id": department_id,
        "batch_id": batch_id,
        "semester_id": semester_id,
        "session_id": session_id,
        "offerings": offerings,
        "offering_id": offering_id,
        "enrollments": enrollments,
    })


@login_required(login_url="accounts:login_page")
@never_cache
def student_courses_view(request):
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    student_id = request.GET.get("student_id", "")
    students = Student.objects.filter(is_active=True).order_by("roll_no")
    if department_id:
        students = students.filter(batch__department_id=department_id)
    if batch_id:
        students = students.filter(batch_id=batch_id)
    enrollments_qs = Enrollment.objects.select_related(
        "course_offering",
        "course_offering__course",
        "course_offering__semester",
        "course_offering__session",
        "student",
        "student__batch",
    ).order_by("student__roll_no", "course_offering__course__course_code")

    if department_id:
        enrollments_qs = enrollments_qs.filter(student__batch__department_id=department_id)
    if batch_id:
        enrollments_qs = enrollments_qs.filter(student__batch_id=batch_id)
    if student_id:
        enrollments_qs = enrollments_qs.filter(student_id=student_id)

    return render(request, "enrollments/student_courses.html", {
        "departments": Department.objects.filter(is_active=True).order_by("name"),
        "batches": Batch.objects.all().order_by("start_date"),
        "department_id": department_id,
        "batch_id": batch_id,
        "students": students,
        "student_id": student_id,
        "enrollments": enrollments_qs,
    })


@login_required(login_url="accounts:login_page")
def ajax_batches(request):
    department_id = request.GET.get("department_id")
    qs = Batch.objects.all().order_by("start_date")
    if department_id:
        qs = qs.filter(department_id=department_id)
    data = [{"id": b.id, "label": str(b)} for b in qs]
    return JsonResponse({"results": data})


@login_required(login_url="accounts:login_page")
def ajax_semesters(request):
    batch_id = request.GET.get("batch_id")
    qs = Semester.objects.select_related("batch").all().order_by("semester_number")
    if batch_id:
        qs = qs.filter(batch_id=batch_id)
    data = [{"id": s.id, "label": str(s)} for s in qs]
    return JsonResponse({"results": data})


@login_required(login_url="accounts:login_page")
def ajax_students(request):
    department_id = request.GET.get("department_id")
    batch_id = request.GET.get("batch_id")
    qs = Student.objects.filter(is_active=True).order_by("roll_no")
    if department_id:
        qs = qs.filter(batch__department_id=department_id)
    if batch_id:
        qs = qs.filter(batch_id=batch_id)
    data = [{"id": s.id, "label": f"{s.roll_no} — {s.full_name}"} for s in qs]
    return JsonResponse({"results": data})


@login_required(login_url="accounts:login_page")
def ajax_offerings(request):
    department_id = request.GET.get("department_id")
    batch_id = request.GET.get("batch_id")
    semester_id = request.GET.get("semester_id")
    session_id = request.GET.get("session_id")

    qs = CourseOffering.objects.select_related("course", "session", "semester").order_by("course__course_code")
    if department_id:
        qs = qs.filter(course__department_id=department_id)
    if batch_id:
        qs = qs.filter(semester__batch_id=batch_id)
    if semester_id:
        qs = qs.filter(semester_id=semester_id)
    if session_id:
        qs = qs.filter(session_id=session_id)

    data = [{
        "id": o.id,
        "label": f"{o.course.course_code} — {o.course.course_title} ({o.session.name})",
    } for o in qs]
    return JsonResponse({"results": data})

