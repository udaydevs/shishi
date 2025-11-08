from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.signUp),
    path('login/', views.signIn),
    path('logout/', views.signOut),
    path('profile/', views.profile),
]