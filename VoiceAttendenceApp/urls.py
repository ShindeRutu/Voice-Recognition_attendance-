from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path("Admin.html", views.Admin, name="Admin"),
	       path("index.html", views.Logout, name="Logout"),
	       path("Register.html", views.Register, name="Register"),
	       path("AdminLogin", views.AdminLogin, name="AdminLogin"),
	       path("Signup", views.Signup, name="Signup"),
	       path("SignupRecord", views.SignupRecord, name="SignupRecord"),
	       path("TrainModel", views.TrainModel, name="TrainModel"),
	       path("ViewAttendence", views.ViewAttendence, name="ViewAttendence"),
	       path("Logout", views.Logout, name="Logout"),
	       path("User", views.User, name="User"),
	       path("successrecording", views.successrecording, name="successrecording"),
	       path("attendence", views.attendence, name="attendence"),
]