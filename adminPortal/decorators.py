from django.http import JsonResponse
from functools import wraps


def user_type(type):
    def decorator(view):
        @wraps(view)
        def wrapped_view(request):
            if type == 'admin':
                if request.user.is_authenticated and request.user.is_staff:
                    return view(request)
                else: return JsonResponse({'msg' : 'Please login with admin credentials'}, status = 401)
            else:
                if request.user.is_authenticated and (request.user.is_staff == False):
                    return view(request)
                else:return JsonResponse({'msg' : 'Please login'}, status = 401)
        return wrapped_view
    return decorator


def allowed_methods(type):
    def decorators(view):
        @wraps(view)
        def wrapped_view(request):
            if request.method in type:
                return view(request)
            return JsonResponse({'msg' : 'Invalid method'}, status = 405)
        return wrapped_view
    return decorators
