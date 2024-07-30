# utils.py

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Employee, Manager

def check_user_view(telegram_id):
    if telegram_id:
        employee_exists = Employee.objects.filter(telegram_id=telegram_id).exists()
        manager_exists = Manager.objects.filter(telegram_id=telegram_id).exists()
        user_exists = employee_exists or manager_exists
        return JsonResponse({'user_exists': user_exists})
    else:
        return JsonResponse({'error': 'Missing telegram_id parameter'}, status=400)

def update_language_view(data):
    telegram_id = data.get("telegram_id")
    language = data.get("language")
    try:
        user = Employee.objects.get(telegram_id=telegram_id)
        user.language = language
        user.save()
        return JsonResponse({"success": True})
    except Employee.DoesNotExist:
        try:
            user = Manager.objects.get(telegram_id=telegram_id)
            user.language = language
            user.save()
            return JsonResponse({"success": True})
        except Manager.DoesNotExist:
            return JsonResponse({"success": False})

def get_employees_view():
    employees = Employee.objects.all().values('telegram_id', 'name', 'language', 'role', 'first_day')
    return JsonResponse({"get_employees": list(employees)})

def get_managers_view():
    managers = Manager.objects.all()
    managers_data = []

    for manager in managers:
        supervised_employees = manager.supervised_employees.all().values('telegram_id', 'name')
        mentored_employees = manager.mentored_employees.all().values('telegram_id', 'name')
        manager_data = {
            'telegram_id': manager.telegram_id,
            'name': manager.name,
            'language': manager.language,
            'role': manager.role,
            'supervised_employees': list(supervised_employees),
            'mentored_employees': list(mentored_employees)
        }
        managers_data.append(manager_data)

    return JsonResponse({"get_managers": managers_data})

