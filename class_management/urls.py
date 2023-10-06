from django.urls import path
from . import views 

urlpatterns = [
    path('student/filter/', views.StudentFilterGetMethods.as_view(), name='student-filter'),
    path('classes/view/', views.AllClassesView.as_view(), name='all-classes')
]
