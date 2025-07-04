from django.http import JsonResponse
from apps.register_student.models import Student
from apps.client_auth.utils import TokenUtil


# Add 2 blank lines before this class
class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION")

        request.user_role = None
        request.user_id = None

        if auth:
            try:
                _, token = auth.split()
                payload = TokenUtil.decode_token(token)

                if not payload:
                    return JsonResponse({"error": "Invalid or expired token."}, status=401)

                user_type = payload.get("user_type")
                user_id = payload.get("id")
                request.user_role = user_type
                request.user_id = user_id

                if user_type == "student":
                    if not user_id:
                        return JsonResponse({"error": "Invalid user id."}, status=400)

                    user = Student.objects.filter(id=user_id).first()
                    if not user:
                        return JsonResponse({"error": "User not found."}, status=404)

                    if user.restricted:
                        return JsonResponse({"error": "You have been blocked."}, status=403)

            except Exception:
                pass  # e removed

        return self.get_response(request)
