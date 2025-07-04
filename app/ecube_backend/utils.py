from functools import wraps
from django.http import JsonResponse


def role_checker(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user_role = getattr(request, "user_role", None)
            print(user_role)
            print(allowed_roles)

            if user_role in allowed_roles:
                return view_func(self, request, *args, **kwargs)

            return JsonResponse({"error": "Unauthorized"}, status=403)

        return _wrapped_view

    return decorator
