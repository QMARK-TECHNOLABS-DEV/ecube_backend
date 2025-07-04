from django.urls import path
from . import views

urlpatterns = [
    path(
        "get_student_details/",
        views.StudentGetDashboard.as_view(),
        name="get_student_details",
    ),
]
