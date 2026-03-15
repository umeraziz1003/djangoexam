from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from django.db.models import Q
from academics.models import Department, Batch
from accounts.permissions import can
from .forms import StudentForm
from .models import Student
# Create your views here.

@login_required(login_url="accounts:login_page")
@never_cache
def students_view(request):
    department_id = request.GET.get("department_id", "")
    batch_id = request.GET.get("batch_id", "")
    search = request.GET.get("search", "").strip()
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        if not department_id:
            department_id = str(request.user.department_id)

    students = Student.objects.filter(is_active=True).select_related("batch", "batch__department")
    if department_id:
        students = students.filter(batch__department_id=department_id)
    if batch_id:
        students = students.filter(batch_id=batch_id)
    if search:
        students = students.filter(
            Q(full_name__icontains=search) | Q(roll_no__icontains=search)
        )

    departments = Department.objects.filter(is_active=True).order_by("name")
    batches = Batch.objects.all().order_by("start_date")
    if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
        departments = departments.filter(id=request.user.department_id)
        batches = batches.filter(department_id=request.user.department_id)
        students = students.filter(batch__department_id=request.user.department_id)

    return render(request, "admission/students.html", {
        "students": students,
        "departments": departments,
        "batches": batches,
        "department_id": department_id,
        "batch_id": batch_id,
        "search": search,
    })

def create_student(request):
    if request.method == "POST":
        if not can(request.user.role, "STUDENTS", "create"):
            return redirect("admission:students")
        form = StudentForm(request.POST)
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            form.fields["batch"].queryset = Batch.objects.filter(department_id=request.user.department_id)
        if form.is_valid():
            cnic = form.cleaned_data.get("cnic")
            User = get_user_model()
            if User.objects.filter(username=cnic).exists():
                form.add_error("cnic", "A user with this CNIC already exists.")
            else:
                user = User.objects.create_user(
                    username=cnic,
                    password=cnic,
                    role="STUDENT",
                )
                student = form.save(commit=False)
                student.user = user
                if student.batch_id and student.batch.department_id:
                    user.department_id = student.batch.department_id
                    user.save(update_fields=["department"])
                student.save()
                return redirect("admission:students")
    else:
        form = StudentForm()
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            form.fields["batch"].queryset = Batch.objects.filter(department_id=request.user.department_id)
    return render(request, "admission/create_student.html", {"form": form})

def edit_student(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == "POST":
        if not can(request.user.role, "STUDENTS", "update"):
            return redirect("admission:students")
        form = StudentForm(request.POST, instance=student)
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            form.fields["batch"].queryset = Batch.objects.filter(department_id=request.user.department_id)
        if form.is_valid():
            form.save()
            return redirect("admission:students")
    else:
        form = StudentForm(instance=student)
        if request.user.role in ("DEPT_CONTROLLER", "INTERNAL_EXAM_CONTROLLER") and request.user.department_id:
            form.fields["batch"].queryset = Batch.objects.filter(department_id=request.user.department_id)
    return render(request, "admission/edit_student.html", {"form": form, "student": student})

def delete_student(request, pk):
    student = Student.objects.get(pk=pk)
    if not can(request.user.role, "STUDENTS", "delete"):
        return redirect("admission:students")
    if request.method == "POST":
        student.is_active = False
        student.save()
        return redirect("admission:students")
    return render(request, "admission/delete_student.html", {"student": student})




