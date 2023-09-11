from django.urls import path
from . import views

urlpatterns = [
    path('exam-result/add/', views.AddExamResult.as_view(), name='add-exam-result'),
    path('exam-result/add/bulk/', views.AddExamResultBulk.as_view(), name='add-exam-result-bulk'),
]