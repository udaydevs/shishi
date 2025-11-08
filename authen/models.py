from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator



class CustomUser(AbstractUser):
    class Gender(models.IntegerChoices):
        Male = 0, 'Male'
        Female = 1, 'Female'
        Other =  2 ,'Other'
    username = None
    email = models.EmailField(_("email address"),unique=True)
    address = models.CharField(max_length=150)
    phoneNo = models.BigIntegerField(null=True, blank=False, validators=[MaxValueValidator(10)])
    gender = models.PositiveSmallIntegerField(choices=Gender.choices)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class userImageModel(models.Model):
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profilePhoto = models.ImageField(upload_to='profilePhoto/')
