"""
URL configuration for ecube_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/admin/', include('register_student.urls')),
    path('client_auth/', include('client_auth.urls')),
    path('student_attendance/', include('student_attendance.urls')),
    path('student_exam_result/', include('student_exam_result.urls')),
    path('student_leaderboard/', include('student_leaderboard.urls')),
    path('student_daily_activities/', include('student_daily_activities.urls')),
    path('student_dashboard/', include('student_dashboard.urls')),
]
