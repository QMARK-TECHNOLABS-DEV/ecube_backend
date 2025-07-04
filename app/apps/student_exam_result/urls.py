from django.urls import path
from . import views

urlpatterns = [
    path("exam-result/add/", views.ExamResult.as_view(), name="add-exam-result"),
    path("exam-result/update/", views.ExamResult.as_view(), name="update-exam-result"),
    path("exam-result/delete/", views.ExamResult.as_view(), name="delete-exam-result"),
    path("exam-result/get/", views.ExamResult.as_view(), name="get-exam-result"),
    path("exam-name/filter/", views.GetExamType.as_view(), name="get-exam-type"),
    path(
        "exam-result/add/bulk/",
        views.AddExamResultBulk.as_view(),
        name="add-exam-result-bulk",
    ),
    path(
        "get/client/exam-result/",
        views.ExamResultsView.as_view(),
        name="get-exam-result",
    ),
    path(
        "get/admin/exam-result/",
        views.AdminExamResultsView.as_view(),
        name="get-exam-result-admin",
    ),
]
