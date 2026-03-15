from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from academics.models import Department, Batch, Semester, Session
from admission.models import Student
from courses.models import CourseOffering
from enrollments.models import Enrollment
from exams.models import GradeScale, Marks
from .models import Result


def _get_grade_for_total(total):
    scale = GradeScale.objects.filter(
        is_active=True,
        min_percentage__lte=total,
        max_percentage__gte=total,
    ).order_by("-min_percentage").first()
    if not scale:
        return "N/A", 0
    return scale.grade, scale.grade_point


def _recalc_result(enrollment):
    total = 0
    for mark in Marks.objects.filter(enrollment=enrollment):
        total += mark.obtained_marks
    grade, grade_point = _get_grade_for_total(total)
    result, created = Result.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            "total_marks": total,
            "grade": grade,
            "grade_point": grade_point,
            "result_published": False,
        },
    )
    if not created:
        result.total_marks = total
        result.grade = grade
        result.grade_point = grade_point
        result.save(update_fields=["total_marks", "grade", "grade_point", "calculated_at"])
    return result


@login_required(login_url="accounts:login_page")
@never_cache
def results_view(request):
    search = request.GET.get("search", "").strip()
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    session_id = request.GET.get("session_id", "")
    semester_id = request.GET.get("semester_id", "")
    offering_id = request.GET.get("offering_id", "")
    student_id = request.GET.get("student_id", "")

    qs = Enrollment.objects.select_related(
        "student",
        "course_offering",
        "course_offering__course",
        "course_offering__semester",
        "course_offering__session",
    ).order_by("student__roll_no")

    if session_id:
        qs = qs.filter(course_offering__session_id=session_id)
    if semester_id:
        qs = qs.filter(course_offering__semester_id=semester_id)
    if department_id:
        qs = qs.filter(course_offering__course__department_id=department_id)
    if batch_id:
        qs = qs.filter(student__batch_id=batch_id)
    if offering_id:
        qs = qs.filter(course_offering_id=offering_id)
    if student_id:
        qs = qs.filter(student_id=student_id)
    if search:
        qs = qs.filter(
            Q(student__roll_no__icontains=search)
            | Q(student__full_name__icontains=search)
            | Q(course_offering__course__course_code__icontains=search)
            | Q(course_offering__course__course_title__icontains=search)
        )

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "recalc_filtered":
            for enrollment in qs:
                _recalc_result(enrollment)
            messages.success(request, "Results recalculated for current filter.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))
        if action == "publish_filtered":
            for enrollment in qs:
                result = _recalc_result(enrollment)
                result.result_published = True
                result.save(update_fields=["result_published"])
            messages.success(request, "Results published for current filter.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))
        if action == "toggle_publish":
            enrollment_id = request.POST.get("enrollment_id")
            enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
            result = _recalc_result(enrollment)
            result.result_published = not result.result_published
            result.save(update_fields=["result_published"])
            messages.success(request, "Result publish status updated.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))
        if action == "recalc_one":
            enrollment_id = request.POST.get("enrollment_id")
            enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
            _recalc_result(enrollment)
            messages.success(request, "Result recalculated.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    rows = []
    results_map = {r.enrollment_id: r for r in Result.objects.filter(enrollment__in=page_obj)}
    for enrollment in page_obj:
        result = results_map.get(enrollment.id)
        rows.append({
            "enrollment": enrollment,
            "result": result,
        })

    context = {
        "rows": rows,
        "page_obj": page_obj,
        "sessions": Session.objects.order_by("-start_date"),
        "semesters": Semester.objects.select_related("batch").all(),
        "offerings": CourseOffering.objects.select_related("course", "session", "semester").order_by("course__course_code"),
        "students": Student.objects.filter(is_active=True).order_by("roll_no"),
        "departments": Department.objects.filter(is_active=True).order_by("name"),
        "batches": Batch.objects.all().order_by("start_date"),
        "search": search,
        "department_id": department_id,
        "batch_id": batch_id,
        "session_id": session_id,
        "semester_id": semester_id,
        "offering_id": offering_id,
        "student_id": student_id,
    }
    return render(request, "results/results.html", context)


@login_required(login_url="accounts:login_page")
@never_cache
def student_results_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    enrollments = Enrollment.objects.select_related(
        "course_offering",
        "course_offering__course",
        "course_offering__semester",
        "course_offering__session",
    ).filter(student=student).order_by("course_offering__session__start_date")

    results_map = {r.enrollment_id: r for r in Result.objects.filter(enrollment__in=enrollments)}
    rows = []
    for enrollment in enrollments:
        rows.append({
            "enrollment": enrollment,
            "result": results_map.get(enrollment.id),
        })

    return render(request, "results/student_results.html", {
        "student": student,
        "rows": rows,
    })


# Backward-compatible stub (in case old URLconf is still referenced)
def upload_file(request):
    return HttpResponse("results upload file view")
