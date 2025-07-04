from django.urls import path
from . import views

urlpatterns = [
    path("get_leaderboard/", views.GetLeaderBoard.as_view(), name="get_leaderboard"),
    path(
        "get_leaderboard/exams/",
        views.GetLeaderBoardByExams.as_view(),
        name="get_leaderboard_subject",
    ),
    path("get_exams/", views.GetExams.as_view(), name="get_exams"),
    path("admin/get/exams", views.AdminGetExams.as_view(), name="admin_get_exams"),
    path(
        "admin/get_leaderboard/",
        views.AdminGetLeaderBoard.as_view(),
        name="admin_get_leaderboard",
    ),
    path(
        "admin/recalculate/leaderboard/",
        views.RecalculateLeaderBoardByClass.as_view(),
        name="recalculate_leaderboard",
    ),
]
