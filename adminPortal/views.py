from django.http import JsonResponse, HttpResponse
from .models import productModel, productImageModel, productManagementModel, cartModel
from .constants import productFields
from django.db.models import Sum
import  xlwt


def product(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            message = request.GET.get('category')
            product = []
            if  message in ['0','1','2','3']:
                productData = productModel.objects.filter( productCategory = message, isDeleted = False)
            else:
                productData = productModel.objects.filter(isDeleted = False)
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
        else:return JsonResponse({'msg' : 'Please Login'}, status =400)

    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_staff:
            data = request.POST
            image = request.FILES.getlist('productImage')
            if len(image) == 0:
                return JsonResponse({'msg': 'Please send images of the product'}, status =400)
            if len(image) > 3:
                return JsonResponse({'msg': 'Not more than 3 images are allowed'}, status =400)
            if not request.FILES['productImage'].content_type in ['image/png','image/jpeg','image/jpg']:
                return JsonResponse({'msg' : 'Image should have a valid format'},status = 400)
            if not data.get('productCategory') in ['0','1','2','3']:
                return JsonResponse({'msg': 'Please select a valid category'}, status =400)
            productInstance = productModel.objects.create(
                user = request.user,
                productTitle = data.get('productTitle'),
                productDescription = data.get('productDescription'),
                productPrice = data.get('productPrice'),
                productStock = data.get('productStock'),
                productCategory = data.get('productCategory')
            )
            for img in image:
                productImageModel.objects.create(productImage = img, productId = productInstance)
            return JsonResponse({"msg" : 'Product added successfully'}, status = 201)
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =400)

    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def updateProduct(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({"msg" : "Please Use the proper json format to send the data"}, status = 400)
        if request.user.is_authenticated and request.user.is_staff:
            message = request.GET.get('id')
            images = request.FILES.getlist('productImage')
            print(images)
            print(len(images))
            if message == None:
                return JsonResponse({'msg': 'Please tell which product you want to update'}, status =200)
            data = request.POST
            if len(images) == 0:
                return JsonResponse({'msg': 'Please send images of the product'}, status =400)
            if len(images) > 3:
                return JsonResponse({'msg': 'Not more than 3 images are allowed'}, status =400)
            if not request.FILES['productImage'].content_type in ['image/png','image/jpeg','image/jpg']:
                return JsonResponse({'msg' : 'Image should have a valid format'},status = 400)
            if not data.get('productCategory') in ['0','1','2','3']:
                return JsonResponse({'msg': 'Please select a valid category'}, status =400)
            product = productModel.objects.filter(user = request.user, id = message)
            if(product.exists() == False):
                return JsonResponse({'msg' : 'Product with this id doesnot exist'}, status = 404)
            updateFields = list(data.keys())
            product = productModel.objects.get(id = message, user = request.user)
            product.productTitle = data.get('productTitle')
            product.productDescription = data.get('productDescription')
            product.productPrice = data.get('productPrice')
            product.productCategory = data.get('productCategory')
            product.productStock = data.get('productStock')
            for img in images:
                productImageModel.objects.update_or_create(productId = product, productImage = img)
            product.save(force_update=True, update_fields = updateFields)
            return JsonResponse({"msg" : "Updated Successfully"}, status = 200)
        else:return JsonResponse({"msg":" Please Login with admin credentials"}, status = 401)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def deleteProduct(request):
    if request.method == 'DELETE':
        if  request.user.is_authenticated and request.user.is_staff == True:
            message = request.GET.get('id')
            if message == None:
                return JsonResponse({'msg': 'Please tell which product you want to delete'}, status =200)
            product = productModel.objects.filter(user = request.user, isDeleted = False, id = message)
            if (product.exists()):
                product.isDeleted = True
                return JsonResponse({"msg":"Deleted Successfully"}, status = 200) 
            else:return JsonResponse({'msg' : 'Product does not exist'}, status = 400)
        return JsonResponse({"msg":"No Active User"}, status = 401) 
    else:
           return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def productCategories(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            categories = productModel.Category.labels
            return JsonResponse({'categories': categories}, status = 200)
        else:return JsonResponse({'msg' : 'Please login with admin credentials'}, status = 401)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405)

def statusFilter(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            status = ['Placed', 'Dispatched', 'Shipped', 'Delievered']
            return JsonResponse({'status': status}, status = 200)
        else:return JsonResponse({'msg' : 'Please login with admin credentials'}, status = 401)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405)

def orderManagement(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_staff :
            product = []
            message = request.GET.get('status')
            if  message in ['0','1','2','3']:
                productPurchased = productManagementModel.objects.all().filter(cart__cartStatus = message)
            else:
                productPurchased = productManagementModel.objects.all()
            for item in productPurchased:
                productData = {
                    'user' : item.cart.user.email,
                    'cartId' : item.cart.id,
                    'productStatus': cartModel.Status(item.cart.cartStatus).label,
                    'productTitle':item.cart.productId.productTitle,
                    'productQuantity':item.cart.productQuantity,  
                    'productPrice':item.price
                }
                product.append(productData)
            return JsonResponse(list(product), safe=False,status = 200)
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =401)

    elif request.method == 'PATCH':
        if request.user.is_authenticated and request.user.is_staff :
            message = request.GET.get('status')
            id = request.GET.get('id')
            if message in ['1','2','3','0']:
                cart = cartModel.objects.filter(id = id)
                if cart.exists():
                    cart.update(cartStatus = message)
                    return JsonResponse({'msg' : "Status Updated Successfully"}, status = 200)
                else:return JsonResponse({'msg' : 'Cart with this id does not exists'}, 400)
            else:return JsonResponse({'msg' : 'Please select a valid status'}, status = 400)
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =400)   

    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

def download_excel_data(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("sheet1")

    columns = ['User', 'Created At', 'Price', 'Quantity', 'Name', 'Phone No.', 'Product']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num, col_name in enumerate(columns):
        ws.write(0, col_num, col_name, font_style)

    rows = productManagementModel.objects.select_related('cart__user', 'cart__productId').all()
    row_num = 0
    for row in rows:
        row_num += 1
        user = row.cart.user
        ws.write(row_num, 0, user.email)
        ws.write(row_num, 1, row.cart.added_at.strftime("%d-%b-%Y"))
        ws.write(row_num, 2, row.cart.productId.productPrice)
        ws.write(row_num, 3, row.cart.productQuantity)
        ws.write(row_num, 4, f"{user.first_name} {user.last_name}")
        ws.write(row_num, 5, getattr(user, 'phoneNo', 'N/A'))
        ws.write(row_num, 6, row.cart.productId.productTitle)

    wb.save(response)
    return response

def dashboard(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_staff:
            data = productManagementModel.objects.aggregate(Sum('price'))
            return JsonResponse(data , status = 200)
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =400)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 