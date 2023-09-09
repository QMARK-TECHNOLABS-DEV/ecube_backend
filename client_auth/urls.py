from django.urls import path
from . import views

urlpatterns = [
    path('send_otp/', views.SendOTP.as_view(), name='send-otp'),
    path('verify_otp/', views.VerifyOTP.as_view(), name='verify-otp'),
    path('validate/', views.ValidateTokenView.as_view(), name='validate-token'),
    path('refresh/', views.RequestAccessToken.as_view(), name='refresh-token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]