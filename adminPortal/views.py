from django.http import JsonResponse, HttpResponse
from .models import productModel, productImageModel, productManagementModel, cartModel, Categories
from authen.models import CustomUser
from .decorators import user_type, allowed_methods
from django.db.models import Sum,Count
import  xlwt, json

maxImage = 3
minImage = 0
contentType = ['image/png','image/jpeg','image/jpg', 'image/webp']

def product(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            category = request.GET.get('category')
            product = []
            if category and Categories.objects.filter(id=category).exists():
                productData = productModel.objects.filter(productCategory=category, isDeleted=False).order_by('-created_at')
            else:
                productData = productModel.objects.filter(isDeleted=False).order_by('-created_at')
            for item in productData:
                productData = {
                    'id':item.id,
                    'productCategory': item.productCategory.category,
                    'productTitle': item.productTitle,
                    'productDescription': item.productDescription,
                    'productPrice': item.productPrice,
                    'productStock': item.productStock,
                    'productImage':[img['productImage'] for img in productImageModel.objects.filter(productId=item.id).values('productImage')],            
                }
                product.append(productData)            
            return JsonResponse(list(product), safe=False, status = 200)
        else:return JsonResponse({'msg' : 'Please Sign In'}, status =400)

    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_staff:
            data = request.POST
            image = request.FILES.getlist('productImage')

            title = data.get('productTitle')
            desc = data.get('productDescription')
            price = data.get('productPrice')
            stock = data.get('productStock')
            category = data.get('productCategory')

            if not title or len(title) > 50:
                return JsonResponse({'msg': 'Invalid title or too long'}, status=400)
            if len(image) == minImage or len(image) > maxImage:
                return JsonResponse({'msg': 'Images are required (max 3)'}, status=400)
            if not request.FILES['productImage'].content_type in contentType:
                return JsonResponse({'msg' : 'Image should have a valid format(jpg, png, jpeg, webp) '},status = 400)
            
            if not price:
                return JsonResponse({'msg': 'Invalid price'}, status=400)
            
            if not category or not Categories.objects.filter(id=category).exists():
                return JsonResponse({'msg': 'Invalid category'}, status=400)
            productInstance = productModel.objects.create(
                user=request.user,
                productTitle=title,
                productDescription=desc,
                productPrice=price,
                productStock=stock,
                productCategory = Categories.objects.get(id = category)
            )
            for img in image:
                productImageModel.objects.create(productImage = img, productId = productInstance)
            return JsonResponse({"msg" : 'Product added successfully'}, status = 201)
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =400)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 

@allowed_methods(['POST'])
@user_type('admin')
def updateProduct(request):
    if not request.body:
        return JsonResponse({"msg" : "Please use the proper json format to send the data"}, status = 400)
    id = request.GET.get('id')
    images = request.FILES.getlist('productImage')

    if not id:
        return JsonResponse({'msg': 'Product ID is required'}, status=400)
    if not productModel.objects.filter(id=id, user=request.user, isDeleted=False).exists():
        return JsonResponse({'msg': 'Product not found'}, status=404)
    product= productModel.objects.get(id=id, user=request.user, isDeleted=False)
    if len(images) > minImage:
        if len(images) > maxImage:
            return JsonResponse({'msg': 'Too many images'}, status=400)
        for img in images:
            if img.content_type not in contentType:
                return JsonResponse({'msg': 'Invalid image format'}, status=400)
    productImageModel.objects.filter(productId=product).update(isDeleted=True)
    for img in images:
        productImageModel.objects.create(productId=product, productImage=img)
    data = request.POST
    if data.get('productTitle'):
        product.productTitle = data.get('productTitle')
    if data.get('productDescription'):
        product.productDescription = data.get('productDescription')
    if data.get('productPrice') and int(data.get('productPrice')) > 1:
        product.productPrice = data.get('productPrice')
    if data.get('productStock'):
        product.productStock = int(data.get('productStock'))
    if data.get('productCategory') and Categories.objects.filter(id=data.get('productCategory')).exists():
        product.productCategory = Categories.objects.get(id=data.get('productCategory'))
    product.save()
    return JsonResponse({"msg" : "Updated Successfully"}, status = 200)

@allowed_methods(['DELETE'])
@user_type('admin')
def deleteProduct(request):
    id = request.GET.get('id')
    if not id:
        return JsonResponse({'msg': 'Product ID is required'}, status=400)
    product = productModel.objects.get(user = request.user, isDeleted = False, id = id)
    product.isDeleted = True
    product.save()
    productImageModel.objects.filter(productId=product).update(isDeleted=True)
    return JsonResponse({"msg":"Deleted Successfully"}, status = 200) 
        
        
@allowed_methods(['GET'])
def productCategories(request):
    categories = Categories.objects.all().values('id', 'category')
    return JsonResponse(list(categories), safe=False, status = 200)


@allowed_methods(['GET'])
@user_type('admin')
def statusFilter(request):
    status = ['Placed', 'Dispatched', 'Shipped', 'Delievered', 'Cancelled']
    return JsonResponse({'status': status}, status = 200)

@user_type('admin')
def orderManagement(request):
    if request.method == 'GET':
            product = []
            status = request.GET.get('status')
            if status:
                productPurchased = productManagementModel.objects.filter(cart__cartStatus=status).order_by('-created_at')
            else:
                productPurchased = productManagementModel.objects.all().order_by('-created_at')
            for item in productPurchased:
                productData = {
                    'user' : item.cart.user.email,
                    'cartId' : item.cart.id,
                    'productStatus': cartModel.Status(item.cart.cartStatus).label,
                    'productTitle':item.cart.productId.productTitle,
                    'productQuantity':item.cart.productQuantity,  
                    'productPrice':item.cart.productId.productPrice,
                    'totalPrice':item.price
                }
                product.append(productData)
            return JsonResponse(list(product), safe=False,status = 200)
        
    elif request.method == 'PATCH':
            status = request.GET.get('status')
            id = request.GET.get('id')
            if status:
                cart = cartModel.objects.filter(id = id)
                if cart.exists():
                    cart.update(cartStatus = status)
                    return JsonResponse({'msg' : "Status Updated Successfully"}, status = 200)
                else:return JsonResponse({'msg' : 'Cart with this id does not exists'}, 400)
            else:return JsonResponse({'msg' : 'Please select a valid status'}, status = 400)
    else:return JsonResponse({"msg":"Invalid Method"} ,status = 405) 


@allowed_methods(['GET'])
@user_type('admin')
def download_excel_data(request):
        if request.user.is_authenticated and request.user.is_staff:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Report.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet("sheet1")

            columns = ['Name','User','Phone No.','Product', 'Quantity', 'Price', 'Created At']
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            for col_num, col_name in enumerate(columns):
                ws.write(0, col_num, col_name, font_style)

            rows = productManagementModel.objects.all()
            row_num = 0
            for row in rows:
                row_num += 1
                user = row.cart.user
                ws.write(row_num, 0, f"{user.first_name} {user.last_name}")
                ws.write(row_num, 1, user.email)
                ws.write(row_num, 2, row.cart.user.phoneNo)
                ws.write(row_num, 3, row.cart.productId.productTitle)
                ws.write(row_num, 4, row.cart.productQuantity)
                ws.write(row_num, 5, row.price)
                ws.write(row_num, 6, row.cart.added_at ,xlwt.easyxf(num_format_str='DD-MMM-YY'))
            wb.save(response)
            return response
        else:return JsonResponse({'msg' : 'Please Login with admin credentials'}, status =400)


@allowed_methods(["GET"])    
@user_type('admin')
def dashboard(request):
    d = productManagementModel.objects.all()
    data = {
        'totalDispatched' : d.filter(cart__cartStatus = 1).aggregate(totalDispatched = Count('id')),
        'totalPlaced' : d.filter(cart__cartStatus = 0).aggregate(totalPlaced = Count('id')),
        'totalDelievered' : d.filter(cart__cartStatus = 3).aggregate(totalDelievered = Count('id')),
        'totalShipped' : d.filter(cart__cartStatus = 2).aggregate(totalShipped = Count('id')),
        'totalUsers': CustomUser.objects.count(),
        'totalOrders': d.count(),
        'totalRevenue' : d.aggregate(totalRevenue = Sum('price')),
    }
    return JsonResponse(data , status = 200)

@allowed_methods(['POST'])
@user_type('admin')
def addCategory(request):
    if not request.body:
        return JsonResponse({"msg" : "Please use the proper json format to send the data"}, status = 400)
    data = json.loads(request.body)
    category = data.get('category')
    if not category:
        return JsonResponse({'msg' : 'Category type is required'}, status = 400)
    category, created = Categories.objects.get_or_create(category = category)
    if not created:
        return JsonResponse({'msg': 'Category already exists'}, status = 400)
    return JsonResponse({'msg': 'Category added successfully'}, status = 200)
