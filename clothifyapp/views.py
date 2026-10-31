from decimal import Decimal, InvalidOperation
import uuid

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404, redirect, render

from .models import Admin, Orders, cartModel, customerModel, productModel


def _customer(request):
    email = request.session.get('cust_emailId')
    if not email:
        return None
    return customerModel.objects.filter(customeremailId=email).first()


def _is_admin(request):
    return bool(request.session.get('admin'))


def home(request):
    products = productModel.objects.all()[:8]
    return render(request, 'index.html', {'products': products})


def shopview(request):
    products = productModel.objects.all()
    return render(request, 'shop.html', {'products': products})


def product_detail(request, productId):
    product = get_object_or_404(productModel, productId=productId)
    return render(request, 'product_detail.html', {'product': product})


def displaycustomer(request):
    if _customer(request):
        return redirect('home')
    return render(request, 'register.html')


def addcustomer(request):
    if request.method != 'POST':
        return redirect('register')

    name = request.POST.get('customername', '').strip()
    phone = request.POST.get('customerphonenumber', '').strip()
    address = request.POST.get('customeraddress', '').strip()
    email = request.POST.get('customeremailId', '').strip().lower()
    password = request.POST.get('customerpassword', '')

    if not name or not email or not password:
        messages.error(request, 'Name, email and password are required.')
        return redirect('register')

    if len(password) < 6:
        messages.error(request, 'Password must contain at least 6 characters.')
        return redirect('register')

    if customerModel.objects.filter(customeremailId=email).exists():
        messages.error(request, 'An account with this email already exists.')
        return redirect('register')

    customerModel.objects.create(
        customername=name,
        customerphonenumber=phone,
        customeraddress=address,
        customeremailId=email,
        customerpassword=make_password(password),
    )

    messages.success(request, 'Account created successfully. Please login.')
    return redirect('login')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    email = request.POST.get('customeremailId', '').strip().lower()
    password = request.POST.get('customerpassword', '')

    customer = customerModel.objects.filter(customeremailId=email).first()
    if customer and check_password(password, customer.customerpassword):
        request.session.flush()
        request.session['cust_emailId'] = customer.customeremailId
        request.session['customer_name'] = customer.customername
        return redirect('home')

    admin = Admin.objects.filter(adminEmailId=email).first()
    if admin:
        valid_admin_password = check_password(password, admin.adminPassword)
        # Support an older plain-text admin record from the original project.
        # If it matches, immediately upgrade it to a hashed password.
        if not valid_admin_password and admin.adminPassword == password:
            admin.adminPassword = make_password(password)
            admin.save(update_fields=['adminPassword'])
            valid_admin_password = True

        if valid_admin_password:
            request.session.flush()
            request.session['admin'] = admin.adminEmailId
            return redirect('dashboard')

    messages.error(request, 'Invalid email or password.')
    return redirect('login')


def logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def addtocart(request, productId):
    customer = _customer(request)
    if not customer:
        messages.error(request, 'Please login before adding products to your cart.')
        return redirect('login')

    product = get_object_or_404(productModel, productId=productId)
    cart_item = cartModel.objects.filter(productid=product, emailId=customer).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = cartModel(productid=product, emailId=customer, quantity=1)

    cart_item.totalPrice = product.productprice * cart_item.quantity
    cart_item.save()

    messages.success(request, f'{product.productname} was added to your cart.')
    return redirect('cart')


def showCart(request):
    customer = _customer(request)
    if not customer:
        messages.error(request, 'Please login to view your cart.')
        return redirect('login')

    cart_items = list(
        cartModel.objects.filter(emailId=customer).select_related('productid')
    )
    cart_total = Decimal('0.00')

    for item in cart_items:
        item.totalPrice = item.productid.productprice * item.quantity
        item.save(update_fields=['totalPrice'])
        cart_total += item.totalPrice

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


def updateprice(request, id):
    customer = _customer(request)
    if not customer:
        return redirect('login')

    cart_item = get_object_or_404(cartModel, id=id, emailId=customer)
    try:
        quantity = int(request.POST.get('quantity', '1'))
    except (TypeError, ValueError):
        quantity = 1

    cart_item.quantity = max(quantity, 1)
    cart_item.totalPrice = cart_item.productid.productprice * cart_item.quantity
    cart_item.save()
    return redirect('cart')


def remove_from_cart(request, id):
    customer = _customer(request)
    if not customer:
        return redirect('login')

    cart_item = get_object_or_404(cartModel, id=id, emailId=customer)
    cart_item.delete()
    messages.success(request, 'Product removed from your cart.')
    return redirect('cart')


def checkout(request):
    customer = _customer(request)
    if not customer:
        messages.error(request, 'Please login before checkout.')
        return redirect('login')

    cart_items = list(
        cartModel.objects.filter(emailId=customer).select_related('productid')
    )
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    cart_total = Decimal('0.00')
    for item in cart_items:
        item.totalPrice = item.productid.productprice * item.quantity
        item.save(update_fields=['totalPrice'])
        cart_total += item.totalPrice

    return render(request, 'checkout.html', {
        'customer': customer,
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


def placeorder(request):
    customer = _customer(request)
    if not customer:
        messages.error(request, 'Please login before placing an order.')
        return redirect('login')
    if request.method != 'POST':
        return redirect('checkout')

    cart_items = list(
        cartModel.objects.filter(emailId=customer).select_related('productid')
    )
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    name = request.POST.get('name', customer.customername).strip()
    address = request.POST.get('address', customer.customeraddress or '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    phoneno = request.POST.get('phoneno', customer.customerphonenumber or '').strip()

    if not all([name, address, city, state, pincode, phoneno]):
        messages.error(request, 'Please complete all delivery details.')
        return redirect('checkout')

    totalbill = sum(
        (item.productid.productprice * item.quantity for item in cart_items),
        Decimal('0.00')
    )
    order_number = f"CLT-{uuid.uuid4().hex[:8].upper()}"

    order = Orders.objects.create(
        customer=customer,
        orderNo=order_number,
        name=name,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        phoneno=phoneno,
        totalbill=totalbill,
    )
    cartModel.objects.filter(emailId=customer).delete()

    return redirect('order_success', orderNo=order.orderNo)


def order_success(request, orderNo):
    customer = _customer(request)
    if not customer:
        return redirect('login')

    order = get_object_or_404(
        Orders,
        orderNo=orderNo,
        customer=customer,
    )
    return render(request, 'order_success.html', {'order': order})


def dashboard(request):
    if not _is_admin(request):
        messages.error(request, 'Please login as an admin.')
        return redirect('login')

    return render(request, 'admin/dashboard.html', {
        'product_count': productModel.objects.count(),
        'customer_count': customerModel.objects.count(),
        'order_count': Orders.objects.count(),
        'recent_orders': Orders.objects.select_related('customer').order_by('-id')[:5],
    })


def productlist_admin(request):
    if not _is_admin(request):
        return redirect('login')
    return render(request, 'admin/products.html', {
        'products': productModel.objects.all().order_by('-productId')
    })


def displayproduct(request):
    if not _is_admin(request):
        return redirect('login')
    return render(request, 'admin/add_product.html')


def addproduct(request):
    if not _is_admin(request):
        return redirect('login')
    if request.method != 'POST':
        return redirect('addproduct')

    name = request.POST.get('productname', '').strip()
    description = request.POST.get('productdescription', '').strip()
    price_text = request.POST.get('productprice', '').strip()
    image = request.FILES.get('product_image')

    if not name or not description or not price_text:
        messages.error(request, 'Please fill in all product details.')
        return redirect('addproduct')

    try:
        price = Decimal(price_text)
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        messages.error(request, 'Please enter a valid product price.')
        return redirect('addproduct')

    productModel.objects.create(
        productname=name,
        productdescription=description,
        productprice=price,
        product_image=image,
    )
    messages.success(request, 'Product added successfully.')
    return redirect('productlist_admin')


def getproductbyid(request, productId):
    if not _is_admin(request):
        return redirect('login')
    product = get_object_or_404(productModel, productId=productId)
    return render(request, 'admin/edit_product.html', {'product': product})


def dataupdateproduct(request):
    if not _is_admin(request):
        return redirect('login')
    if request.method != 'POST':
        return redirect('productlist_admin')

    product = get_object_or_404(productModel, productId=request.POST.get('productId'))
    name = request.POST.get('productname', '').strip()
    description = request.POST.get('productdescription', '').strip()
    price_text = request.POST.get('productprice', '').strip()

    try:
        price = Decimal(price_text)
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        messages.error(request, 'Please enter a valid product price.')
        return redirect('edit_product', productId=product.productId)

    product.productname = name
    product.productdescription = description
    product.productprice = price
    if request.FILES.get('product_image'):
        product.product_image = request.FILES['product_image']
    product.save()

    messages.success(request, 'Product updated successfully.')
    return redirect('productlist_admin')


def deleteproductbyId(request, productId):
    if not _is_admin(request):
        return redirect('login')
    product = get_object_or_404(productModel, productId=productId)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('productlist_admin')


def getcustomer(request):
    if not _is_admin(request):
        return redirect('login')
    return render(request, 'admin/customers.html', {
        'customers': customerModel.objects.all().order_by('customername')
    })


def orderlist(request):
    if not _is_admin(request):
        return redirect('login')
    return render(request, 'admin/orders.html', {
        'orders': Orders.objects.select_related('customer').order_by('-id')
    })


def faqs(request):
    return render(request, 'faqs.html')


def returnpolicy(request):
    return render(request, 'returnpolicy.html')
