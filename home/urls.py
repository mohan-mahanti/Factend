from django.urls import path,include
from home import views

urlpatterns = [
    path("", views.home,name="home"),
    path("leave_dashboard", views.leave_dashboard,name="leave_dashboard"),
    path("process_leave", views.process_leave,name="process_leave")
    
]