from django.urls import path
from . import views

urlpatterns = [
    path('send_otp/', views.SendOTPPhone.as_view(), name='send-otp'),
    path('send_otp_email/', views.SendOTPEmail.as_view(), name='send-otp-email'),
    path('verify_otp/', views.VerifyOTP.as_view(), name='verify-otp'),
    path('verify_otp_email/', views.VerifyOTPEmail.as_view(), name='verify-otp-email'),
    path('validate/', views.ValidateTokenView.as_view(), name='validate-token'),
    path('refresh/', views.RequestAccessToken.as_view(), name='refresh-token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]