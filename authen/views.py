from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from adminPortal.decorators import user_type, allowed_methods
from .models import  CustomUser, userImageModel
from .functions import check_regex
from .constants import mailRegex, passRegex,phoneNumberRegex 
from django.core.mail import send_mail
from django.conf import settings
import json


def signUp(request):
    if request.method == 'GET':
        gender = ["Male", 'Female', 'Other']
        return JsonResponse({'gender': gender}, status = 200)
    
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({"msg" : "Please Use the proper json format to send the data"}, status = 400)
        data = request.POST
        if (data.get('email')) is None or (check_regex(mailRegex, data.get('email')) is None ):
            return JsonResponse({"msg" : "Email should have a proper format"}, status = 400)
        if (data.get('password')) is None ((check_regex(passRegex, data.get('password')) is None)):
            return JsonResponse({"msg" : "Use valid pattern Password  (Make sure you are giving all the required field)"}, status = 400)
        if (data.get('password') != data.get('confirmPassword')):
            return JsonResponse({ "msg" : "Confirm password should be same as password or confirm password field is missing"}, status = 400)
        if not data.get('gender') in ['0','1','2']:
             return JsonResponse({"msg" : "Gender choice does not match"}, status = 400)
        if  ((check_regex(phoneNumberRegex, data.get('phoneNo')) is None)):
            return JsonResponse({"msg" : "Use valid pattern Password  (Make sure you are giving all the required field)"}, status = 400)
        if len(request.FILES.getlist('ProfilePhoto')) > 1:
            return JsonResponse({'msg' : 'Image should not more than 1'},status = 400)
        if not request.FILES['profilePhoto'].content_type in ['image/png','image/jpeg','image/jpg']:
            return JsonResponse({'msg' : 'Image should have a valid format'},status = 400)
        if (CustomUser.objects.filter(email = data.get('email')).exists()):
            return JsonResponse({"msg" : "User already exists"},status = 409) 
        else:

            user = CustomUser(
                email=data.get('email'),
                phoneNo = data.get('phoneNo'),
                first_name = data.get('firstName'),
                gender = data.get('gender'),   
            )
            user.set_password(data.get('password')) 
            if data.get('lastName'):
                user.last_name = data.get('lastName')    
            user.save()

            for img in request.FILES.getlist('profilePhoto'):
                userImageModel.objects.create(profilePhoto = img, userId = user)
            send_mail('Welcome to Shishi', "Registered Successfully with Shishi", settings.EMAIL_HOST_USER, [data.get('email')])
            return JsonResponse({"msg" : "User Created Successfully"}, status = 201)
    else:
           return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def signIn(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({"msg" : "Please Use the proper json format to send the data"}, status = 400)
        data = json.loads(request.body)
        if ('email' not in (data.keys()) or 'password' not in (data.keys())):
            return JsonResponse({"msg" : "Please give me all the required fields"}, status = 400)
        if request.user.is_authenticated:
            return JsonResponse({"msg":"Already Logged In "}, status = 400) 
        user = authenticate(request, email = data.get('email') , password = data.get('password'))
        if user is not None: 
            login(request,user)   
            return JsonResponse({"msg":"Logged In Successfully","isAdmin" : request.user.is_staff }, status = 200)
        else:return JsonResponse({"msg":"Wrong Credentials"}, status = 401)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 


def signOut(request):
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({"msg":"Logout Successfully"}, status = 200) 
        return JsonResponse({"msg":"No Active User"}, status = 401) 
    else:
           return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def profile(request):
    if request.method == "POST":
        if (request.body):
            if request.user.is_authenticated:
                user = CustomUser.objects.filter(email = request.user)
                if(user.exists() == False):
                    return JsonResponse({'msg' : 'User doesnot exist'}, status = 404)
                data = request.POST
                if not data.get('gender') in ['0','1','2']:
                    return JsonResponse({"msg" : "Gender choice does not match"}, status = 400)
                if  ((check_regex(phoneNumberRegex, data.get('phoneNo')) is None)):
                    return JsonResponse({"msg" : "Use valid pattern Password  (Make sure you are giving all the required field)"}, status = 400)
                if len(request.FILES.getlist('ProfilePhoto')) > 1:
                    return JsonResponse({'msg' : 'Image should not more than 1'},status = 400)
                if not data.get('gender') in ['0','1','2']:
                    return JsonResponse({"msg" : "Gender choice does not match"}, status = 400)
                user = CustomUser.objects.get(email = request.user)
                user.first_name = data.get('first_name')
                if data.get('last_name'):
                    user.last_name = data.get('last_name')
                user.address = data.get('address')
                user.phoneNo = data.get('phoneNo')
                user.gender = data.get('gender')
                user.save()
                image = request.FILES.getlist('profilePhoto')
                if not len(image) == 0:
                    if len(image)> 1:
                        return JsonResponse({'msg' : 'You can only upload one image'}, status = 400)
                    if not image[0].content_type in ['image/png','image/jpeg','image/jpg']:
                        return JsonResponse({'msg' : 'Image should have a valid format'},status = 400)
                    userImage, created = userImageModel.objects.get_or_create(userId = request.user)
                    for img in image:
                        userImage.profilePhoto = img
                        userImage.save()
                return JsonResponse({"msg" : "Updated Successfully"}, status = 200)
            else:return JsonResponse({'msg' : 'Please Log In'}, status = 401)
        else: return JsonResponse({'msg' : "Invalid Json Format"} , status= 400)

    if request.method == 'GET':
        if request.user.is_authenticated:      
            user = CustomUser.objects.filter(email = request.user).values('email', 'phoneNo', 'is_staff','first_name', 'last_name', 'address', 'gender', 'userimagemodel__profilePhoto')
            user = user[0]
            gender_value = user['gender']
            user['gender'] = CustomUser.Gender(gender_value).label
            return JsonResponse(user, status = 200)
        else:return JsonResponse({"msg" : "Please Log In "},status = 401)

    else:return JsonResponse({"msg" : "Invalid Method"}, status= 405)      