from django.urls import path
from . import views

urlpatterns = [
    path('create/link/', views.Class_Updates_Admin.as_view(), name='create_link'),
    path('get/link/', views.Class_Updates_Admin.as_view(), name='get_link'),
    path('update/link/', views.Class_Updates_Admin.as_view(), name='update_link'),
    path('delete/link/', views.Class_Updates_Admin.as_view(), name='delete_link'),
    path('client/get/link/', views.Class_Update_Client_Side.as_view(), name='client_get_link'),
    path('announcement/operation/', views.Announcements.as_view(), name='announcement_operation'),
    path('recordings/operation/', views.RecordingsLink.as_view(), name='recordings_operation'),
    path('recordings/client/get/', views.recording_client_side.as_view(), name='recordings_client_get'),
    path('recordings/client/web/get/', views.recording_client_side_web.as_view(), name='recordings_client_get_web'),    
    path('recordings/dates/client/', views.GetRecordingDates.as_view(), name='recordings_dates_client_get'),
]
