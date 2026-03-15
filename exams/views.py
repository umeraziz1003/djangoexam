from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from enrollments.models import Enrollment
from courses.models import CourseOffering
from results.models import Result

from .forms import ExamSplitConfigForm, GradeScaleForm, ExamRulesForm
from .models import ExamSplitConfig, GradeScale, ExamRules, Marks, EXAM_TYPE_CHOICES


def _get_grade_for_total(total):
    scale = GradeScale.objects.filter(is_active=True, min_percentage__lte=total, max_percentage__gte=total) \
        .order_by("-min_percentage") \
        .first()
    if not scale:
        return "N/A", 0
    return scale.grade, scale.grade_point


@login_required(login_url="accounts:login_page")
@never_cache
def exam_splits_view(request):
    config = ExamSplitConfig.get_solo()
    if request.method == "POST":
        form = ExamSplitConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam splits updated.")
            return redirect("exams:exam_splits")
    else:
        form = ExamSplitConfigForm(instance=config)
    return render(request, "exams/exam_splits.html", {"form": form, "total": config.total()})


@login_required(login_url="accounts:login_page")
@never_cache
def grading_system_view(request):
    if request.method == "POST":
        form = GradeScaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Grade scale added.")
            return redirect("exams:grading_system")
    else:
        form = GradeScaleForm()

    scales = GradeScale.objects.all()
    return render(request, "exams/grading_system.html", {"form": form, "scales": scales})


@login_required(login_url="accounts:login_page")
@never_cache
def edit_grade_scale(request, pk):
    scale = get_object_or_404(GradeScale, pk=pk)
    if request.method == "POST":
        form = GradeScaleForm(request.POST, instance=scale)
        if form.is_valid():
            form.save()
            messages.success(request, "Grade scale updated.")
            return redirect("exams:grading_system")
    else:
        form = GradeScaleForm(instance=scale)
    return render(request, "exams/edit_grade_scale.html", {"form": form, "scale": scale})


@login_required(login_url="accounts:login_page")
@never_cache
def delete_grade_scale(request, pk):
    scale = get_object_or_404(GradeScale, pk=pk)
    if request.method == "POST":
        scale.delete()
        messages.success(request, "Grade scale removed.")
        return redirect("exams:grading_system")
    return render(request, "exams/delete_grade_scale.html", {"scale": scale})


@login_required(login_url="accounts:login_page")
@never_cache
def exam_rules_view(request):
    rules = ExamRules.get_solo()
    if request.method == "POST":
        form = ExamRulesForm(request.POST, instance=rules)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam rules updated.")
            return redirect("exams:exam_rules")
    else:
        form = ExamRulesForm(instance=rules)
    return render(request, "exams/exam_rules.html", {"form": form})


@login_required(login_url="accounts:login_page")
@never_cache
def manage_marks_view(request):
    config = ExamSplitConfig.get_solo()
    offerings = CourseOffering.objects.select_related("course", "session", "semester").order_by("course__course_code")

    offering_id = request.GET.get("offering_id") or request.POST.get("offering_id") or ""
    enrollments = Enrollment.objects.select_related("student", "course_offering").filter(
        course_offering_id=offering_id
    ).order_by("student__roll_no") if offering_id else Enrollment.objects.none()

    marks_map = {(m.enrollment_id, m.exam_type): m for m in Marks.objects.filter(enrollment__in=enrollments)}
    rows = []
    for enrollment in enrollments:
        rows.append({
            "enrollment": enrollment,
            "sessional": marks_map.get((enrollment.id, "SESSIONAL")).obtained_marks if marks_map.get((enrollment.id, "SESSIONAL")) else "",
            "midterm": marks_map.get((enrollment.id, "MIDTERM")).obtained_marks if marks_map.get((enrollment.id, "MIDTERM")) else "",
            "terminal": marks_map.get((enrollment.id, "TERMINAL")).obtained_marks if marks_map.get((enrollment.id, "TERMINAL")) else "",
        })

    if request.method == "POST" and offering_id:
        errors = []
        for enrollment in enrollments:
            for exam_type, label in EXAM_TYPE_CHOICES:
                key = f"{exam_type.lower()}_{enrollment.id}"
                raw = request.POST.get(key, "").strip()
                if raw == "":
                    continue
                try:
                    value = float(raw)
                except ValueError:
                    errors.append(f"Invalid marks for {enrollment.student.roll_no} ({label}).")
                    continue

                max_allowed = {
                    "SESSIONAL": config.sessional_max,
                    "MIDTERM": config.midterm_max,
                    "TERMINAL": config.terminal_max,
                }[exam_type]

                if value < 0 or value > max_allowed:
                    errors.append(f"{enrollment.student.roll_no} {label} must be 0 - {max_allowed}.")
                    continue

                Marks.objects.update_or_create(
                    enrollment=enrollment,
                    exam_type=exam_type,
                    defaults={
                        "obtained_marks": value,
                        "entered_by": request.user,
                    },
                )

            # calculate final result
            total = 0
            for exam_type, _ in EXAM_TYPE_CHOICES:
                mark = Marks.objects.filter(enrollment=enrollment, exam_type=exam_type).first()
                if mark:
                    total += mark.obtained_marks

            grade, grade_point = _get_grade_for_total(total)
            result, created = Result.objects.get_or_create(
                enrollment=enrollment,
                defaults={
                    "total_marks": total,
                    "grade": grade,
                    "grade_point": grade_point,
                    "result_published": False,
                }
            )
            if not created:
                result.total_marks = total
                result.grade = grade
                result.grade_point = grade_point
                result.save(update_fields=["total_marks", "grade", "grade_point", "calculated_at"])

        if errors:
            for msg in errors:
                messages.error(request, msg)
        else:
            messages.success(request, "Marks saved and results updated.")
        return redirect(f"{request.path}?offering_id={offering_id}")

    context = {
        "offerings": offerings,
        "offering_id": offering_id,
        "enrollments": enrollments,
        "rows": rows,
        "splits": config,
    }
    return render(request, "exams/manage_marks.html", context)
