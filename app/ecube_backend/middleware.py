from django.http import JsonResponse
from apps.register_student.models import Student
from apps.client_auth.utils import TokenUtil

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION")
        if auth:
            try:
                _, token = auth.split()
                payload = TokenUtil.decode_token(token)

                if payload and payload.get("user_type") == "admin":
                    return self.get_response(request)

                elif payload and payload.get("user_type") == "student":
                    user_id = payload.get("id")
                    if user_id:
                        user = Student.objects.get(id=user_id)
                        if user.restricted:
                            return JsonResponse({"error": "You have been blocked."}, status=403)
                    else:
                        return JsonResponse({"error": "Invalid user id"}, status=400)

            except Exception as e:
                pass 

        return self.get_response(request)
