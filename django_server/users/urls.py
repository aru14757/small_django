from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet, EmployeeViewSet, check_user, update_language, get_employees, employee_detail
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'managers', ManagerViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('check_user/', check_user, name='check_user'),
    path('update_language/', update_language, name='update_language'),
    path('get_employees/', get_employees, name='get_employees'),
    path('get_managers/', views.get_managers, name='get_managers'),
    path('employee/<int:pk>/', employee_detail, name='employee_detail'),
    path('api/', include(router.urls)),
    path('docs/', include_docs_urls(title='Users API Documentation'))
]