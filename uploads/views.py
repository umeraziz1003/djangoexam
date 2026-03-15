from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def upload_file(request):
    return HttpResponse("uploads upload file view")
