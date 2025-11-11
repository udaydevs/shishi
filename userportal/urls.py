from django.urls import path
from . import views

urlpatterns = [
    path('addToCart', views.addToCart),
    path('removeFromCart', views.removeFromCart),
    path('buyProducts', views.buyProducts),
    path('orderHistory/', views.orderHistory),
    path('newArrivals/', views.newArrivals),
    path('paymentMethods/', views.paymentMethod)
]
