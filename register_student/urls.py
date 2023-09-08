from django.urls import path
from . import views

urlpatterns = [
    path('student/individual/', views.StudentMethods.as_view(), name='student-register-individual'),
    path('student/bulk/', views.StudentBulkMethods.as_view(), name='student-register-bulk-file'),
    path('student/get/all/', views.StudentBulkMethods.as_view(), name='student-get-all'),
    path('student/get/ind/', views.StudentMethods.as_view(), name='student-get'),
    path('student/delete/ind/', views.StudentMethods.as_view(), name='student-delete'),
    path('student/update/ind/', views.StudentMethods.as_view(), name='student-update'),
    path('filter/option/class_name/add/', views.classMethods.as_view(), name='filter-class-name'),
    path('filter/option/class_name/get/', views.classMethods.as_view(), name='filter-class-name-get'),
    path('filter/option/class_name/delete/', views.classMethods.as_view(), name='filter-class-name-delete'),
    path('filter/option/division/add/', views.divisionMethods.as_view(), name='filter-division'),
    path('filter/option/division/get/', views.divisionMethods.as_view(), name='filter-division-get'),
    path('filter/option/division/delete/', views.divisionMethods.as_view(), name='filter-division-delete'),
    path('filter/option/subject/add/', views.subjectMethods.as_view(), name='filter-subject'),
    path('filter/option/subject/get/', views.subjectMethods.as_view(), name='filter-subject-get'),
    path('filter/option/subject/delete/', views.subjectMethods.as_view(), name='filter-subject-delete'),
    path('filter/option/batch/add/', views.batchYearMethods.as_view(), name='filter-batch'),
    path('filter/option/batch/get/', views.batchYearMethods.as_view(), name='filter-batch-get'),
    path('filter/option/batch/delete/', views.batchYearMethods.as_view(), name='filter-batch-delete'),
    path('filtered/students/', views.StudentFilterGetMethods.as_view(), name='filtered-students'),
]