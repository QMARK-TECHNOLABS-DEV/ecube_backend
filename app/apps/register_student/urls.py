from django.urls import path
from . import views

urlpatterns = [
    path(
        "student/individual/",
        views.StudentMethods.as_view(),
        name="student-register-individual",
    ),
    path(
        "student/bulk/",
        views.StudentBulkMethods.as_view(),
        name="student-register-bulk-file",
    ),
    path(
        "student/class/get/all/",
        views.StudentBulkMethods.as_view(),
        name="student-get-all",
    ),
    path("student/get/all/", views.GetAllStudents.as_view(), name="student-get-all"),
    path("student/get/ind/", views.StudentMethods.as_view(), name="student-get"),
    path(
        "exam-result/student/display/",
        views.ExamStudentDisplay.as_view(),
        name="exam-student-display",
    ),
    path("student/delete/ind/", views.StudentMethods.as_view(), name="student-delete"),
    path("student/update/ind/", views.StudentMethods.as_view(), name="student-update"),
    path("add/class/details/", views.ClassMethods.as_view(), name="add-class-details"),
    path(
        "update/class/details/",
        views.ClassMethods.as_view(),
        name="update-class-details",
    ),
    path(
        "get/class/details/", views.ClassMethods.as_view(), name="update-class-details"
    ),
    path(
        "delete/class/details/",
        views.ClassMethods.as_view(),
        name="update-class-details",
    ),
    path(
        "update/device/key/", views.DeviceIdMethods.as_view(), name="update-device-key"
    ),
    path("set/restricted/", views.StudentSoftDelete.as_view(), name="set-restricted"),
    path(
        "get/next/admission-no/",
        views.NextAdmNumber.as_view(),
        name="get-next-admission-no",
    ),
    path(
        "class-details/dashboard",
        views.GetClassDetailsDashboard.as_view(),
        name="class-details-dashboard",
    ),
    #  path('student/backup/post/', views.AddStudentDataBackup.as_view(), name='student-backup-post'),
    path(
        "class/methods/tables/create",
        views.ClassCreatTables.as_view(),
        name="class-methods-tables-create",
    ),
]
