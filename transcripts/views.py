from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from admission.models import Student
from accounts.permissions import can
from .services import update_transcript_for_student


@login_required(login_url="accounts:login_page")
@never_cache
def my_transcript_view(request):
    if not can(request.user, "TRANSCRIPTS", "read"):
        return redirect("accounts:dashboard")
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
    if not can(request.user, "TRANSCRIPTS", "read"):
        return redirect("accounts:dashboard")
    student = get_object_or_404(Student, pk=student_id)
    if request.user.is_student():
        try:
            if request.user.student_profile.id != student.id:
                return redirect("accounts:dashboard")
        except Student.DoesNotExist:
            return redirect("accounts:dashboard")
    return _render_transcript(request, student)


def _render_transcript(request, student):
    data = update_transcript_for_student(student)
    if not data:
        return redirect("accounts:dashboard")

    results = data["results"]
    semester_groups = data["semester_groups"]
    semester_gpas = data["semester_gpas"]

    semester_rows = []
    for semester, res_list in semester_groups.items():
        gpa = semester_gpas.get(semester, 0)
        semester_rows.append({
            "semester": semester,
            "gpa": gpa,
            "results": res_list,
        })

    semester_rows.sort(key=lambda r: r["semester"].semester_number)

    cgpa = data["cgpa"]

    return render(request, "transcripts/transcript.html", {
        "student": student,
        "semester_rows": semester_rows,
        "cgpa": cgpa,
        "total_credits": data["total_credits"],
    })
