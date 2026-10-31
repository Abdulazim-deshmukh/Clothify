from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from clothifyapp import views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Customer storefront
    path('', views.home, name='home'),
    path('shop/', views.shopview, name='shop'),
    path('product/<int:productId>/', views.product_detail, name='product_detail'),

    # Customer account
    path('register/', views.displaycustomer, name='register'),
    path('customer/', views.addcustomer, name='customer'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # Cart
    path('cart/', views.showCart, name='cart'),
    path('cart/add/<int:productId>/', views.addtocart, name='addtocart'),
    path('cart/update/<int:id>/', views.updateprice, name='updateprice'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),

    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/place/', views.placeorder, name='placeorder'),
    path('order/success/<str:orderNo>/', views.order_success, name='order_success'),

    # Admin dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/', views.productlist_admin, name='productlist_admin'),
    path('dashboard/products/add/', views.displayproduct, name='addproduct'),
    path('dashboard/products/create/', views.addproduct, name='product'),
    path('dashboard/products/edit/<int:productId>/', views.getproductbyid, name='edit_product'),
    path('dashboard/products/update/', views.dataupdateproduct, name='dataupdateproduct'),
    path('dashboard/products/delete/<int:productId>/', views.deleteproductbyId, name='delete_product'),
    path('dashboard/customers/', views.getcustomer, name='customerlist'),
    path('dashboard/orders/', views.orderlist, name='orderlist'),

    # Informational pages
    path('faqs/', views.faqs, name='faqs'),
    path('return-policy/', views.returnpolicy, name='return'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
