from django.urls import path
from . import views

urlpatterns = [
    path('product', views.product),
    path('updateProduct', views.updateProduct),
    path('deleteProduct', views.deleteProduct),
    path('productCategories/', views.productCategories),
    path('orderManagement', views.orderManagement),
    path('download/', views.download_excel_data),
    path('status/', views.statusFilter),
    path('dashboard/', views.dashboard),
    path('addCategory/', views.addCategory)

]
