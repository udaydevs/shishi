from django.http import JsonResponse
from adminPortal.models import cartModel, productModel, productManagementModel, productImageModel,paymentMethods
from adminPortal.decorators import user_type,allowed_methods


def addToCart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            message = request.GET.get('cart')
            if (message == None):
                return JsonResponse({'msg' : 'Please select a valid product to the cart'}, status = 400) 
            if request.user.is_staff:
                return JsonResponse({'msg' : 'Please login with user credentials'}, status = 400)
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
        else:return JsonResponse({'msg' : 'Please Login'}, status =400)

    elif request.method == 'GET':
            if request.user.is_authenticated:
                if request.user.is_staff:
                    return JsonResponse({'msg' : 'Please login with user credentials'}, status = 401)
                cartData = cartModel.objects.filter(user = request.user, isDeleted =False, purchased = False).values('productId', 'productQuantity')
                return JsonResponse(list(cartData), status = 200,safe=False )
            else:return JsonResponse({'msg':'Please Login '}, status = 401)

    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

@allowed_methods(['DELETE'])
@user_type('user')
def removeFromCart(request):
    id = request.GET.get('id')
    delete = request.GET.get('del')
    if (id == None):
        return JsonResponse({'msg' : 'Please select a valid product to the cart'},status = 400) 
    product = productModel.objects.get(id = id)
    cartInstance = cartModel.objects.get(user = request.user, productId = product, purchased = False)
    if delete:
        product.productStock = product.productStock  + cartInstance.productQuantity
    else:
        cartInstance.productQuantity = cartInstance.productQuantity - 1
        product.productStock = product.productStock - 1
    if cartInstance.productQuantity == 0:
        cartInstance.isDeleted = True
    cartInstance.save()
    product.save()
    return JsonResponse({'msg' : 'Product removed from the cart'}, status = 200)


@allowed_methods(['POST'])
def buyProducts(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.user.is_staff:
                return JsonResponse({'msg' : 'Please login with user credentials'}, status = 400)
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


@allowed_methods(['GET'])
@user_type('user')
def orderHistory(request):
            history = productManagementModel.objects.all().filter( cart__user  = request.user, cart__purchased = True )
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

@allowed_methods(['GET'])
def newArrivals(request):
        product = []
        productData = productModel.objects.filter(isDeleted = False).order_by('-created_at')[:5]
        for item in productData:
            productData = {
                'id':item.id,
                'productCategory':productModel.Category(item.productCategory).label,
                'productTitle': item.productTitle,
                'productDescription': item.productDescription,
                'productPrice': item.productPrice,
                'productStock': item.productStock,
                'productImage':[img['productImage'] for img in productImageModel.objects.filter(productId=item.id).values('productImage')],            
            }
            product.append(productData)        
        return JsonResponse(list(product), safe=False, status = 200)


@allowed_methods(['POST'])
@user_type('user')
def cancelOrder(request):
    cartId = request.GET.get('id')
    order = productManagementModel.objects.filter(cart__user = request.user, cartId = cartId).exclude(cart__cartStatus = 4)
    order.cart.productId.productStock = order.cart.productId.productStock + order.cart.productQuantity
    order.cart.cartStatus = 4
    order.save()
    return JsonResponse({'msg' : 'Order canceled successfully'}, status = 200)

@allowed_methods(['GET'])
@user_type('user')
def paymentMethod(request):
    payment = paymentMethods.objects.values('paymentType', 'id')
    return JsonResponse(list(payment),safe=False,status = 200)
