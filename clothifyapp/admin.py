from django.contrib import admin
from .models import productModel
from .models import customerModel
from .models import cartModel
from .models import Orders
from .models import Admin

# Register your models here.
admin.site.register(productModel)
admin.site.register(customerModel)
admin.site.register(cartModel)
admin.site.register(Orders)
admin.site.register(Admin)