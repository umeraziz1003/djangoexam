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
from exams.models import GradeScale, Marks, ExamRules
from .models import Result
from transcripts.services import calc_gpa, update_transcript_for_student
from accounts.permissions import can


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


def _require_results_read(request):
    if not can(request.user, "RESULTS", "read"):
        return redirect("accounts:dashboard")
    return None


def _refresh_transcripts_for_enrollments(enrollments):
    student_ids = enrollments.values_list("student_id", flat=True).distinct()
    for student_id in student_ids:
        update_transcript_for_student(student_id)


@login_required(login_url="accounts:login_page")
@never_cache
def results_view(request):
    deny = _require_results_read(request)
    if deny:
        return deny
    if request.user.is_student():
        return redirect("accounts:dashboard")
    search = request.GET.get("search", "").strip()
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    session_id = request.GET.get("session_id", "")
    semester_id = request.GET.get("semester_id", "")
    offering_id = request.GET.get("offering_id", "")
    student_id = request.GET.get("student_id", "")

    if request.user.is_department_scoped() and request.user.department_id:
        if not department_id:
            department_id = str(request.user.department_id)
    qs = Enrollment.objects.select_related(
        "student",
        "course_offering",
        "course_offering__course",
        "course_offering__semester",
        "course_offering__session",
    ).order_by("student__roll_no")
    if request.user.is_department_scoped() and request.user.department_id:
        qs = qs.filter(course_offering__course__department_id=request.user.department_id)

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
            if not can(request.user, "RESULTS", "update"):
                return redirect("results:results")
            for enrollment in qs:
                _recalc_result(enrollment)
            _refresh_transcripts_for_enrollments(qs)
            messages.success(request, "Results recalculated for current filter.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))
        if action == "publish_filtered":
            if not can(request.user, "RESULTS", "update"):
                return redirect("results:results")
            for enrollment in qs:
                result = _recalc_result(enrollment)
                result.result_published = True
                result.save(update_fields=["result_published"])
            _refresh_transcripts_for_enrollments(qs)
            messages.success(request, "Results published for current filter.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))
        if action == "toggle_publish":
            if not can(request.user, "RESULTS", "update"):
                return redirect("results:results")
            enrollment_id = request.POST.get("enrollment_id")
            enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
            result = _recalc_result(enrollment)
            result.result_published = not result.result_published
            result.save(update_fields=["result_published"])
            update_transcript_for_student(enrollment.student_id)
            messages.success(request, "Result publish status updated.")
            return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))
        if action == "recalc_one":
            if not can(request.user, "RESULTS", "update"):
                return redirect("results:results")
            enrollment_id = request.POST.get("enrollment_id")
            enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
            _recalc_result(enrollment)
            update_transcript_for_student(enrollment.student_id)
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

    session_obj = None
    session_batch_ids = []
    session_dept_ids = []
    if session_id:
        session_obj = Session.objects.prefetch_related("batches", "departments").filter(id=session_id).first()
        if session_obj:
            session_batch_ids = list(session_obj.batches.values_list("id", flat=True))
            session_dept_ids = list(session_obj.departments.values_list("id", flat=True))

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
    if session_obj:
        if session_batch_ids:
            context["batches"] = context["batches"].filter(id__in=session_batch_ids)
            context["semesters"] = context["semesters"].filter(batch_id__in=session_batch_ids)
            context["students"] = context["students"].filter(batch_id__in=session_batch_ids)
        context["offerings"] = context["offerings"].filter(session_id=session_id)
        if session_dept_ids:
            context["departments"] = context["departments"].filter(id__in=session_dept_ids)
        elif session_batch_ids:
            context["departments"] = context["departments"].filter(batches__id__in=session_batch_ids).distinct()
    if request.user.is_department_scoped() and request.user.department_id:
        context["departments"] = context["departments"].filter(id=request.user.department_id)
        context["batches"] = context["batches"].filter(department_id=request.user.department_id)
        context["students"] = context["students"].filter(batch__department_id=request.user.department_id)
        context["offerings"] = context["offerings"].filter(course__department_id=request.user.department_id)
    return render(request, "results/results.html", context)


@login_required(login_url="accounts:login_page")
@never_cache
def student_results_view(request, student_id):
    deny = _require_results_read(request)
    if deny:
        return deny
    student = get_object_or_404(Student, pk=student_id)
    if request.user.is_student():
        try:
            if request.user.student_profile.id != student.id:
                return redirect("accounts:dashboard")
        except Student.DoesNotExist:
            return redirect("accounts:dashboard")
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


@login_required(login_url="accounts:login_page")
@never_cache
def my_results_view(request):
    deny = _require_results_read(request)
    if deny:
        return deny
    if not request.user.is_student():
        return redirect("results:results")
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect("accounts:dashboard")
    return student_results_view(request, student.id)


@login_required(login_url="accounts:login_page")
@never_cache
def consolidated_sheet_view(request):
    deny = _require_results_read(request)
    if deny:
        return deny
    if request.user.is_student():
        return redirect("accounts:dashboard")

    search = request.GET.get("search", "").strip()
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    session_id = request.GET.get("session_id", "")
    semester_id = request.GET.get("semester_id", "")

    if request.user.is_department_scoped() and request.user.department_id:
        if not department_id:
            department_id = str(request.user.department_id)

    session_obj = None
    session_batch_ids = []
    session_dept_ids = []
    if session_id:
        session_obj = Session.objects.prefetch_related("batches", "departments").filter(id=session_id).first()
        if session_obj:
            session_batch_ids = list(session_obj.batches.values_list("id", flat=True))
            session_dept_ids = list(session_obj.departments.values_list("id", flat=True))

    students_qs = Student.objects.filter(is_active=True).order_by("roll_no")
    if department_id:
        students_qs = students_qs.filter(batch__department_id=department_id)
    if batch_id:
        students_qs = students_qs.filter(batch_id=batch_id)
    if search:
        students_qs = students_qs.filter(
            Q(roll_no__icontains=search) | Q(full_name__icontains=search)
        )
    if session_batch_ids:
        students_qs = students_qs.filter(batch_id__in=session_batch_ids)

    semesters_qs = Semester.objects.select_related("batch").all()
    if department_id:
        semesters_qs = semesters_qs.filter(batch__department_id=department_id)
    if batch_id:
        semesters_qs = semesters_qs.filter(batch_id=batch_id)
    if session_batch_ids:
        semesters_qs = semesters_qs.filter(batch_id__in=session_batch_ids)
    semesters_qs = semesters_qs.order_by("batch__start_date", "semester_number")
    semesters_data_qs = semesters_qs.filter(id=semester_id) if semester_id else semesters_qs

    departments_qs = Department.objects.filter(is_active=True).order_by("name")
    batches_qs = Batch.objects.all().order_by("start_date")
    if session_obj:
        if session_batch_ids:
            batches_qs = batches_qs.filter(id__in=session_batch_ids)
            semesters_qs = semesters_qs.filter(batch_id__in=session_batch_ids)
        if session_dept_ids:
            departments_qs = departments_qs.filter(id__in=session_dept_ids)
        elif session_batch_ids:
            departments_qs = departments_qs.filter(batches__id__in=session_batch_ids).distinct()

    if request.user.is_department_scoped() and request.user.department_id:
        departments_qs = departments_qs.filter(id=request.user.department_id)
        batches_qs = batches_qs.filter(department_id=request.user.department_id)
        semesters_qs = semesters_qs.filter(batch__department_id=request.user.department_id)

    paginator = Paginator(students_qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    semesters = list(semesters_data_qs)
    semester_ids = [s.id for s in semesters]
    results_qs = Result.objects.select_related(
        "enrollment",
        "enrollment__student",
        "enrollment__course_offering",
        "enrollment__course_offering__course",
        "enrollment__course_offering__semester",
    ).filter(
        enrollment__student__in=page_obj,
        result_published=True,
    )
    if semester_ids:
        results_qs = results_qs.filter(enrollment__course_offering__semester_id__in=semester_ids)
    if session_id:
        results_qs = results_qs.filter(enrollment__course_offering__session_id=session_id)

    rows = []
    offerings = []
    semester_obj = None
    semester_label = ""
    total_cols = None
    if semester_id:
        semester_obj = semesters[0] if semesters else None
        offerings_qs = CourseOffering.objects.select_related(
            "course",
            "semester",
            "session",
        ).filter(semester_id=semester_id)
        if session_id:
            offerings_qs = offerings_qs.filter(session_id=session_id)
        if department_id:
            offerings_qs = offerings_qs.filter(course__department_id=department_id)
        offerings = list(offerings_qs.order_by("course__course_code"))
        total_cols = 9 + (len(offerings) * 3)

        results_by_student_offering = {
            (r.enrollment.student_id, r.enrollment.course_offering_id): r
            for r in results_qs
        }

        def _ordinal(n):
            if 10 <= n % 100 <= 20:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return f"{n}{suffix}"

        if semester_obj:
            semester_label = f"{_ordinal(semester_obj.semester_number)} Semester"

        rules = ExamRules.get_solo()
        for student in page_obj:
            total_quality = 0
            total_credits = 0
            total_marks = 0
            marks_count = 0
            course_rows = []
            for offering in offerings:
                res = results_by_student_offering.get((student.id, offering.id))
                if res:
                    credits = offering.course.credit_hours
                    gp = res.grade_point * credits
                    total_quality += gp
                    total_credits += credits
                    total_marks += res.total_marks
                    marks_count += 1
                    course_rows.append({
                        "marks": res.total_marks,
                        "ng": round(res.grade_point, 2),
                        "gp": round(gp, 2),
                    })
                else:
                    course_rows.append({
                        "marks": "",
                        "ng": "",
                        "gp": "",
                    })

            gpa = round(total_quality / total_credits, 2) if total_credits else ""
            percentage = round(total_marks / marks_count, 2) if marks_count else ""
            status = ""
            if gpa != "":
                if gpa < rules.min_cgpa_dropout:
                    status = "Dropout"
                elif gpa < rules.min_cgpa_probation:
                    status = "Probation"
                else:
                    status = "Promoted"

            rows.append({
                "student": student,
                "course_rows": course_rows,
                "total_quality": round(total_quality, 2) if total_credits else "",
                "total_credits": total_credits if total_credits else "",
                "percentage": percentage,
                "gpa": gpa,
                "status": status,
                "remarks": "",
            })
    else:
        semester_buckets = {}
        student_buckets = {}
        for res in results_qs:
            sid = res.enrollment.student_id
            sem_id = res.enrollment.course_offering.semester_id
            semester_buckets.setdefault((sid, sem_id), []).append(res)
            student_buckets.setdefault(sid, []).append(res)

        for student in page_obj:
            per_semester = {}
            for semester in semesters:
                res_list = semester_buckets.get((student.id, semester.id), [])
                if res_list:
                    per_semester[semester.id] = calc_gpa(res_list)
            all_results = student_buckets.get(student.id, [])
            cgpa = calc_gpa(all_results) if all_results else ""
            rows.append({
                "student": student,
                "gpa_map": per_semester,
                "cgpa": cgpa,
            })

    context = {
        "rows": rows,
        "page_obj": page_obj,
        "semesters": semesters,
        "semester_options": list(semesters_qs),
        "offerings": offerings,
        "semester_obj": semester_obj,
        "semester_label": semester_label,
        "total_cols": total_cols,
        "sessions": Session.objects.order_by("-start_date"),
        "departments": departments_qs,
        "batches": batches_qs,
        "search": search,
        "department_id": department_id,
        "batch_id": batch_id,
        "session_id": session_id,
        "semester_id": semester_id,
    }
    return render(request, "results/consolidated_sheet.html", context)


# Backward-compatible stub (in case old URLconf is still referenced)
def upload_file(request):
    return HttpResponse("results upload file view")
