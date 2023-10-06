from django.urls import path
from . import views 

urlpatterns = [
    path('student/filter/', views.StudentFilterGetMethods.as_view(), name='student-filter'),
]
