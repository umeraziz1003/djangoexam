from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from admission.models import Student
from enrollments.models import Enrollment
from results.models import Result, SemesterResult
from .models import Transcript


def _calc_gpa(results):
    total_quality = 0
    total_credits = 0
    for res in results:
        credits = res.enrollment.course_offering.course.credit_hours
        total_quality += res.grade_point * credits
        total_credits += credits
    if total_credits == 0:
        return 0
    return round(total_quality / total_credits, 2)


@login_required(login_url="accounts:login_page")
@never_cache
def my_transcript_view(request):
    if not request.user.is_student():
        return redirect("accounts:dashboard")
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect("accounts:dashboard")
    return _render_transcript(request, student)


@login_required(login_url="accounts:login_page")
@never_cache
def transcript_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.user.is_student():
        try:
            if request.user.student_profile.id != student.id:
                return redirect("accounts:dashboard")
        except Student.DoesNotExist:
            return redirect("accounts:dashboard")
    return _render_transcript(request, student)


def _render_transcript(request, student):
    enrollments = Enrollment.objects.select_related(
        "course_offering",
        "course_offering__course",
        "course_offering__semester",
        "course_offering__session",
    ).filter(student=student)

    results = Result.objects.select_related(
        "enrollment",
        "enrollment__course_offering",
        "enrollment__course_offering__course",
        "enrollment__course_offering__semester",
        "enrollment__course_offering__session",
    ).filter(
        enrollment__in=enrollments,
        result_published=True,
    )

    # Group by semester for GPA
    semester_groups = {}
    for res in results:
        semester = res.enrollment.course_offering.semester
        semester_groups.setdefault(semester, []).append(res)

    semester_rows = []
    for semester, res_list in semester_groups.items():
        gpa = _calc_gpa(res_list)
        SemesterResult.objects.update_or_create(
            student=student,
            semester=semester,
            defaults={"gpa": gpa},
        )
        semester_rows.append({
            "semester": semester,
            "gpa": gpa,
            "results": res_list,
        })

    semester_rows.sort(key=lambda r: r["semester"].semester_number)

    cgpa = _calc_gpa(results)
    Transcript.objects.update_or_create(
        student=student,
        defaults={"cgpa": cgpa},
    )

    return render(request, "transcripts/transcript.html", {
        "student": student,
        "semester_rows": semester_rows,
        "cgpa": cgpa,
        "total_credits": results.aggregate(total=Sum("enrollment__course_offering__course__credit_hours"))["total"] or 0,
    })
