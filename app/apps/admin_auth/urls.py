from django.urls import path
from . import views

urlpatterns = [
    path("sign_up/", views.SignUpUser.as_view(), name="sign-up"),
    path("login/", views.LoginUser.as_view(), name="login"),
    path("user/update/", views.UpdateUser.as_view(), name="update"),
    path("user/delete/", views.DeleteUser.as_view(), name="delete"),
    path("get/all/", views.GetAllUsers.as_view(), name="get-all"),
    path("get/", views.GetUserById.as_view(), name="get"),
    path("logout/", views.LogoutUser.as_view(), name="logout"),
    path("token/validate/", views.ValidateTokenView.as_view(), name="validate-token"),
    path("token/refresh/", views.RequestAccessToken.as_view(), name="refresh-token"),
    path("forgot/password/", views.ForgotPassword.as_view(), name="forgot-password"),
    path(
        "reset/password/<token>/", views.ResetPassword.as_view(), name="reset-password"
    ),
    path(
        "reset/confirm/submit/",
        views.ResetPasswordSubmit.as_view(),
        name="reset-password-submit",
    ),
]
