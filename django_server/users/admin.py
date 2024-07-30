from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from import_export.admin import ExportActionModelAdmin
from import_export.forms import ExportForm, ImportForm
from .models import Employee, Manager

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Queryset for mentor and supervisor fields limited to managers only
        self.fields['mentor'].queryset = Manager.objects.filter(role='mentor')
        self.fields['supervisor'].queryset = Manager.objects.filter(role='supervisor')

class EmployeeAdmin(ExportActionModelAdmin):
    form = UserAdminForm
    list_display = ('name', 'telegram_id', 'email', 'language', 'role', 'first_day', 'supervisor_link', 'mentor_link', 'created_at', 'updated_at')
    search_fields = ('name', 'email')
    list_filter = ('role',)
    readonly_fields = ('created_at', 'updated_at')
    export_form = ExportForm
    import_form = ImportForm

    def supervisor_link(self, obj):
        if obj.supervisor:
            url = reverse('admin:users_manager_change', args=[obj.supervisor.pk])
            return format_html('<a href="{}">{}</a>', url, obj.supervisor.name)
        return '-'
    supervisor_link.short_description = 'Supervisor'

    def mentor_link(self, obj):
        if obj.mentor:
            url = reverse('admin:users_manager_change', args=[obj.mentor.pk])
            return format_html('<a href="{}">{}</a>', url, obj.mentor.name)
        return '-'
    mentor_link.short_description = 'Mentor'

class ManagerAdmin(ExportActionModelAdmin):
    list_display = ('name', 'role', 'email', 'language', 'employees_links', 'created_at', 'updated_at')
    search_fields = ('name', 'email')
    list_filter = ('role',)
    readonly_fields = ('created_at', 'updated_at')
    export_form = ExportForm
    import_form = ImportForm

    def employees_links(self, obj):
        employees = Employee.objects.filter(supervisor=obj) | Employee.objects.filter(mentor=obj)
        if employees:
            return format_html('<br>'.join(
                '<a href="{}">{}</a>'.format(reverse('admin:users_employee_change', args=[emp.pk]), emp.name)
                for emp in employees
            ))
        return 'No employees'
    employees_links.short_description = 'Employees'

admin.site.register(Manager, ManagerAdmin)
admin.site.register(Employee, EmployeeAdmin)
