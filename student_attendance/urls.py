from django.urls import path
from . import views

urlpatterns = [
    path('attendance/add/', views.AddAttendance.as_view(), name='add-attendance'),
    path('attendance/add/bulk/', views.AddAttendanceBulk.as_view(), name='add-attendance-bulk'),
    path('attendance/get/', views.GetAttendance.as_view(), name='get-attendance'),
]