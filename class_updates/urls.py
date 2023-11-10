from django.urls import path
from . import views

urlpatterns = [
    path('create/link/', views.Class_Updates_Admin.as_view(), name='create_link'),
    path('get/link/', views.Class_Updates_Admin.as_view(), name='get_link'),
    path('update/link/', views.Class_Updates_Admin.as_view(), name='update_link'),
    path('delete/link/', views.Class_Updates_Admin.as_view(), name='delete_link'),
    path('client/get/link/', views.Class_Update_Client_Side.as_view(), name='client_get_link'),
]
