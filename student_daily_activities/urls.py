from django.urls import path
from . import views

urlpatterns = [
    path('daily-activities/add/bulk/', views.AddDailyUpdatesBulk.as_view(), name='add-daily-activities'),
    path('get/dates/daily-activities/', views.GetDates.as_view(), name='get-dates-daily-activities'),
    path('get/daily-activities/', views.GetDailyUpdate.as_view(), name='get-daily-activities')
]