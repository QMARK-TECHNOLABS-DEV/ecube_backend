from rest_framework.response import Response
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render
from .utils import TokenUtil
import jwt
from .models import Admin
from .serializers import UserSerializer
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest
from ecube_backend.utils import role_checker


def generate_token(user_id, email):
    # Set the expiration time for the token (e.g., 1 hour from now)
    expiration_time = datetime.now() + timedelta(minutes=5)

    # Create the payload dictionary
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expiration_time,  # Expiration time
    }

    # Replace 'your_secret_key' with your own secret key
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


class GetAllUsers(APIView):
    def get(self, request):
        users = Admin.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"all_users": serializer.data})


# get user by id
class GetUserById(APIView):
    def get(self, request):

        user_id = request.GET.get("id")

        user = Admin.objects.get(id=user_id)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


# create user
class SignUpUser(APIView):
    def post(self, request):
        try:
            data = request.data.copy()

            email_db = Admin.objects.filter(
                email=data["email"], login_type="email"
            ).first()

            if email_db:
                return Response(
                    {"error": "Email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if "password" in data:
                data["password"] = make_password(data["password"])

            domain = data["email"].split("@")[1]

            if data["email"][0:3] != "chn" and domain != "ceconline.edu":
                data["role"] = "guest"
            else:
                data["register_no"] = str(data["email"].split("@")[0]).upper()

            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save()

                access_token, refresh_token = TokenUtil.generate_tokens(user)

                return Response(
                    {"access_token": access_token, "refresh_token": refresh_token},
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return Response(
                f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# update user
class UpdateUser(APIView):
    def update(self, request):

        try:
            user_id = request.GET.get("id")

            user = Admin.objects.get(id=user_id)
            serializer = UserSerializer(instance=user, data=request.data)

            if serializer.is_valid():
                serializer.save()

            return Response(serializer.data)

        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)


# delete user
class DeleteUser(APIView):
    def delete(self, request):

        try:

            user_id = request.GET.get("id")

            user = Admin.objects.get(id=user_id)

            user.delete()

            return Response(
                "User deleted successfully!", status=status.HTTP_204_NO_CONTENT
            )

        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)


class ValidateTokenView(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response(
                {"error": "Access token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            _, token = authorization_header.split()

            payload = TokenUtil.decode_token(token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response(
                    {"error": "Invalid access token."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Implement additional authorization logic here if needed

        except (
            jwt.ExpiredSignatureError,
            jwt.DecodeError,
            ValueError,
            Admin.DoesNotExist,
        ):
            return Response(
                {"error": "Invalid or expired access token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Access token is valid; you can proceed with request processing
        return Response(
            {"message": "Access token is valid."}, status=status.HTTP_200_OK
        )


class LoginUser(APIView):
    def post(self, request):
        try:
            user = Admin.objects.get(email=request.data["email"], login_type="email")

            print(user.id)
            if user is not None:

                print("User exists")
                if check_password(request.data["password"], user.password):
                    print("Password is correct")
                    # Generate refresh and access tokens
                    access_token, refresh_token = TokenUtil.generate_tokens(user)

                    # Validate tokens
                    if TokenUtil.validate_tokens(access_token, refresh_token):
                        user.save()

                        return Response(
                            {
                                "access_token": access_token,
                                "refresh_token": refresh_token,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"error": "Invalid tokens."},
                            status=status.HTTP_401_UNAUTHORIZED,
                        )

                else:
                    return Response(
                        "Password is incorrect!", status=status.HTTP_400_BAD_REQUEST
                    )

        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)


class RequestAccessToken(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response(
                {"error": "Access token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        _, refresh_token = authorization_header.split()

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)

        if not refresh_token_payload:
            return Response(
                {"error": "Invalid refresh token or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = refresh_token_payload.get("id")

        if not user_id:
            return Response(
                {"error": "The refresh token is not associated with a user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate a new access token
        user = Admin.objects.get(id=user_id)

        try:
            access_token = TokenUtil.generate_access_token(user)

            return Response({"access_token": access_token}, status=status.HTTP_200_OK)

        except Exception as e:

            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ForgotPassword(APIView):
    def post(self, request):

        email = request.data.get("email")

        try:
            user = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            user = None

        if user is not None:
            token = generate_token(user.id, email)

            reset_link = (
                f"http://{request.get_host()}/admin_auth/reset/password/{token}/"
            )

            subject = (
                "Password Reset Mail for Admins in Muthookas Ecube Learning System"
            )

            from_email = "qmarktechnolabs@gmail.com"

            receipient = [email]
            html_message = render_to_string(
                "reset_mail.html", {"reset_link": reset_link}
            )

            # Send the email with HTML content
            send_mail(subject, "", from_email, receipient, html_message=html_message)

            return Response(
                {"message": "Password reset mail sent successfully"},
                status=status.HTTP_200_OK,
            )
        else:

            return Response(
                {"message": "No user with that email address found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ResetPassword(APIView):
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            expiration_time = datetime.utcfromtimestamp(payload["exp"])
            current_time = datetime.utcnow()

            if current_time <= expiration_time:
                return render(
                    request,
                    "password_change.html",
                    {"validlink": True, "user_id": payload["user_id"]},
                )
            else:
                return render(request, "password_change.html", {"validlink": False})
        except jwt.ExpiredSignatureError:
            return HttpResponseBadRequest("Password reset link has expired.")
        except jwt.InvalidTokenError:
            return HttpResponseBadRequest("Invalid password reset link.")


class ResetPasswordSubmit(APIView):
    def get(self, request):
        user_id = request.GET["user_id"]
        password = request.GET["password"]
        confirm_password = request.GET["confirm_password"]

        try:

            if password == confirm_password:
                admin_instance = Admin.objects.get(id=user_id)

                admin_instance.password = make_password(password)

                admin_instance.save()

                return render(request, "password_change_success.html")

            else:
                return Response(
                    {"error": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# logout user
class LogoutUser(APIView):
    @role_checker(allowed_roles=["admin"])
    def post(self, request):
        try:

            authorization_header = request.META.get("HTTP_AUTHORIZATION")

            if not authorization_header:
                return Response(
                    {"error": "Access token is missing."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            _, token = authorization_header.split()

            payload = TokenUtil.decode_token(token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response(
                    {"error": "Invalid access token."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = payload.get("id")

            if not user_id:
                return Response(
                    {"error": "The access token is not associated with a user."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            print("User logged out and starting to blacklist token")
            if TokenUtil.is_token_valid(token):

                return Response(
                    {"message": "Logout successful."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Invalid access token or expired access token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
