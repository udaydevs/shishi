from django.db import models
from authen.models import CustomUser

class productModel(models.Model):
    class Category(models.IntegerChoices):
        Analgesics = 0,'Analgesics'
        Antibiotics = 1, 'Antibiotics'
        Antifungals = 2, 'Antifungals'
        Antihistamines = 3, 'Antihistamines'
    productTitle = models.CharField(max_length=230)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    productDescription = models.TextField(max_length=600)
    productPrice = models.IntegerField()
    productStock = models.IntegerField()
    isDeleted = models.BooleanField(default=False)
    productCategory =  models.PositiveSmallIntegerField(
        choices=Category.choices,
        default=Category.Analgesics
    )
    
class productImageModel(models.Model):
    productId = models.ForeignKey(productModel, on_delete=models.CASCADE)
    productImage = models.ImageField(upload_to='productImages/')
    isDeleted = models.BooleanField(default=False)


class cartModel(models.Model):
    class Status(models.IntegerChoices):
        Unplaced = 5, 'Unplaced'
        Placed = 0, 'Placed'
        Dispatched = 1,'Dispatched'
        Shipped = 2,'Shipped'
        Delieved = 3, 'Delivered'
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    productId = models.ForeignKey(productModel, on_delete= models.CASCADE)
    productQuantity = models.IntegerField(default=1)
    added_at = models.DateField(auto_now=True)
    isDeleted = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    cartStatus =  models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.Unplaced
    )

class productManagementModel(models.Model):
    cart = models.ForeignKey(cartModel, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)
    price = models.BigIntegerField(default=0)


