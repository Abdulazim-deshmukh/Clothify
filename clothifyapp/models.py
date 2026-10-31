from django.db import models


class productModel(models.Model):
    productId = models.AutoField(primary_key=True)
    productname = models.CharField(max_length=50)
    productdescription = models.CharField(max_length=200)
    productprice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    product_image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.productname


class customerModel(models.Model):
    customername = models.CharField(max_length=100)
    customerphonenumber = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    customeraddress = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    customeremailId = models.CharField(
        primary_key=True,
        max_length=100
    )
    customerpassword = models.CharField(max_length=128)

    def __str__(self):
        return self.customername


class cartModel(models.Model):
    productid = models.ForeignKey(
        productModel,
        on_delete=models.CASCADE
    )
    emailId = models.ForeignKey(
        customerModel,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=1)
    totalPrice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return f"{self.emailId} - {self.productid}"


class Orders(models.Model):
    customer = models.ForeignKey(
        customerModel,
        on_delete=models.CASCADE
    )
    orderNo = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phoneno = models.CharField(max_length=20)
    totalbill = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return self.orderNo


class Admin(models.Model):
    adminEmailId = models.CharField(
        max_length=100,
        primary_key=True
    )
    adminPassword = models.CharField(max_length=128)

    def __str__(self):
        return self.adminEmailId