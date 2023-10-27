from django.urls import path
from . import views

urlpatterns = [
    path('attendance/add/', views.AddAttendance.as_view(), name='add-attendance'),
    path('attendance/add/bulk/', views.AddAttendanceBulk.as_view(), name='add-attendance-bulk'),
    path('attendance/get/', views.GetAttendance.as_view(), name='get-attendance'),
    path('attendance/get/status/', views.GetAttendanceYearStatus.as_view(), name='get-attendance-year-status'),
    path('admin/attendance/get/', views.AdminGetAttendance.as_view(), name='get-admin-attendance'),
    path('admin/attendance/get/status/', views.AdminGetAttendanceMonth.as_view(), name='get-admin-attendance-year-status'),
]