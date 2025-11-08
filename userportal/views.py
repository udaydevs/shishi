from django.http import JsonResponse
from adminPortal.models import cartModel, productModel, productManagementModel
import json

def addToCart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            message = request.GET.get('cart')
            if (message == None):
                return JsonResponse({'msg' : 'Please select a valid product to the cart'}, status = 400) 
            product = productModel.objects.get(id = message)
            if product.productStock == 0:
                return JsonResponse({'msg' : 'Product is currently unavailable'},status = 400)
            cart, created = cartModel.objects.get_or_create(
                user = request.user,
                productId = product,
                purchased = False
            )
            if not created:
                cart.productQuantity = cart.productQuantity + 1
                cart.save()
            product.productStock = product.productStock  - 1
            product.save()
            return JsonResponse({"msg" : 'Product added successfully'}, status = 201)
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =400)

    elif request.method == 'GET':
            if request.user.is_authenticated:
                cartData = cartModel.objects.filter(user = request.user, isDeleted =False, purchased = False).values('productId', 'productQuantity')
                return JsonResponse(list(cartData), status = 200,safe=False )
            else:return JsonResponse({'msg':'Please Login '}, status = 401)

    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def removeFromCart(request):
    if request.method == 'DELETE':
        if  request.user.is_authenticated :
            message = request.GET.get('id')
            if (message == None):
                return JsonResponse({'msg' : 'Please select a valid product to the cart'},status = 400) 
            product = productModel.objects.get(id = message)
            cartInstance = cartModel.objects.get(user = request.user, productId = product, purchased = False)
            cartInstance.isDeleted = True
            cartInstance.purchased = False
            product.productStock = product.productStock  + 1
            product.save()
            cartInstance.save()
            return JsonResponse({'msg' : 'Product removed from the cart'}, status = 200)
        return JsonResponse({"msg":"No Active User"}, status = 401) 
    
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def buyProducts(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cart = cartModel.objects.filter(user = request.user, purchased = False)
            if not cart.exists():
                return JsonResponse({'msg' : 'Cart is empty'}, status = 400)
            for car in cart:
                productData = productManagementModel.objects.create( cart = car)
                productData.price = car.productId.productPrice * car.productQuantity
                productData.save()
            cart.update(purchased = True, cartStatus = 0)
            return JsonResponse({'msg' : 'Product Ordered successfully'}, status = 200)
        else:return JsonResponse({'msg' : 'Please login with admin credentials'}, status = 401)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def orderHistory(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            history = productManagementModel.objects.all().filter(cart__user  = request.user, cart__purchased = True)
            if history.exists():
                product = []
                for item in history:
                    productData  =  {
                        'productTitle': item.cart.productId.productTitle,
                        'productDescription': item.cart.productId.productDescription,
                        'productQuantity' : item.cart.productQuantity,
                        'productId' : item.cart.productId.id,
                        'productPrice' : item.price,
                        'createdAt':item.created_at,
                        'productStatus': cartModel.Status(item.cart.cartStatus).label
                    }
                    product.append(productData)
                print(product)
                return JsonResponse(list(product),safe=False, status = 200)
            else:return JsonResponse({'msg':'Order history is empty'}, status = 200)
        else:return JsonResponse({'msg' : 'Please login'}, status = 401)
    else:return JsonResponse({'msg': 'Invalid Method'}, status = 400)