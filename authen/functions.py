import re

from django.http import JsonResponse
from django.contrib.auth.models import User

def check_regex(regex, value):
    x = re.fullmatch(regex, value)
    return x

