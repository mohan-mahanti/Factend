from django.urls import path,include
from company import views

urlpatterns = [
    path("signup", views.signup,name="company-signup"),
    path("login", views.login,name="login"),
    path("company_login", views.company_login,name="company-login"),
    path("register_employee", views.register_employe,name="register_employe"),
    path("logout", views.logout,name="logout"),
    path("send_otp", views.send_otp,name="send_otp"),
    path("swipe_in", views.swipe_in,name="swipe_in"),
    path("swipe_out", views.swipe_out,name="swipe_out"),
    path("add_branch", views.add_branch,name="add_branch"),
    path("leave", views.leave,name="leave"),
]