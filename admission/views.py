from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from .forms import StudentForm
from .models import Student
# Create your views here.

@login_required(login_url="accounts:login_page")
@never_cache
def students_view(request):
    students = Student.objects.filter(is_active=True)
    return render(request, "admission/students.html", {"students": students})

def create_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
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
    return render(request, "admission/create_student.html", {"form": form})

def edit_student(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect("admission:students")
    else:
        form = StudentForm(instance=student)
    return render(request, "admission/edit_student.html", {"form": form, "student": student})

def delete_student(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == "POST":
        student.is_active = False
        student.save()
        return redirect("admission:students")
    return render(request, "admission/delete_student.html", {"student": student})




