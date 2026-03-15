from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from admission.models import Student
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

