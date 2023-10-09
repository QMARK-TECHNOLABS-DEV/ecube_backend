from django.urls import path
from . import views 

urlpatterns = [
    path('student/filter/', views.StudentFilterGetMethods.as_view(), name='student-filter'),
    path('classes/view/', views.AllClassesView.as_view(), name='all-classes'),
    path('filter/batch_years/', views.AllBatchYear.as_view(), name='all-batch-years'),
    path('filter/class_names/', views.AllClassName.as_view(), name='all-class-names'),
    path('filter/divisions/', views.AllDivision.as_view(), name='all-divisions')
]
