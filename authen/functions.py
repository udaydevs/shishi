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
