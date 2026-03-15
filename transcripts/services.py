from django.db.models import Sum

from admission.models import Student
from enrollments.models import Enrollment
from results.models import Result, SemesterResult

from .models import Transcript


def calc_gpa(results):
    total_quality = 0
    total_credits = 0
    for res in results:
        credits = res.enrollment.course_offering.course.credit_hours
        total_quality += res.grade_point * credits
        total_credits += credits
    if total_credits == 0:
        return 0
    return round(total_quality / total_credits, 2)


def update_transcript_for_student(student_or_id):
    if isinstance(student_or_id, Student):
        student = student_or_id
    else:
        student = Student.objects.filter(pk=student_or_id).first()
    if not student:
        return None

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

    semester_groups = {}
    semester_gpas = {}
    for res in results:
        semester = res.enrollment.course_offering.semester
        semester_groups.setdefault(semester, []).append(res)

    for semester, res_list in semester_groups.items():
        gpa = calc_gpa(res_list)
        semester_gpas[semester] = gpa
        SemesterResult.objects.update_or_create(
            student=student,
            semester=semester,
            defaults={"gpa": gpa},
        )

    cgpa = calc_gpa(results)
    Transcript.objects.update_or_create(
        student=student,
        defaults={"cgpa": cgpa},
    )

    total_credits = results.aggregate(
        total=Sum("enrollment__course_offering__course__credit_hours")
    )["total"] or 0

    return {
        "student": student,
        "results": results,
        "semester_groups": semester_groups,
        "semester_gpas": semester_gpas,
        "cgpa": cgpa,
        "total_credits": total_credits,
    }
