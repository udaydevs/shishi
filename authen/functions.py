import re

from django.http import JsonResponse
from django.contrib.auth.models import User

def check_regex(regex, value):
    x = re.fullmatch(regex, value)
    return x

def authenticate_user(email, password):
    check = User.objects.filter(email = email)
    if check:
        if User.check_password(password):
            return True

def check_method(request, type:str ):

    if  request.method != type:
        print('heljlj')
        return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def check_data(request):
    if not request.body:
        return JsonResponse({"msg" : "Please Use the proper json format to send the data"}, status = 400)

def check_auth(request):
    if request.user.is_authenticated:
            return JsonResponse({"msg":"Already Logged In "}, status = 409) 
def login_check(request):
    if  request.user.is_authenticated:
        pass
    return JsonResponse({"msg" : "Please Log In"}, status = 401)