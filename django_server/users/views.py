from rest_framework import viewsets
from .serializer import ManagerSerializer, EmployeeSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from .models import Employee, Manager
from .utils import check_user_view, update_language_view, get_employees_view, get_managers_view

@csrf_exempt
def check_user(request):
    telegram_id = request.GET.get('telegram_id')
    return check_user_view(telegram_id)

@csrf_exempt
def update_language(request):
    if request.method == "POST":
        data = json.loads(request.body)
        return update_language_view(data)
    return JsonResponse({"success": False})

def get_employees(request):
    return get_employees_view()

def get_managers(request):
    return get_managers_view()

def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee_detail.html', {'employee': employee})

class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
