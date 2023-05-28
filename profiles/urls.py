from django.urls import path,include
from profiles import views

urlpatterns = [
    path("employee_profile/<str:employee_id>", views.employee_profile,name="employee_profile"),
    path("company_profile", views.company_profile,name="company_profile"),
    path("company_profile", views.company_profile,name="company_profile"),
    path("employee_dashboard", views.employee_dashboard,name="employee_dashboard"),
    path("branches/<str:branch_id>", views.branch_profile,name="branch_profile"),
    path("add_holiday/<str:branch_id>", views.add_holiday,name="add_holiday"),
    path("edit_employee/<str:employee_id>", views.edit_employee,name="edit_employee"),
  
]