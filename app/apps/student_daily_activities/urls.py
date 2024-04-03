from django.urls import path
from . import views

urlpatterns = [
    path('daily-activities/add/bulk/', views.AddDailyUpdatesBulk.as_view(), name='add-daily-activities'),
    path('get/dates/daily-activities/', views.GetDates.as_view(), name='get-dates-daily-activities'),
    path('get/daily-activities/', views.GetDailyUpdate.as_view(), name='get-daily-activities'),
    path('admin/get/dates/daily-activities/', views.AdminGetDates.as_view(), name='admin-get-daily-activities'),
    path('admin/get/daily-activities/', views.AdminGetDailyUpdate.as_view(), name='admin-get-daily-activities'),
]